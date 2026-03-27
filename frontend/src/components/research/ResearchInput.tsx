"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { research } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { useResearchStore } from "@/stores/research";
import { DEPTH_LABELS, DEPTH_DESCRIPTIONS, type ResearchDepth } from "@/types";
import { clsx } from "clsx";

const DEPTHS: ResearchDepth[] = ["quick", "standard", "deep"];

const EXAMPLE_QUERIES = [
  "What is the market size and key players in AI-powered legal tech?",
  "Analyze the competitive landscape for vertical SaaS in healthcare",
  "What are the regulatory risks for crypto exchanges in the EU in 2025?",
];

export function ResearchInput() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [depth, setDepth] = useState<ResearchDepth>("standard");
  const [error, setError] = useState<string | null>(null);
  const { isCreating, setIsCreating, addTask, setActiveTask } = useResearchStore();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim() || query.length < 10) {
      setError("Please enter at least 10 characters.");
      return;
    }

    setIsCreating(true);
    setError(null);

    try {
      const token = await getToken();
      if (!token) {
        router.push("/login");
        return;
      }

      const task = await research.create(token, { query: query.trim(), depth });
      addTask(task);
      setActiveTask(task.id);
      router.push(`/app/research/${task.id}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to start research";
      setError(msg);
      setIsCreating(false);
    }
  }

  return (
    <div className="card space-y-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What would you like to research? e.g. 'Analyze the AI research tools market for enterprise...'"
            rows={3}
            className="w-full resize-none rounded-lg border border-gray-700 bg-gray-800 px-4 py-3
              text-white placeholder-gray-500 focus:border-brand-500 focus:outline-none
              focus:ring-1 focus:ring-brand-500 text-sm"
            maxLength={500}
          />
          <div className="flex justify-between mt-1">
            {error && <p className="text-xs text-red-400">{error}</p>}
            <span className="ml-auto text-xs text-gray-600">{query.length}/500</span>
          </div>
        </div>

        {/* Depth selector */}
        <div>
          <p className="text-xs font-medium text-gray-400 mb-2">Research depth</p>
          <div className="grid grid-cols-3 gap-2">
            {DEPTHS.map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setDepth(d)}
                className={clsx(
                  "rounded-lg border px-3 py-2 text-left transition-colors",
                  depth === d
                    ? "border-brand-500 bg-brand-900/30 text-brand-300"
                    : "border-gray-700 text-gray-400 hover:border-gray-600 hover:text-gray-300",
                )}
              >
                <div className="text-xs font-semibold">{DEPTH_LABELS[d]}</div>
                <div className="text-xs opacity-70 mt-0.5">{DEPTH_DESCRIPTIONS[d]}</div>
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={isCreating || query.length < 10}
          className="btn-primary w-full justify-center gap-2"
        >
          {isCreating ? (
            <>
              <span className="size-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
              Starting research...
            </>
          ) : (
            "Start Research →"
          )}
        </button>
      </form>

      {/* Examples */}
      <div>
        <p className="text-xs text-gray-600 mb-2">Try an example:</p>
        <div className="space-y-1">
          {EXAMPLE_QUERIES.map((q) => (
            <button
              key={q}
              onClick={() => setQuery(q)}
              className="block w-full text-left text-xs text-gray-500 hover:text-brand-400 transition-colors truncate"
            >
              → {q}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
