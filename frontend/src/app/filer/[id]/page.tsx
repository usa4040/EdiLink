"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

interface Filer {
    id: number;
    edinet_code: string;
    name: string;
    sec_code: string | null;
    filing_count: number;
    issuer_count: number;
}

interface Issuer {
    id: number;
    edinet_code: string;
    name: string;
    sec_code: string | null;
    latest_filing_date: string | null;
    filing_count: number;
    latest_ratio?: number | null;
    ratio_change?: number | null;
}

export default function FilerDetail() {
    const params = useParams();
    const filerId = params.id as string;

    const [filer, setFiler] = useState<Filer | null>(null);
    const [issuers, setIssuers] = useState<Issuer[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [sortKey, setSortKey] = useState<"date" | "ratio" | "name" | "change">("date");
    const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

    const fetchData = useCallback(async () => {
        try {
            const [filerRes, issuersRes] = await Promise.all([
                fetch(`http://localhost:8000/api/filers/${filerId}`),
                fetch(`http://localhost:8000/api/filers/${filerId}/issuers`),
            ]);

            if (!filerRes.ok) throw new Error("提出者が見つかりません");

            const filerData = await filerRes.json();
            const issuersData = await issuersRes.json();

            setFiler(filerData);
            setIssuers(issuersData);
        } catch (err) {
            setError(err instanceof Error ? err.message : "エラーが発生しました");
        } finally {
            setLoading(false);
        }
    }, [filerId]);

    useEffect(() => {
        if (filerId) {
            fetchData();
        }
    }, [filerId, fetchData]);

    const formatDate = (dateString: string | null) => {
        if (!dateString) return "-";
        const date = new Date(dateString);
        return date.toLocaleDateString("ja-JP", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
        }).replace(/\//g, "-");
    };

    const formatRatio = (ratio: number | null | undefined) => {
        if (ratio === null || ratio === undefined) return "-";
        return `${ratio.toFixed(2)}%`;
    };

    const filteredIssuers = issuers.filter(issuer =>
        (issuer.name || issuer.edinet_code).toLowerCase().includes(searchQuery.toLowerCase()) ||
        (issuer.sec_code || "").includes(searchQuery)
    );

    // ソート処理
    const sortedIssuers = [...filteredIssuers].sort((a, b) => {
        let comparison = 0;

        switch (sortKey) {
            case "date":
                const dateA = a.latest_filing_date ? new Date(a.latest_filing_date).getTime() : 0;
                const dateB = b.latest_filing_date ? new Date(b.latest_filing_date).getTime() : 0;
                comparison = dateA - dateB;
                break;
            case "ratio":
                const ratioA = a.latest_ratio ?? -1;
                const ratioB = b.latest_ratio ?? -1;
                comparison = ratioA - ratioB;
                break;
            case "change":
                const changeA = a.ratio_change ?? -999;
                const changeB = b.ratio_change ?? -999;
                comparison = changeA - changeB;
                break;
            case "name":
                const nameA = a.name || a.edinet_code;
                const nameB = b.name || b.edinet_code;
                comparison = nameA.localeCompare(nameB, "ja");
                break;
        }

        return sortOrder === "asc" ? comparison : -comparison;
    });

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

    if (error || !filer) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
                <p className="text-red-600">{error || "提出者が見つかりません"}</p>
                <Link
                    href="/"
                    className="mt-4 inline-block px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors"
                >
                    トップに戻る
                </Link>
            </div>
        );
    }

    return (
        <div>
            {/* ヘッダー */}
            <div className="flex flex-col gap-4 mb-6 sm:mb-8">
                <div className="flex items-center gap-3">
                    <Link href="/" className="text-gray-400 hover:text-gray-600 transition-colors shrink-0">
                        <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                    </Link>
                    <div className="min-w-0 flex-1">
                        <h1 className="text-lg sm:text-2xl font-bold text-gray-900 truncate">{filer.name}</h1>
                        <p className="text-sm sm:text-base text-gray-500 mt-0.5 sm:mt-1">保有銘柄リスト・動向分析</p>
                    </div>
                </div>
                <div className="flex items-center gap-2 sm:gap-4">
                    <div className="relative flex-1">
                        <svg className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        <input
                            type="text"
                            placeholder="銘柄名 / コード..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg bg-gray-50 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent focus:bg-white text-sm sm:text-base"
                        />
                    </div>
                    <button
                        onClick={() => {
                            setLoading(true);
                            fetchData();
                        }}
                        className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors shrink-0"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                    </button>
                </div>
            </div>

            {/* 銘柄一覧 */}
            <section>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                    <div className="flex items-center gap-2">
                        <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <h2 className="text-lg font-semibold text-gray-900">保有銘柄一覧</h2>
                        <span className="text-sm text-gray-500">({sortedIssuers.length}銘柄)</span>
                    </div>

                    {/* ソートコントロール */}
                    <div className="flex items-center gap-2">
                        <select
                            value={sortKey}
                            onChange={(e) => setSortKey(e.target.value as "date" | "ratio" | "name" | "change")}
                            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg bg-gray-50 text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
                        >
                            <option value="date">⛲ 更新日</option>
                            <option value="ratio">📊 保有比率</option>
                            <option value="change">📈 増減</option>
                            <option value="name">🎯 銘柄名</option>
                        </select>
                        <button
                            onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
                            className="p-1.5 border border-gray-200 rounded-lg bg-white hover:bg-gray-50 transition-colors"
                            title={sortOrder === "asc" ? "昇順" : "降順"}
                        >
                            {sortOrder === "desc" ? (
                                <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                </svg>
                            ) : (
                                <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                                </svg>
                            )}
                        </button>
                    </div>
                </div>

                {sortedIssuers.length === 0 ? (
                    <div className="bg-gray-50 border border-gray-200 rounded-xl p-12 text-center">
                        <p className="text-gray-500">
                            {searchQuery ? "検索結果がありません" : "保有銘柄データがありません"}
                        </p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                        {sortedIssuers.map((issuer) => (
                            <Link
                                key={issuer.id}
                                href={`/filer/${filerId}/issuer/${issuer.id}`}
                                className="bg-white border border-gray-200 rounded-xl p-4 sm:p-5 hover:border-indigo-300 hover:shadow-md transition-all active:scale-[0.98]"
                            >
                                {/* ヘッダー */}
                                <div className="flex items-start justify-between mb-2 sm:mb-3">
                                    <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
                                        {issuer.filing_count === 1 && (
                                            <span className="px-1.5 sm:px-2 py-0.5 sm:py-1 bg-emerald-100 text-emerald-600 text-[10px] sm:text-xs font-bold rounded">
                                                New!
                                            </span>
                                        )}
                                        {issuer.sec_code && (
                                            <span className="px-1.5 sm:px-2 py-0.5 sm:py-1 bg-indigo-100 text-indigo-600 text-[10px] sm:text-xs font-medium rounded">
                                                {issuer.sec_code.slice(0, 4)}
                                            </span>
                                        )}
                                        <span className="text-[10px] sm:text-xs text-gray-400">{formatDate(issuer.latest_filing_date)}</span>
                                    </div>
                                    <svg className="w-4 h-4 text-gray-300 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                </div>

                                {/* 銘柄名 */}
                                <h3 className="font-semibold text-gray-900 mb-3 sm:mb-4 line-clamp-2 text-sm sm:text-base">{issuer.name || issuer.edinet_code}</h3>

                                {/* 保有比率 */}
                                <div className="flex items-end justify-between">
                                    <div>
                                        <p className="text-[10px] sm:text-xs text-gray-400 mb-0.5 sm:mb-1">保有比率</p>
                                        <p className="text-xl sm:text-2xl font-bold text-gray-900">{formatRatio(issuer.latest_ratio)}</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-[10px] sm:text-xs text-gray-400 mb-0.5 sm:mb-1">増減</p>
                                        {issuer.ratio_change !== null && issuer.ratio_change !== undefined ? (
                                            <p className={`text-base sm:text-lg font-semibold ${issuer.ratio_change > 0 ? "text-emerald-500" :
                                                issuer.ratio_change < 0 ? "text-red-500" : "text-gray-400"
                                                }`}>
                                                {issuer.ratio_change > 0 ? "+" : ""}{formatRatio(issuer.ratio_change)}
                                            </p>
                                        ) : (
                                            <p className="text-base sm:text-lg text-gray-400">-</p>
                                        )}
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
