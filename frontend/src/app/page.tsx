import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-gray-950">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
        <span className="text-xl font-bold text-white">
          <span className="text-brand-500">◎</span> Parallax
        </span>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm text-gray-400 hover:text-white transition-colors">
            Sign in
          </Link>
          <Link href="/signup" className="btn-primary">
            Get started free
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="mx-auto max-w-4xl px-6 py-24 text-center">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-brand-800 bg-brand-950 px-4 py-1.5 text-sm text-brand-300">
          <span className="size-2 rounded-full bg-brand-500 animate-pulse" />
          7 AI agents running in parallel
        </div>

        <h1 className="text-5xl font-bold tracking-tight text-white sm:text-6xl lg:text-7xl">
          Research at the
          <br />
          <span className="text-brand-400">speed of thought</span>
        </h1>

        <p className="mt-6 text-xl text-gray-400 max-w-2xl mx-auto">
          Parallax deploys 7 specialist AI agents simultaneously to research any market,
          competitor, or trend. Cross-validated findings. Confidence scores. In minutes.
        </p>

        <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/signup" className="btn-primary text-base px-8 py-3">
            Start researching free →
          </Link>
          <Link href="#how-it-works" className="btn-secondary text-base px-8 py-3">
            See how it works
          </Link>
        </div>
      </section>

      {/* Agent Grid */}
      <section id="how-it-works" className="mx-auto max-w-5xl px-6 py-16">
        <h2 className="text-center text-3xl font-bold text-white mb-12">
          7 agents. One query. Parallel execution.
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {[
            { icon: "📊", label: "Market Intelligence", desc: "TAM, trends, growth rates" },
            { icon: "🔍", label: "Competitor Analysis", desc: "Landscape, positioning" },
            { icon: "⚖️", label: "Regulatory", desc: "Compliance risks, policy" },
            { icon: "📰", label: "News & Events", desc: "Recent developments" },
            { icon: "💰", label: "Financial Data", desc: "Funding, valuations" },
            { icon: "💬", label: "Public Sentiment", desc: "Brand perception" },
            { icon: "🎓", label: "Academic Research", desc: "Peer-reviewed findings" },
            { icon: "✅", label: "Cross-Validation", desc: "Fact-checks everything" },
          ].map((agent) => (
            <div key={agent.label} className="card text-center hover:border-brand-700 transition-colors">
              <div className="text-3xl mb-2">{agent.icon}</div>
              <div className="text-sm font-semibold text-white">{agent.label}</div>
              <div className="text-xs text-gray-500 mt-1">{agent.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing teaser */}
      <section className="mx-auto max-w-3xl px-6 py-16 text-center">
        <h2 className="text-3xl font-bold text-white mb-4">Start free. Scale as you grow.</h2>
        <p className="text-gray-400 mb-8">
          Free plan includes 3 research tasks/month. No credit card required.
        </p>
        <Link href="/signup" className="btn-primary text-base px-8 py-3">
          Create free account →
        </Link>
      </section>

      <footer className="border-t border-gray-800 py-8 text-center text-sm text-gray-600">
        © 2025 Parallax. Built with Claude AI.
      </footer>
    </main>
  );
}
