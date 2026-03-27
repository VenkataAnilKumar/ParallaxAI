import { ResearchInput } from "@/components/research/ResearchInput";
import { RecentResearch } from "@/components/research/RecentResearch";

export default function AppHomePage() {
  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">New Research</h1>
        <p className="mt-1 text-sm text-gray-400">
          Enter any topic, company, market, or question.
        </p>
      </div>
      <ResearchInput />
      <RecentResearch />
    </div>
  );
}
