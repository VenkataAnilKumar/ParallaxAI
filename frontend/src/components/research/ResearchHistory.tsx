"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { research } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { clsx } from "clsx";

export function ResearchHistory() {
  const [tasks, setTasks] = useState<Awaited<ReturnType<typeof research.list>>["items"]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const PAGE_SIZE = 20;

  useEffect(() => {
    async function load() {
      const token = await getToken();
      if (!token) return;
      setLoading(true);
      try {
        const result = await research.list(token, page, PAGE_SIZE);
        setTasks(result.items);
        setTotal(result.total);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [page]);

  if (loading) {
    return (
      <div className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-16 rounded-xl bg-gray-900 animate-pulse" />
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="card text-center py-16 text-gray-500">
        <p className="text-4xl mb-3">🔍</p>
        <p>No research tasks yet.</p>
        <Link href="/app" className="mt-3 inline-block text-brand-400 hover:text-brand-300 text-sm">
          Start your first research →
        </Link>
      </div>
    );
  }

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="space-y-2">
      {tasks.map((task) => (
        <Link
          key={task.id}
          href={`/app/research/${task.id}`}
          className="flex items-center justify-between rounded-xl border border-gray-800
            bg-gray-900 px-4 py-3 hover:border-gray-700 transition-colors"
        >
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-white truncate">{task.query}</p>
            <div className="flex items-center gap-3 mt-0.5">
              <span className="text-xs text-gray-500">
                {new Date(task.created_at).toLocaleString()}
              </span>
              <span className="text-xs text-gray-600">·</span>
              <span className="text-xs text-gray-500 capitalize">{task.depth}</span>
              {task.cost_usd > 0 && (
                <>
                  <span className="text-xs text-gray-600">·</span>
                  <span className="text-xs text-gray-500">${task.cost_usd.toFixed(3)}</span>
                </>
              )}
            </div>
          </div>
          <div className="ml-4 flex-shrink-0">
            <span className={clsx(
              "badge",
              task.status === "completed" && "badge-success",
              task.status === "running" && "badge-info",
              task.status === "failed" && "badge-error",
              task.status === "pending" && "badge-info",
              task.status === "canceled" && "bg-gray-800 text-gray-400",
            )}>
              {task.status}
            </span>
          </div>
        </Link>
      ))}

      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-4">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn-secondary text-sm disabled:opacity-40"
          >
            ← Previous
          </button>
          <span className="text-sm text-gray-500">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="btn-secondary text-sm disabled:opacity-40"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
