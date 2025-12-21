"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Filer {
  id: number;
  edinet_code: string;
  name: string;
  sec_code: string | null;
  filing_count: number;
  issuer_count: number;
  latest_filing_date: string | null;
}

export default function Home() {
  const [filers, setFilers] = useState<Filer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFilers();
  }, []);

  const fetchFilers = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/filers");
      if (!response.ok) throw new Error("Failed to fetch filers");
      const data = await response.json();
      setFilers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "エラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "-";
    const date = new Date(dateString);
    return date.toLocaleDateString("ja-JP", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-zinc-400">データを読み込み中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-6">
        <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-6 text-center">
          <p className="text-red-400">{error}</p>
          <p className="text-sm text-zinc-500 mt-2">
            バックエンドサーバーが起動しているか確認してください
          </p>
          <button
            onClick={() => {
              setLoading(true);
              setError(null);
              fetchFilers();
            }}
            className="mt-4 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
          >
            再試行
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6">
      {/* ヒーローセクション */}
      <section className="mb-12 animate-fade-in">
        <h1 className="text-4xl font-bold mb-4">
          <span className="gradient-text">大量保有報告書</span>ビューア
        </h1>
        <p className="text-lg text-zinc-400 max-w-2xl">
          EDINET APIから取得した大量保有報告書のデータを閲覧・分析できます。
          提出者を選択して、保有銘柄の履歴を確認しましょう。
        </p>
      </section>

      {/* 統計 */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="bg-[#1a1a2e] border border-[#2d2d44] rounded-2xl p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div>
              <p className="text-3xl font-bold text-white">{filers.length}</p>
              <p className="text-sm text-zinc-400">登録提出者</p>
            </div>
          </div>
        </div>

        <div className="bg-[#1a1a2e] border border-[#2d2d44] rounded-2xl p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <p className="text-3xl font-bold text-white">
                {filers.reduce((sum, f) => sum + (f.filing_count || 0), 0)}
              </p>
              <p className="text-sm text-zinc-400">総報告書数</p>
            </div>
          </div>
        </div>

        <div className="bg-[#1a1a2e] border border-[#2d2d44] rounded-2xl p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div>
              <p className="text-3xl font-bold text-white">
                {filers.reduce((sum, f) => sum + (f.issuer_count || 0), 0)}
              </p>
              <p className="text-sm text-zinc-400">総保有銘柄数</p>
            </div>
          </div>
        </div>
      </section>

      {/* 提出者一覧 */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">提出者一覧</h2>
          <button className="px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg transition-colors flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            提出者を追加
          </button>
        </div>

        {filers.length === 0 ? (
          <div className="bg-[#1a1a2e] border border-[#2d2d44] rounded-2xl p-12 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-zinc-800 flex items-center justify-center">
              <svg className="w-8 h-8 text-zinc-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <p className="text-zinc-400">登録されている提出者がありません</p>
            <p className="text-sm text-zinc-500 mt-2">
              「提出者を追加」ボタンから新しい提出者を登録してください
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filers.map((filer, index) => (
              <Link
                key={filer.id}
                href={`/filer/${filer.id}`}
                className="block"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="bg-[#1a1a2e] border border-[#2d2d44] rounded-2xl p-6 card-hover animate-fade-in">
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg">
                      {filer.name.charAt(0)}
                    </div>
                    <span className="px-2 py-1 bg-indigo-500/20 text-indigo-400 text-xs rounded-full">
                      {filer.edinet_code}
                    </span>
                  </div>

                  <h3 className="text-lg font-semibold text-white mb-2 truncate">
                    {filer.name}
                  </h3>

                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div>
                      <p className="text-2xl font-bold text-indigo-400">{filer.issuer_count || 0}</p>
                      <p className="text-xs text-zinc-500">保有銘柄</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-purple-400">{filer.filing_count || 0}</p>
                      <p className="text-xs text-zinc-500">報告書数</p>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-[#2d2d44]">
                    <p className="text-xs text-zinc-500">
                      最終更新: {formatDate(filer.latest_filing_date)}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
