"""Celery tasks for parallel research agent execution."""

import json
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from typing import Any

import redis
import sqlalchemy as sa
import structlog
from celery import Task
from sqlalchemy.engine import Engine

from app.agents.base import AgentInput, AgentOutput
from app.agents.orchestrator import OrchestratorAgent
from app.agents.research import ALL_AGENTS
from app.agents.synthesizer import SynthesisAgent
from app.agents.validator import CrossValidatorAgent
from app.celery_app import celery_app
from app.config import settings

log = structlog.get_logger()

# Claude API pricing (per token, as of 2025)
# Adjust if Anthropic updates pricing
COST_PER_TOKEN = {
    "claude-opus-4-6": {"input": 0.000015, "output": 0.000075},
    "claude-sonnet-4-6": {"input": 0.000003, "output": 0.000015},
}
BLENDED_COST_PER_TOKEN = 0.000012  # weighted average across opus/sonnet usage

# Columns _update_task_status may set besides status/updated_at
_TASK_UPDATE_COLUMNS = {"completed_at", "error_message", "tokens_used", "cost_usd"}

_engine: Engine | None = None


def _get_engine() -> Engine:
    """Lazily create one pooled sync engine per worker process."""
    global _engine
    if _engine is None:
        _engine = sa.create_engine(settings.sync_database_url, pool_pre_ping=True)
    return _engine


def _publish_event(task_id: str, event_type: str, data: dict[str, Any]) -> None:
    """Fire-and-forget Redis pub/sub event."""
    try:
        r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        payload = {
            "event": event_type,
            "task_id": task_id,
            "data": data,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        r.publish(f"research:progress:{task_id}", json.dumps(payload))
        r.close()
    except Exception as exc:
        log.warning("publish_event_failed", error=str(exc))


def _update_task_status(task_id: str, status: str, **kwargs: Any) -> None:
    """Update a research task row."""
    unknown = set(kwargs) - _TASK_UPDATE_COLUMNS
    if unknown:
        raise ValueError(f"Unknown task columns: {sorted(unknown)}")
    assignments = ", ".join(f"{col}=:{col}" for col in kwargs)
    sql = "UPDATE research_tasks SET status=:status, updated_at=now()"
    if assignments:
        sql += f", {assignments}"
    with _get_engine().begin() as conn:
        conn.execute(
            sa.text(sql + " WHERE id=:id"),
            {"status": status, "id": task_id, **kwargs},
        )


def _get_task_status(task_id: str) -> str | None:
    with _get_engine().connect() as conn:
        status: str | None = conn.execute(
            sa.text("SELECT status FROM research_tasks WHERE id=:id"), {"id": task_id}
        ).scalar_one_or_none()
    return status


def _record_agent_run(
    task_id: str, result: dict[str, Any], started_at: datetime
) -> str:
    """Persist a finished agent run. Returns the agent_run id."""
    run_id = str(uuid.uuid4())
    raw_output = {
        "summary": result["summary"],
        "findings": result["findings"],
        "sources": result["sources"],
        "confidence_score": result["confidence_score"],
    }
    with _get_engine().begin() as conn:
        conn.execute(
            sa.text(
                "INSERT INTO agent_runs (id, task_id, agent_type, status, started_at, "
                "completed_at, duration_seconds, tokens_used, sources_found, "
                "error_message, raw_output, created_at, updated_at) "
                "VALUES (:id, :task_id, :agent_type, :status, :started_at, now(), "
                ":duration_seconds, :tokens_used, :sources_found, :error_message, "
                "CAST(:raw_output AS jsonb), now(), now())"
            ),
            {
                "id": run_id,
                "task_id": task_id,
                "agent_type": result["agent_type"],
                "status": result["status"],
                "started_at": started_at,
                "duration_seconds": result["duration_seconds"],
                "tokens_used": result["tokens_used"],
                "sources_found": len(result["sources"]),
                "error_message": result.get("error"),
                "raw_output": json.dumps(raw_output),
            },
        )
    return run_id


@celery_app.task(bind=True, name="app.tasks.research.run_research_task")
def run_research_task(self: Task, task_id: str) -> dict[str, Any]:
    """
    Main orchestration task:
    1. Orchestrator decomposes the query
    2. Research agents run in parallel (ThreadPoolExecutor)
    3. Cross-validator validates findings
    4. Synthesis agent produces the final report
    """
    log.info("research_task_started", task_id=task_id)
    if _get_task_status(task_id) == "canceled":
        log.info("research_task_skipped_canceled", task_id=task_id)
        return {"status": "canceled", "task_id": task_id}
    _update_task_status(task_id, "running")
    _publish_event(task_id, "task.started", {"task_id": task_id})

    try:
        # Fetch task details
        with _get_engine().connect() as conn:
            row = conn.execute(
                sa.text(
                    "SELECT query, depth, agent_config FROM research_tasks WHERE id=:id"
                ),
                {"id": task_id},
            ).fetchone()

        if not row:
            raise ValueError(f"Task {task_id} not found")

        query, depth, agent_config = row.query, row.depth, row.agent_config or {}
        requested_agents = [
            a for a in (agent_config.get("agents") or ALL_AGENTS) if a in ALL_AGENTS
        ]

        # Step 1: Orchestration
        # Planning is advisory: if it fails, run every requested agent.
        plan: dict[str, Any] = {}
        total_tokens = 0
        try:
            orch_output = OrchestratorAgent().run(AgentInput(query=query, depth=depth))
            total_tokens = orch_output.tokens_used
            if orch_output.findings:
                plan = orch_output.findings[0].get("plan", {})
        except Exception as exc:
            log.warning("orchestrator_failed", task_id=task_id, error=str(exc))

        # Filter agents based on plan
        skip_agents = set(plan.get("skip_agents", []))
        agents_to_run = [a for a in requested_agents if a not in skip_agents]
        if not agents_to_run:
            agents_to_run = requested_agents

        _publish_event(
            task_id, "task.started",
            {"agents": agents_to_run, "plan": plan.get("research_plan", "")}
        )

        # Step 2: Parallel research
        agent_outputs: list[dict[str, Any]] = []

        def run_agent(agent_name: str) -> dict[str, Any]:
            agent = ALL_AGENTS[agent_name]()
            _publish_event(task_id, "agent.started", {"agent": agent_name})
            started = datetime.now(UTC)
            result: dict[str, Any]
            try:
                output = agent.run(AgentInput(query=query, depth=depth))
                duration = (datetime.now(UTC) - started).total_seconds()
                result = {
                    "agent_type": agent_name,
                    "status": "completed",
                    "findings": output.findings,
                    "sources": output.sources,
                    "confidence_score": output.confidence_score,
                    "summary": output.summary,
                    "tokens_used": output.tokens_used,
                    "duration_seconds": duration,
                }
            except Exception as exc:
                duration = (datetime.now(UTC) - started).total_seconds()
                log.error("agent_run_failed", agent=agent_name, error=str(exc))
                result = {
                    "agent_type": agent_name,
                    "status": "failed",
                    "findings": [],
                    "sources": [],
                    "confidence_score": 0.0,
                    "summary": "",
                    "tokens_used": 0,
                    "duration_seconds": duration,
                    "error": str(exc),
                }

            try:
                _record_agent_run(task_id, result, started)
            except Exception as exc:
                log.warning("agent_run_persist_failed", agent=agent_name, error=str(exc))

            if result["status"] == "completed":
                _publish_event(
                    task_id,
                    "agent.completed",
                    {
                        "agent": agent_name,
                        "findings": len(result["findings"]),
                        "sources": len(result["sources"]),
                        "duration": duration,
                    },
                )
            else:
                _publish_event(
                    task_id, "agent.failed", {"agent": agent_name, "error": result["error"]}
                )
            return result

        # Run all agents in parallel threads
        with ThreadPoolExecutor(max_workers=len(agents_to_run)) as executor:
            futures = {executor.submit(run_agent, name): name for name in agents_to_run}
            for future in as_completed(futures):
                result = future.result()
                agent_outputs.append(result)
                total_tokens += result.get("tokens_used", 0)

        successful_outputs = [o for o in agent_outputs if o["status"] == "completed"]
        if not successful_outputs:
            raise RuntimeError("All research agents failed")

        # Step 3: Cross-validation
        _publish_event(task_id, "validation.started", {})
        validator = CrossValidatorAgent()
        validation_output = validator.validate(query, successful_outputs)
        total_tokens += validation_output.tokens_used
        _publish_event(
            task_id, "validation.completed",
            {"confidence": validation_output.confidence_score}
        )

        # Step 4: Synthesis
        _publish_event(task_id, "synthesis.started", {})
        synthesizer = SynthesisAgent()
        synthesis_output = synthesizer.synthesize(
            query, successful_outputs, {"findings": validation_output.findings}
        )
        total_tokens += synthesis_output.tokens_used

        # Persist report
        _save_report(task_id, query, synthesis_output)

        # Update task as completed
        cost_usd = total_tokens * BLENDED_COST_PER_TOKEN
        _update_task_status(
            task_id, "completed",
            completed_at=datetime.now(UTC),
            tokens_used=total_tokens,
            cost_usd=cost_usd,
        )

        _publish_event(
            task_id, "task.completed",
            {"tokens_used": total_tokens, "cost_usd": cost_usd}
        )

        log.info("research_task_completed", task_id=task_id, tokens=total_tokens)
        return {"status": "completed", "task_id": task_id, "tokens_used": total_tokens}

    except Exception as exc:
        log.error("research_task_failed", task_id=task_id, error=str(exc))
        _update_task_status(task_id, "failed", error_message=str(exc))
        _publish_event(task_id, "task.failed", {"error": str(exc)})
        raise


def _save_report(task_id: str, query: str, synthesis_output: AgentOutput) -> None:
    """Persist synthesized report to the database."""
    raw = synthesis_output.raw_response
    data: dict[str, Any] = {}
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        pass

    strategic = {
        key: data.get(key, [])
        for key in (
            "strategic_implications",
            "risks_to_watch",
            "recommended_next_steps",
        )
    }
    params = {
        "id": str(uuid.uuid4()),
        "task_id": task_id,
        "title": (data.get("title") or f"Research Report: {query[:60]}")[:512],
        "executive_summary": data.get("executive_summary") or synthesis_output.summary,
        "body_markdown": data.get("body_markdown") or raw,
        "key_findings": json.dumps(data.get("key_findings", synthesis_output.findings)),
        "confidence_breakdown": json.dumps(data.get("confidence_breakdown", {})),
        "sources": json.dumps(data.get("sources") or synthesis_output.sources),
        "agent_summary": json.dumps(strategic),
    }

    with _get_engine().begin() as conn:
        conn.execute(
            sa.text(
                "INSERT INTO reports (id, task_id, title, executive_summary, "
                "body_markdown, key_findings, confidence_breakdown, sources, "
                "agent_summary, created_at, updated_at) "
                "VALUES (:id, :task_id, :title, :executive_summary, :body_markdown, "
                "CAST(:key_findings AS jsonb), CAST(:confidence_breakdown AS jsonb), "
                "CAST(:sources AS jsonb), CAST(:agent_summary AS jsonb), now(), now())"
            ),
            params,
        )
