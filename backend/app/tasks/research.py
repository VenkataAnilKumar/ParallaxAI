"""Celery tasks for parallel research agent execution."""

import json
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

import structlog

# Claude API pricing (per token, as of 2025)
# Adjust if Anthropic updates pricing
COST_PER_TOKEN = {
    "claude-opus-4-6": {"input": 0.000015, "output": 0.000075},
    "claude-sonnet-4-6": {"input": 0.000003, "output": 0.000015},
}
BLENDED_COST_PER_TOKEN = 0.000012  # weighted average across opus/sonnet usage

from app.agents.base import AgentInput
from app.agents.orchestrator import OrchestratorAgent
from app.agents.research import ALL_AGENTS
from app.agents.synthesizer import SynthesisAgent
from app.agents.validator import CrossValidatorAgent
from app.celery_app import celery_app
from app.config import settings

log = structlog.get_logger()


def _publish_event(task_id: str, event_type: str, data: dict) -> None:
    """Fire-and-forget Redis pub/sub event."""
    try:
        import redis

        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        payload = {
            "event": event_type,
            "task_id": task_id,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        r.publish(f"research:progress:{task_id}", json.dumps(payload))
        r.close()
    except Exception as exc:
        log.warning("publish_event_failed", error=str(exc))


def _update_task_status(task_id: str, status: str, **kwargs) -> None:
    """Update task in DB using a fresh sync connection."""
    import sqlalchemy as sa
    from sqlalchemy import create_engine

    engine = create_engine(settings.DATABASE_URL)
    try:
        with engine.begin() as conn:
            updates = {"status": status, "updated_at": datetime.now(timezone.utc), **kwargs}
            conn.execute(
                sa.text(
                    "UPDATE research_tasks SET status=:status, updated_at=:updated_at "
                    + (", completed_at=:completed_at" if "completed_at" in kwargs else "")
                    + (", error_message=:error_message" if "error_message" in kwargs else "")
                    + (", tokens_used=:tokens_used" if "tokens_used" in kwargs else "")
                    + (", cost_usd=:cost_usd" if "cost_usd" in kwargs else "")
                    + " WHERE id=:id"
                ),
                {**updates, "id": task_id},
            )
    finally:
        engine.dispose()


def _upsert_agent_run(task_id: str, agent_type: str, status: str, **kwargs) -> str:
    """Insert or update an agent run record. Returns agent_run_id."""
    import sqlalchemy as sa
    from sqlalchemy import create_engine

    run_id = str(uuid.uuid4())
    engine = create_engine(settings.DATABASE_URL)
    try:
        with engine.begin() as conn:
            conn.execute(
                sa.text(
                    "INSERT INTO agent_runs (id, task_id, agent_type, status, created_at, updated_at) "
                    "VALUES (:id, :task_id, :agent_type, :status, now(), now()) "
                    "ON CONFLICT DO NOTHING"
                ),
                {"id": run_id, "task_id": task_id, "agent_type": agent_type, "status": status},
            )
    finally:
        engine.dispose()
    return run_id


@celery_app.task(bind=True, name="app.tasks.research.run_research_task")
def run_research_task(self, task_id: str) -> dict:
    """
    Main orchestration task:
    1. Orchestrator decomposes the query
    2. Research agents run in parallel (ThreadPoolExecutor)
    3. Cross-validator validates findings
    4. Synthesis agent produces the final report
    """
    log.info("research_task_started", task_id=task_id)
    _update_task_status(task_id, "running")
    _publish_event(task_id, "task.started", {"task_id": task_id})

    try:
        # Fetch task details
        import sqlalchemy as sa
        from sqlalchemy import create_engine

        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            row = conn.execute(
                sa.text("SELECT query, depth, agent_config FROM research_tasks WHERE id=:id"),
                {"id": task_id},
            ).fetchone()
        engine.dispose()

        if not row:
            raise ValueError(f"Task {task_id} not found")

        query, depth, agent_config = row.query, row.depth, row.agent_config or {}
        requested_agents = agent_config.get("agents") or list(ALL_AGENTS.keys())

        # Step 1: Orchestration
        orchestrator = OrchestratorAgent()
        orch_output = orchestrator.run(AgentInput(query=query, depth=depth))
        plan = orch_output.findings[0].get("plan", {}) if orch_output.findings else {}

        # Filter agents based on plan
        skip_agents = set(plan.get("skip_agents", []))
        agents_to_run = [a for a in requested_agents if a not in skip_agents]

        _publish_event(
            task_id, "task.started",
            {"agents": agents_to_run, "plan": plan.get("research_plan", "")}
        )

        # Step 2: Parallel research
        agent_outputs = []
        total_tokens = orch_output.tokens_used

        def run_agent(agent_name: str) -> dict:
            AgentClass = ALL_AGENTS[agent_name]
            agent = AgentClass()
            _publish_event(task_id, "agent.started", {"agent": agent_name})
            started = datetime.now(timezone.utc)
            try:
                output = agent.run(AgentInput(query=query, depth=depth))
                duration = (datetime.now(timezone.utc) - started).total_seconds()
                _publish_event(
                    task_id, "agent.completed",
                    {"agent": agent_name, "findings": len(output.findings), "duration": duration}
                )
                return {
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
                duration = (datetime.now(timezone.utc) - started).total_seconds()
                _publish_event(task_id, "agent.failed", {"agent": agent_name, "error": str(exc)})
                log.error("agent_run_failed", agent=agent_name, error=str(exc))
                return {
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

        # Run all agents in parallel threads
        with ThreadPoolExecutor(max_workers=min(len(agents_to_run), 7)) as executor:
            futures = {executor.submit(run_agent, name): name for name in agents_to_run}
            for future in as_completed(futures):
                result = future.result()
                agent_outputs.append(result)
                total_tokens += result.get("tokens_used", 0)

        successful_outputs = [o for o in agent_outputs if o["status"] == "completed"]

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
            completed_at=datetime.now(timezone.utc),
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


def _save_report(task_id: str, query: str, synthesis_output) -> None:
    """Persist synthesized report to the database."""
    import json as _json

    import sqlalchemy as sa
    from sqlalchemy import create_engine

    raw = synthesis_output.raw_response
    data: dict = {}
    try:
        data = _json.loads(raw)
    except Exception:
        pass

    report_id = str(uuid.uuid4())
    title = data.get("title", f"Research Report: {query[:60]}")
    executive_summary = data.get("executive_summary", synthesis_output.summary)
    body_markdown = data.get("body_markdown", raw)
    key_findings = _json.dumps(data.get("key_findings", synthesis_output.findings))
    confidence_breakdown = _json.dumps(data.get("confidence_breakdown", {}))
    sources = _json.dumps(data.get("sources", []))
    agent_summary = _json.dumps(
        {"strategic_implications": data.get("strategic_implications", [])}
    )

    engine = create_engine(settings.DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(
            sa.text(
                "INSERT INTO reports (id, task_id, title, executive_summary, body_markdown, "
                "key_findings, confidence_breakdown, sources, agent_summary, created_at, updated_at) "
                "VALUES (:id, :task_id, :title, :executive_summary, :body_markdown, "
                ":key_findings::jsonb, :confidence_breakdown::jsonb, :sources::jsonb, "
                ":agent_summary::jsonb, now(), now())"
            ),
            {
                "id": report_id,
                "task_id": task_id,
                "title": title,
                "executive_summary": executive_summary,
                "body_markdown": body_markdown,
                "key_findings": key_findings,
                "confidence_breakdown": confidence_breakdown,
                "sources": sources,
                "agent_summary": agent_summary,
            },
        )
    engine.dispose()
