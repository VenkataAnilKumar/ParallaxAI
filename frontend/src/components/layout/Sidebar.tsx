"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";

const navItems = [
  { href: "/app", label: "New Research", icon: "✦" },
  { href: "/app/history", label: "History", icon: "◷" },
  { href: "/app/settings", label: "Settings", icon: "◈" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex w-56 flex-col border-r border-gray-800 bg-gray-950">
      <div className="flex h-14 items-center px-4 border-b border-gray-800">
        <Link href="/" className="text-lg font-bold text-white">
          <span className="text-brand-500">◎</span> Parallax
        </Link>
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={clsx(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              pathname === item.href
                ? "bg-brand-900/30 text-brand-300"
                : "text-gray-400 hover:bg-gray-800 hover:text-white",
            )}
          >
            <span className="text-base">{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="p-3 border-t border-gray-800">
        <div className="rounded-lg bg-brand-900/20 border border-brand-800 p-3">
          <p className="text-xs font-medium text-brand-300">Free Plan</p>
          <p className="text-xs text-gray-500 mt-0.5">3 tasks/month</p>
          <Link href="/app/settings/billing" className="mt-2 block text-xs text-brand-400 hover:text-brand-300">
            Upgrade →
          </Link>
        </div>
      </div>
    </aside>
  );
}
