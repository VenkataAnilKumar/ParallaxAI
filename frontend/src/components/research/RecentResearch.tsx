"use client";

import { useEffect } from "react";
import Link from "next/link";
import { research } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { useResearchStore } from "@/stores/research";
import { clsx } from "clsx";

export function RecentResearch() {
  const { tasks, totalTasks, setTasks, isLoadingList, setIsLoadingList } = useResearchStore();

  useEffect(() => {
    async function load() {
      const token = await getToken();
      if (!token) return;
      setIsLoadingList(true);
      try {
        const result = await research.list(token, 1, 5);
        setTasks(result.items, result.total);
      } finally {
        setIsLoadingList(false);
      }
    }
    load();
  }, []);

  if (isLoadingList) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 rounded-xl bg-gray-900 animate-pulse" />
        ))}
      </div>
    );
  }

  if (tasks.length === 0) return null;

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-medium text-gray-400">Recent Research</h2>
        {totalTasks > 5 && (
          <Link href="/app/history" className="text-xs text-brand-400 hover:text-brand-300">
            View all →
          </Link>
        )}
      </div>
      <div className="space-y-2">
        {tasks.map((task) => (
          <Link
            key={task.id}
            href={`/app/research/${task.id}`}
            className="flex items-center justify-between rounded-xl border border-gray-800
              bg-gray-900 px-4 py-3 hover:border-gray-700 transition-colors"
          >
            <div className="min-w-0">
              <p className="text-sm font-medium text-white truncate">{task.query}</p>
              <p className="text-xs text-gray-500 mt-0.5">
                {new Date(task.created_at).toLocaleDateString()} · {task.depth}
              </p>
            </div>
            <StatusDot status={task.status} />
          </Link>
        ))}
      </div>
    </div>
  );
}

function StatusDot({ status }: { status: string }) {
  return (
    <span
      className={clsx(
        "ml-3 flex-shrink-0 size-2 rounded-full",
        status === "completed" && "bg-emerald-500",
        status === "running" && "bg-brand-500 animate-pulse",
        status === "pending" && "bg-gray-500",
        status === "failed" && "bg-red-500",
        status === "canceled" && "bg-gray-600",
      )}
    />
  );
}
