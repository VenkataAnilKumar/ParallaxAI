"use client";

import { useEffect, useState } from "react";
import { auth, type UserProfile } from "@/lib/api";
import { getToken } from "@/lib/supabase";

export default function SettingsPage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      const token = await getToken();
      if (!token) return;
      try {
        setProfile(await auth.me(token));
      } catch {
        setError("Failed to load profile");
      }
    }
    load();
  }, []);

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="mt-1 text-sm text-gray-400">Your account and plan.</p>
      </div>

      <div className="card space-y-3">
        <h2 className="text-sm font-semibold text-brand-400 uppercase tracking-wider">Profile</h2>
        {error && <p className="text-sm text-red-400">{error}</p>}
        {profile ? (
          <dl className="grid grid-cols-3 gap-2 text-sm">
            <dt className="text-gray-500">Name</dt>
            <dd className="col-span-2 text-gray-200">{profile.full_name ?? "—"}</dd>
            <dt className="text-gray-500">Email</dt>
            <dd className="col-span-2 text-gray-200">{profile.email}</dd>
            <dt className="text-gray-500">Member since</dt>
            <dd className="col-span-2 text-gray-200">
              {new Date(profile.created_at).toLocaleDateString()}
            </dd>
          </dl>
        ) : (
          !error && <div className="h-16 rounded-lg bg-gray-800 animate-pulse" />
        )}
      </div>

      <div className="card space-y-2">
        <h2 className="text-sm font-semibold text-brand-400 uppercase tracking-wider">Plan</h2>
        <p className="text-sm text-gray-200">Free — 3 research tasks per month</p>
        <p className="text-xs text-gray-500">Paid plans are coming soon.</p>
      </div>
    </div>
  );
}
