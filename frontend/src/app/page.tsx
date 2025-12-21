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
  const [searchQuery, setSearchQuery] = useState("");

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
      month: "2-digit",
      day: "2-digit",
    }).replace(/\//g, "-");
  };

  const filteredFilers = filers.filter(filer =>
    filer.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-500">データを読み込み中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
        <p className="text-red-600">{error}</p>
        <p className="text-sm text-gray-500 mt-2">
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
    );
  }

  return (
    <div>
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">マーケット・ウォッチ</h1>
          <p className="text-gray-500 mt-1">主要な大量保有報告提出者の動向を追跡</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="relative">
            <svg className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="提出者名を検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 w-64 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={() => {
              setLoading(true);
              fetchFilers();
            }}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      {/* 提出者一覧 */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <h2 className="text-lg font-semibold text-gray-900">追跡中の提出者一覧</h2>
          </div>
          <span className="text-sm text-gray-500">全 {filteredFilers.length} 社</span>
        </div>

        {filteredFilers.length === 0 ? (
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-12 text-center">
            <p className="text-gray-500">
              {searchQuery ? "検索結果がありません" : "登録されている提出者がありません"}
            </p>
          </div>
        ) : (
          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
            {filteredFilers.map((filer, index) => (
              <Link
                key={filer.id}
                href={`/filer/${filer.id}`}
                className={`flex items-center justify-between p-5 hover:bg-gray-50 transition-colors ${index !== filteredFilers.length - 1 ? "border-b border-gray-100" : ""
                  }`}
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center">
                    <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{filer.name}</h3>
                    <p className="text-sm text-gray-500 flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      最終更新: {formatDate(filer.latest_filing_date)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-8">
                  <div className="text-center">
                    <p className="text-xs text-gray-400 mb-1">直近の報告</p>
                    <p className="text-xl font-bold text-gray-900">{filer.filing_count}<span className="text-sm font-normal text-gray-500 ml-1">件</span></p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-400 mb-1">推定保有</p>
                    <p className="text-xl font-bold text-gray-900">{filer.issuer_count}<span className="text-sm font-normal text-gray-500 ml-1">銘柄</span></p>
                  </div>
                  <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
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
