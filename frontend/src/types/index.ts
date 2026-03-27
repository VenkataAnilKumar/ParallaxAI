export type { ResearchTask, AgentRun, Report, KeyFinding, Source, UserProfile } from "@/lib/api";
export type { WSEvent, WSEventType } from "@/lib/websocket";

export type ResearchDepth = "quick" | "standard" | "deep";
export type TaskStatus = "pending" | "running" | "completed" | "failed" | "canceled";

export const DEPTH_LABELS: Record<ResearchDepth, string> = {
  quick: "Quick (2-3 min)",
  standard: "Standard (5-7 min)",
  deep: "Deep (10-15 min)",
};

export const DEPTH_DESCRIPTIONS: Record<ResearchDepth, string> = {
  quick: "Key findings, top sources. Best for quick validation.",
  standard: "Comprehensive analysis with cross-validation.",
  deep: "Exhaustive research. Every angle covered.",
};

export const AGENT_LABELS: Record<string, string> = {
  market: "Market Intelligence",
  competitor: "Competitor Analysis",
  regulatory: "Regulatory & Legal",
  news: "News & Events",
  financial: "Financial Data",
  sentiment: "Public Sentiment",
  academic: "Academic Research",
  cross_validator: "Cross-Validation",
  synthesis: "Report Synthesis",
};

export const AGENT_ICONS: Record<string, string> = {
  market: "📊",
  competitor: "🔍",
  regulatory: "⚖️",
  news: "📰",
  financial: "💰",
  sentiment: "💬",
  academic: "🎓",
  cross_validator: "✅",
  synthesis: "📝",
};
