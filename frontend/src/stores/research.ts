import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import type { ResearchTask, Report } from "@/lib/api";
import type { WSEvent } from "@/lib/websocket";

interface AgentStatus {
  agent_type: string;
  status: "pending" | "running" | "completed" | "failed";
  sources_found: number;
  duration_seconds: number | null;
}

interface ResearchState {
  // Task list
  tasks: ResearchTask[];
  totalTasks: number;

  // Active task being monitored
  activeTaskId: string | null;
  agentStatuses: Record<string, AgentStatus>;
  activeReport: Report | null;

  // Loading
  isCreating: boolean;
  isLoadingList: boolean;

  // Actions
  setTasks: (tasks: ResearchTask[], total: number) => void;
  addTask: (task: ResearchTask) => void;
  updateTask: (taskId: string, updates: Partial<ResearchTask>) => void;
  setActiveTask: (taskId: string | null) => void;
  handleWSEvent: (event: WSEvent) => void;
  setActiveReport: (report: Report | null) => void;
  setIsCreating: (v: boolean) => void;
  setIsLoadingList: (v: boolean) => void;
}

export const useResearchStore = create<ResearchState>()(
  immer((set) => ({
    tasks: [],
    totalTasks: 0,
    activeTaskId: null,
    agentStatuses: {},
    activeReport: null,
    isCreating: false,
    isLoadingList: false,

    setTasks: (tasks, total) =>
      set((s) => {
        s.tasks = tasks;
        s.totalTasks = total;
      }),

    addTask: (task) =>
      set((s) => {
        s.tasks.unshift(task);
        s.totalTasks += 1;
      }),

    updateTask: (taskId, updates) =>
      set((s) => {
        const idx = s.tasks.findIndex((t) => t.id === taskId);
        if (idx !== -1) Object.assign(s.tasks[idx], updates);
      }),

    setActiveTask: (taskId) =>
      set((s) => {
        s.activeTaskId = taskId;
        s.agentStatuses = {};
        s.activeReport = null;
      }),

    handleWSEvent: (event) =>
      set((s) => {
        const data = event.data as Record<string, unknown>;
        switch (event.event) {
          case "agent.started":
            s.agentStatuses[data.agent as string] = {
              agent_type: data.agent as string,
              status: "running",
              sources_found: 0,
              duration_seconds: null,
            };
            break;
          case "agent.completed":
            if (s.agentStatuses[data.agent as string]) {
              s.agentStatuses[data.agent as string].status = "completed";
              s.agentStatuses[data.agent as string].duration_seconds =
                (data.duration as number) ?? null;
            }
            break;
          case "agent.failed":
            if (s.agentStatuses[data.agent as string]) {
              s.agentStatuses[data.agent as string].status = "failed";
            }
            break;
          case "task.completed":
            s.updateTask(event.task_id, { status: "completed" });
            break;
          case "task.failed":
            s.updateTask(event.task_id, { status: "failed" });
            break;
        }
      }),

    setActiveReport: (report) =>
      set((s) => {
        s.activeReport = report;
      }),

    setIsCreating: (v) =>
      set((s) => {
        s.isCreating = v;
      }),

    setIsLoadingList: (v) =>
      set((s) => {
        s.isLoadingList = v;
      }),
  })),
);
