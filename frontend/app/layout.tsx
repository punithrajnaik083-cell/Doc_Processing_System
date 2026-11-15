import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { Providers } from "@/components/providers";
import { Toaster } from "@/components/ui/sonner";

export const metadata: Metadata = {
  title: "Document Processing Agent",
  description: "AI-driven business document processor and GST validator",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 font-sans text-slate-900">
        <Providers>
          <header className="sticky top-0 z-40 w-full border-b bg-white">
            <div className="container mx-auto flex h-16 items-center justify-between px-4 sm:px-8">
              <div className="flex items-center gap-8">
                <Link href="/" className="flex items-center gap-2">
                  <span className="text-lg font-bold tracking-tight text-slate-900">
                    Document Processing Agent
                  </span>
                </Link>
                <nav className="flex items-center gap-6 text-sm font-medium text-slate-600">
                  <Link
                    href="/"
                    className="transition-colors hover:text-slate-900"
                  >
                    Dashboard
                  </Link>
                  <Link
                    href="/upload"
                    className="transition-colors hover:text-slate-900"
                  >
                    Upload
                  </Link>
                  <Link
                    href="/documents"
                    className="transition-colors hover:text-slate-900"
                  >
                    Documents
                  </Link>
                </nav>
              </div>
            </div>
          </header>
          <main className="container mx-auto px-4 py-8 sm:px-8">{children}</main>
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}

