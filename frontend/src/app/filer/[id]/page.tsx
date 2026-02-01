"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { IssuerTable } from "./IssuerTable";
import { api, Filer, Issuer } from "@/lib/api";

const ITEMS_PER_PAGE = 50;

export default function FilerDetail() {
    const params = useParams();
    const filerId = params.id as string;

    const [filer, setFiler] = useState<Filer | null>(null);
    const [issuers, setIssuers] = useState<Issuer[]>([]);
    const [loading, setLoading] = useState(true);
    const [issuersLoading, setIssuersLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [debouncedSearch, setDebouncedSearch] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const [totalCount, setTotalCount] = useState(0);
    const [sortKey, setSortKey] = useState<"date" | "ratio" | "name">("date");
    const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

    // デバウンス処理
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(searchQuery);
            setCurrentPage(1);
        }, 300);
        return () => clearTimeout(timer);
    }, [searchQuery]);

    const fetchFiler = useCallback(async () => {
        try {
            const data = await api.getFiler(Number(filerId));
            setFiler(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : "エラーが発生しました");
        } finally {
            setLoading(false);
        }
    }, [filerId]);

    const fetchIssuers = useCallback(async () => {
        setIssuersLoading(true);
        try {
            const skip = (currentPage - 1) * ITEMS_PER_PAGE;
            const data = await api.getIssuersByFiler(
                Number(filerId),
                skip,
                ITEMS_PER_PAGE,
                debouncedSearch || undefined
            );
            setIssuers(data.items);
            setTotalCount(data.total);
        } catch (err) {
            console.error(err);
        } finally {
            setIssuersLoading(false);
        }
    }, [filerId, currentPage, debouncedSearch]);

    useEffect(() => {
        if (filerId) {
            fetchFiler();
        }
    }, [filerId, fetchFiler]);

    useEffect(() => {
        if (filerId) {
            fetchIssuers();
        }
    }, [filerId, fetchIssuers]);



    // クライアントサイドソート
    const sortedIssuers = [...issuers].sort((a, b) => {
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
            case "name":
                const nameA = a.name || a.edinet_code;
                const nameB = b.name || b.edinet_code;
                comparison = nameA.localeCompare(nameB, "ja");
                break;
        }

        return sortOrder === "asc" ? comparison : -comparison;
    });

    const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE);

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
                        onClick={fetchIssuers}
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
                        <span className="text-sm text-gray-500">
                            (全{totalCount.toLocaleString()}銘柄中 {((currentPage - 1) * ITEMS_PER_PAGE) + 1}-{Math.min(currentPage * ITEMS_PER_PAGE, totalCount)}件)
                        </span>
                    </div>

                    {/* ソートコントロール */}
                    <div className="flex items-center gap-2">
                        <select
                            value={sortKey}
                            onChange={(e) => setSortKey(e.target.value as "date" | "ratio" | "name")}
                            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg bg-gray-50 text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
                        >
                            <option value="date">⛲ 更新日</option>
                            <option value="ratio">📊 保有比率</option>
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

                {issuersLoading ? (
                    <div className="flex items-center justify-center min-h-[300px]">
                        <div className="flex flex-col items-center gap-4">
                            <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                            <p className="text-gray-500">読み込み中...</p>
                        </div>
                    </div>
                ) : sortedIssuers.length === 0 ? (
                    <div className="bg-gray-50 border border-gray-200 rounded-xl p-12 text-center">
                        <p className="text-gray-500">
                            {searchQuery ? "検索結果がありません" : "保有銘柄データがありません"}
                        </p>
                    </div>
                ) : (
                    <>
                        <IssuerTable
                            issuers={sortedIssuers}
                            filerId={filerId}
                            sortKey={sortKey}
                            sortOrder={sortOrder}
                            onSort={(key) => {
                                if (sortKey === key) {
                                    setSortOrder(sortOrder === "asc" ? "desc" : "asc");
                                } else {
                                    setSortKey(key);
                                    setSortOrder("desc"); // Default to desc for new sort
                                }
                            }}
                        />

                        {/* ページネーション */}
                        {totalPages > 1 && (
                            <div className="flex items-center justify-center gap-2 mt-6">
                                <button
                                    onClick={() => setCurrentPage(1)}
                                    disabled={currentPage === 1}
                                    className="px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    «
                                </button>
                                <button
                                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                    disabled={currentPage === 1}
                                    className="px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    前へ
                                </button>

                                <span className="px-4 py-2 text-sm text-gray-700">
                                    {currentPage} / {totalPages}
                                </span>

                                <button
                                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                    disabled={currentPage === totalPages}
                                    className="px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    次へ
                                </button>
                                <button
                                    onClick={() => setCurrentPage(totalPages)}
                                    disabled={currentPage === totalPages}
                                    className="px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    »
                                </button>
                            </div>
                        )}
                    </>
                )}
            </section>
        </div>
    );
}

