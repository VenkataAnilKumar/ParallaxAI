import { createClient } from "@supabase/supabase-js";

// Placeholders keep `next build` working when env vars are absent (e.g. CI);
// auth calls will fail at runtime until real values are configured.
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "http://localhost:54321";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "public-anon-key";

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export async function getSession() {
  const { data: { session } } = await supabase.auth.getSession();
  return session;
}

export async function getToken(): Promise<string | null> {
  const session = await getSession();
  return session?.access_token ?? null;
}
