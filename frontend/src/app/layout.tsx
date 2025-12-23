import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "./components/Sidebar";

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
          {/* サイドバー（レスポンシブ対応） */}
          <Sidebar />

          {/* メインコンテンツ */}
          <main className="flex-1 lg:ml-64 w-full">
            <div className="p-4 sm:p-6 lg:p-8">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
