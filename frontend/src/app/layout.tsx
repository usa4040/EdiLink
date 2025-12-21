import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "EDINET 大量保有報告書ビューア",
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
        <div className="min-h-screen bg-[#0f0f0f]">
          {/* ヘッダー */}
          <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-[#2d2d44]">
            <div className="max-w-7xl mx-auto px-6 py-4">
              <div className="flex items-center justify-between">
                <a href="/" className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div>
                    <h1 className="text-lg font-bold text-white">EDINET Viewer</h1>
                    <p className="text-xs text-zinc-400">大量保有報告書</p>
                  </div>
                </a>
                <nav className="flex items-center gap-6">
                  <a href="/" className="text-sm text-zinc-300 hover:text-white transition-colors">
                    ホーム
                  </a>
                  <a href="/about" className="text-sm text-zinc-400 hover:text-white transition-colors">
                    使い方
                  </a>
                </nav>
              </div>
            </div>
          </header>

          {/* メインコンテンツ */}
          <main className="pt-24 pb-12">
            {children}
          </main>

          {/* フッター */}
          <footer className="border-t border-[#2d2d44] py-8">
            <div className="max-w-7xl mx-auto px-6 text-center text-sm text-zinc-500">
              <p>EDINET APIを使用して取得したデータを表示しています</p>
              <p className="mt-2">© 2024 EDINET Viewer</p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
