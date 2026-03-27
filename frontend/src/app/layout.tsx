import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Parallax — Multi-Agent Research Network",
  description:
    "Research any market, competitor, or trend with 7 specialized AI agents working in parallel.",
  openGraph: {
    title: "Parallax",
    description: "AI-powered research that's 10x faster and 10x deeper.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full bg-gray-950 text-gray-100 antialiased`}>
        {children}
      </body>
    </html>
  );
}
