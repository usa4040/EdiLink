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
