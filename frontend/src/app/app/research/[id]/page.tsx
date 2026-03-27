import { AgentProgress } from "@/components/research/AgentProgress";
import { ReportViewer } from "@/components/research/ReportViewer";

interface Props {
  params: Promise<{ id: string }>;
}

export default async function ResearchPage({ params }: Props) {
  const { id } = await params;
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <AgentProgress taskId={id} />
      <ReportViewer taskId={id} />
    </div>
  );
}
