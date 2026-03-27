"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { reports } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { useResearchStore } from "@/stores/research";
import type { Report } from "@/lib/api";

interface Props {
  taskId: string;
}

export function ReportViewer({ taskId }: Props) {
  const { activeReport, setActiveReport } = useResearchStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [shareUrl, setShareUrl] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    let interval: ReturnType<typeof setInterval>;

    async function loadReport() {
      const token = await getToken();
      if (!token) return;

      try {
        const report = await reports.getByTask(token, taskId);
        if (mounted) setActiveReport(report);
      } catch {
        // Report not ready yet — poll
      }
    }

    // Poll every 5s until report appears
    loadReport();
    interval = setInterval(loadReport, 5000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [taskId]);

  async function handleShare() {
    const token = await getToken();
    if (!token || !activeReport) return;

    try {
      const result = await reports.share(token, activeReport.id);
      setShareUrl(result.share_url);
      await navigator.clipboard.writeText(result.share_url);
    } catch (err) {
      setError("Failed to create share link");
    }
  }

  async function handleExport() {
    const token = await getToken();
    if (!token || !activeReport) return;

    const res = await reports.export(token, activeReport.id, "markdown");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `parallax-report-${taskId}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (!activeReport) {
    return (
      <div className="card text-center text-gray-500 py-12">
        {loading ? "Generating report..." : "Report will appear here when research completes."}
      </div>
    );
  }

  const report = activeReport;

  return (
    <div className="space-y-6">
      {/* Report header */}
      <div className="card">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-white">{report.title}</h1>
            <p className="text-xs text-gray-500 mt-1">
              Generated {new Date(report.created_at).toLocaleDateString()}
            </p>
          </div>
          <div className="flex gap-2 flex-shrink-0">
            <button onClick={handleExport} className="btn-secondary text-xs px-3 py-1.5">
              Export .md
            </button>
            <button onClick={handleShare} className="btn-secondary text-xs px-3 py-1.5">
              {shareUrl ? "Copied!" : "Share"}
            </button>
          </div>
        </div>

        {/* Confidence breakdown */}
        {Object.keys(report.confidence_breakdown).length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-800">
            <p className="text-xs font-medium text-gray-400 mb-2">Confidence by Agent</p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(report.confidence_breakdown).map(([agent, score]) => (
                <div key={agent} className="flex items-center gap-1.5">
                  <div className="text-xs text-gray-400 capitalize">{agent}</div>
                  <div className="h-1.5 w-12 rounded-full bg-gray-800">
                    <div
                      className="h-full rounded-full bg-brand-500"
                      style={{ width: `${Math.round((score as number) * 100)}%` }}
                    />
                  </div>
                  <div className="text-xs text-gray-500">
                    {Math.round((score as number) * 100)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Executive summary */}
      <div className="card">
        <h2 className="text-sm font-semibold text-brand-400 uppercase tracking-wider mb-3">
          Executive Summary
        </h2>
        <p className="text-gray-300 leading-relaxed">{report.executive_summary}</p>
      </div>

      {/* Key findings */}
      {report.key_findings.length > 0 && (
        <div className="card">
          <h2 className="text-sm font-semibold text-brand-400 uppercase tracking-wider mb-4">
            Key Findings
          </h2>
          <div className="space-y-3">
            {report.key_findings.map((finding, i) => (
              <div key={i} className="flex gap-3">
                <div className="flex-shrink-0 mt-0.5 size-5 rounded-full bg-brand-900/50 text-brand-400 flex items-center justify-center text-xs font-bold">
                  {i + 1}
                </div>
                <div>
                  <p className="text-sm font-medium text-white">{finding.title}</p>
                  <p className="text-sm text-gray-400 mt-0.5">{finding.description}</p>
                  <div className="mt-1 flex items-center gap-1.5">
                    <div className="text-xs text-gray-600">Confidence</div>
                    <div className="h-1 w-10 rounded-full bg-gray-800">
                      <div
                        className="h-full rounded-full bg-emerald-500"
                        style={{ width: `${Math.round(finding.confidence * 100)}%` }}
                      />
                    </div>
                    <div className="text-xs text-gray-500">{Math.round(finding.confidence * 100)}%</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Full report body */}
      <div className="card prose prose-invert prose-sm max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {report.body_markdown}
        </ReactMarkdown>
      </div>

      {/* Sources */}
      {report.sources.length > 0 && (
        <div className="card">
          <h2 className="text-sm font-semibold text-brand-400 uppercase tracking-wider mb-3">
            Sources
          </h2>
          <div className="space-y-2">
            {report.sources.map((source, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <span className={`badge ${
                  source.reliability === "high" ? "badge-success" :
                  source.reliability === "medium" ? "badge-warning" : "badge-error"
                }`}>
                  {source.reliability}
                </span>
                {source.url ? (
                  <a href={source.url} target="_blank" rel="noopener noreferrer"
                    className="text-brand-400 hover:text-brand-300 truncate">
                    {source.title}
                  </a>
                ) : (
                  <span className="text-gray-400">{source.title}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
