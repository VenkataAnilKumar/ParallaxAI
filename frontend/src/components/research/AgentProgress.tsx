"use client";

import { useEffect, useRef, useState } from "react";
import { ResearchSocket } from "@/lib/websocket";
import { research } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { useResearchStore } from "@/stores/research";
import { AGENT_LABELS, AGENT_ICONS } from "@/types";
import { clsx } from "clsx";

interface Props {
  taskId: string;
}

export function AgentProgress({ taskId }: Props) {
  const { agentStatuses, handleWSEvent, updateTask } = useResearchStore();
  const socketRef = useRef<ResearchSocket | null>(null);
  const [taskStatus, setTaskStatus] = useState<string>("pending");
  const [query, setQuery] = useState<string>("");

  useEffect(() => {
    let mounted = true;

    async function init() {
      const token = await getToken();
      if (!token || !mounted) return;

      // Load task details
      const task = await research.get(token, taskId).catch(() => null);
      if (task && mounted) {
        setQuery(task.query);
        setTaskStatus(task.status);
      }

      // Connect WebSocket for live updates
      const socket = new ResearchSocket(taskId);
      socketRef.current = socket;

      socket.on("task.started", (ev) => { if (mounted) setTaskStatus("running"); });
      socket.on("task.completed", (ev) => {
        if (mounted) {
          setTaskStatus("completed");
          updateTask(taskId, { status: "completed" });
        }
      });
      socket.on("task.failed", (ev) => {
        if (mounted) setTaskStatus("failed");
      });

      // Forward all events to store
      const allEvents = [
        "agent.started", "agent.completed", "agent.failed",
        "validation.started", "validation.completed", "synthesis.started",
      ] as const;
      allEvents.forEach((evType) => socket.on(evType, handleWSEvent));

      socket.connect();
    }

    init();
    return () => {
      mounted = false;
      socketRef.current?.disconnect();
    };
  }, [taskId]);

  const agentList = Object.values(agentStatuses);
  const isRunning = taskStatus === "running" || taskStatus === "pending";

  if (taskStatus === "completed" && agentList.length === 0) {
    return null; // Report viewer takes over
  }

  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-semibold text-white">
            {isRunning ? "Researching..." : taskStatus === "completed" ? "Research Complete" : "Research Failed"}
          </h2>
          {query && (
            <p className="text-sm text-gray-400 mt-0.5 line-clamp-1">{query}</p>
          )}
        </div>
        <StatusBadge status={taskStatus} />
      </div>

      {agentList.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {agentList.map((agent) => (
            <div
              key={agent.agent_type}
              className={clsx(
                "flex items-center gap-2 rounded-lg border px-3 py-2 text-sm transition-colors",
                agent.status === "completed" && "border-emerald-800 bg-emerald-900/20",
                agent.status === "running" && "border-brand-700 bg-brand-900/20",
                agent.status === "failed" && "border-red-800 bg-red-900/20",
                agent.status === "pending" && "border-gray-700 bg-gray-800/50",
              )}
            >
              <span>{AGENT_ICONS[agent.agent_type] ?? "🤖"}</span>
              <div className="min-w-0">
                <div className="text-xs font-medium text-white truncate">
                  {AGENT_LABELS[agent.agent_type] ?? agent.agent_type}
                </div>
                <div className="text-xs text-gray-500 capitalize">{agent.status}</div>
              </div>
              {agent.status === "running" && (
                <span className="ml-auto size-3 rounded-full border border-brand-400 border-t-transparent animate-spin flex-shrink-0" />
              )}
              {agent.status === "completed" && (
                <span className="ml-auto text-emerald-400 flex-shrink-0">✓</span>
              )}
            </div>
          ))}
        </div>
      )}

      {isRunning && agentList.length === 0 && (
        <div className="flex items-center gap-3 text-sm text-gray-400">
          <span className="size-4 rounded-full border-2 border-brand-400 border-t-transparent animate-spin" />
          Initializing research agents...
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    pending: "badge-info",
    running: "badge-info",
    completed: "badge-success",
    failed: "badge-error",
    canceled: "badge-warning",
  };
  return (
    <span className={map[status] ?? "badge"}>
      {status}
    </span>
  );
}
