import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "EDINET Viewer",
  description: "上場企業の大量保有報告書を閲覧・分析するためのWebアプリケーション",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja" suppressHydrationWarning>
      <body className={`${inter.variable} antialiased`} suppressHydrationWarning>
        <div className="min-h-screen bg-white flex">
          {/* サイドバー */}
          <aside className="w-64 bg-[#f8f9fc] border-r border-gray-200 fixed h-full">
            <div className="p-6">
              {/* ロゴ */}
              <Link href="/" className="flex items-center gap-3 mb-8">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <span className="text-lg font-bold text-indigo-600">EDINET Viewer</span>
              </Link>

              {/* ナビゲーション */}
              <nav className="space-y-2">
                <Link
                  href="/"
                  className="flex items-center gap-3 px-4 py-3 rounded-xl bg-indigo-50 text-indigo-600 font-medium"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  ダッシュボード
                </Link>
              </nav>
            </div>
          </aside>

          {/* メインコンテンツ */}
          <main className="flex-1 ml-64">
            <div className="p-8">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
