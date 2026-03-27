const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

class APIError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "APIError";
  }
}

async function fetcher<T>(
  path: string,
  options: RequestInit & { token?: string } = {},
): Promise<T> {
  const { token, ...init } = options;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new APIError(res.status, body.detail ?? "Unknown error");
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Research ────────────────────────────────────────────────

export interface ResearchTask {
  id: string;
  query: string;
  depth: "quick" | "standard" | "deep";
  status: "pending" | "running" | "completed" | "failed" | "canceled";
  created_at: string;
  completed_at: string | null;
  tokens_used: number;
  cost_usd: number;
  agent_runs: AgentRun[];
}

export interface AgentRun {
  agent_type: string;
  status: string;
  duration_seconds: number | null;
  sources_found: number;
  tokens_used: number;
}

export interface ResearchListResponse {
  items: ResearchTask[];
  total: number;
  page: number;
  page_size: number;
}

export const research = {
  create: (
    token: string,
    payload: { query: string; depth?: string; agents?: string[] },
  ) =>
    fetcher<ResearchTask>("/api/v1/research", {
      method: "POST",
      body: JSON.stringify(payload),
      token,
    }),

  list: (token: string, page = 1, pageSize = 20) =>
    fetcher<ResearchListResponse>(
      `/api/v1/research?page=${page}&page_size=${pageSize}`,
      { token },
    ),

  get: (token: string, taskId: string) =>
    fetcher<ResearchTask>(`/api/v1/research/${taskId}`, { token }),

  cancel: (token: string, taskId: string) =>
    fetcher<void>(`/api/v1/research/${taskId}`, { method: "DELETE", token }),
};

// ── Reports ─────────────────────────────────────────────────

export interface Report {
  id: string;
  task_id: string;
  title: string;
  executive_summary: string;
  body_markdown: string;
  key_findings: KeyFinding[];
  confidence_breakdown: Record<string, number>;
  sources: Source[];
  agent_summary: Record<string, unknown>;
  created_at: string;
}

export interface KeyFinding {
  title: string;
  description: string;
  confidence: number;
  sources: string[];
}

export interface Source {
  title: string;
  url: string;
  reliability: "high" | "medium" | "low";
}

export const reports = {
  getByTask: (token: string, taskId: string) =>
    fetcher<Report>(`/api/v1/reports/research/${taskId}`, { token }),

  share: (
    token: string,
    reportId: string,
    expiresInDays?: number,
  ) =>
    fetcher<{ share_url: string; share_token: string; expires_at: string | null }>(
      `/api/v1/reports/${reportId}/share`,
      {
        method: "POST",
        body: JSON.stringify({ expires_in_days: expiresInDays ?? null }),
        token,
      },
    ),

  export: (token: string, reportId: string, format: "markdown" | "pdf" = "markdown") =>
    fetch(`${API_URL}/api/v1/reports/${reportId}/export?format=${format}`, {
      headers: { Authorization: `Bearer ${token}` },
    }),
};

// ── Auth ─────────────────────────────────────────────────────

export interface UserProfile {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  created_at: string;
}

export const auth = {
  me: (token: string) => fetcher<UserProfile>("/api/v1/me", { token }),
};
