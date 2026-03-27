import { ResearchHistory } from "@/components/research/ResearchHistory";

export default function HistoryPage() {
  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Research History</h1>
        <p className="mt-1 text-sm text-gray-400">All your past research tasks.</p>
      </div>
      <ResearchHistory />
    </div>
  );
}
