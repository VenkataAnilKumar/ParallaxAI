"use client";

import { supabase } from "@/lib/supabase";
import { useRouter } from "next/navigation";

export function Header() {
  const router = useRouter();

  async function handleSignOut() {
    await supabase.auth.signOut();
    router.push("/login");
  }

  return (
    <header className="flex h-14 items-center justify-between border-b border-gray-800 px-6">
      <div className="md:hidden text-lg font-bold text-white">
        <span className="text-brand-500">◎</span> Parallax
      </div>
      <div className="flex-1" />
      <button
        onClick={handleSignOut}
        className="text-sm text-gray-400 hover:text-white transition-colors"
      >
        Sign out
      </button>
    </header>
  );
}
