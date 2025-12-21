"use client";

import { useEffect, useState } from "react";
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
}

export default function FilerDetail() {
    const params = useParams();
    const filerId = params.id as string;

    const [filer, setFiler] = useState<Filer | null>(null);
    const [issuers, setIssuers] = useState<Issuer[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (filerId) {
            fetchData();
        }
    }, [filerId]);

    const fetchData = async () => {
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

    if (error || !filer) {
        return (
            <div className="max-w-7xl mx-auto px-6">
                <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-6 text-center">
                    <p className="text-red-400">{error || "提出者が見つかりません"}</p>
                    <Link
                        href="/"
                        className="mt-4 inline-block px-4 py-2 bg-zinc-700 hover:bg-zinc-600 text-white rounded-lg transition-colors"
                    >
                        トップに戻る
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-6">
            {/* パンくずリスト */}
            <nav className="mb-6 animate-fade-in">
                <ol className="flex items-center gap-2 text-sm">
                    <li>
                        <Link href="/" className="text-zinc-400 hover:text-white transition-colors">
                            ホーム
                        </Link>
                    </li>
                    <li className="text-zinc-600">/</li>
                    <li className="text-white">{filer.name}</li>
                </ol>
            </nav>

            {/* 提出者情報 */}
            <section className="mb-8 animate-fade-in">
                <div className="bg-[#1a1a2e] border border-[#2d2d44] rounded-2xl p-8">
                    <div className="flex items-start gap-6">
                        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-3xl">
                            {filer.name.charAt(0)}
                        </div>
                        <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                                <h1 className="text-3xl font-bold text-white">{filer.name}</h1>
                            </div>
                            {filer.sec_code && (
                                <p className="text-zinc-400">証券コード: {filer.sec_code}</p>
                            )}
                            <div className="flex gap-8 mt-4">
                                <div>
                                    <p className="text-3xl font-bold text-indigo-400">{filer.issuer_count || 0}</p>
                                    <p className="text-sm text-zinc-500">保有銘柄数</p>
                                </div>
                                <div>
                                    <p className="text-3xl font-bold text-purple-400">{filer.filing_count || 0}</p>
                                    <p className="text-sm text-zinc-500">報告書数</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* 保有銘柄一覧 */}
            <section className="animate-fade-in" style={{ animationDelay: "0.1s" }}>
                <h2 className="text-2xl font-bold text-white mb-6">保有銘柄一覧</h2>

                {issuers.length === 0 ? (
                    <div className="bg-[#1a1a2e] border border-[#2d2d44] rounded-2xl p-12 text-center">
                        <p className="text-zinc-400">保有銘柄データがありません</p>
                    </div>
                ) : (
                    <div className="bg-[#1a1a2e] border border-[#2d2d44] rounded-2xl overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-[#2d2d44]">
                                        <th className="text-left px-6 py-4 text-sm font-medium text-zinc-400">銘柄</th>
                                        <th className="text-right px-6 py-4 text-sm font-medium text-zinc-400">報告書数</th>
                                        <th className="text-right px-6 py-4 text-sm font-medium text-zinc-400">最終報告日</th>
                                        <th className="text-center px-6 py-4 text-sm font-medium text-zinc-400">操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {issuers.map((issuer, index) => (
                                        <tr
                                            key={issuer.id}
                                            className="border-b border-[#2d2d44] hover:bg-indigo-500/5 transition-colors table-row-striped"
                                        >
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white font-bold text-sm">
                                                        {(issuer.name || issuer.edinet_code).charAt(0)}
                                                    </div>
                                                    <div>
                                                        <p className="font-medium text-white">
                                                            {issuer.name || issuer.edinet_code}
                                                        </p>
                                                        {issuer.sec_code && (
                                                            <p className="text-xs text-zinc-500">{issuer.sec_code}</p>
                                                        )}
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-sm rounded-full">
                                                    {issuer.filing_count}件
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-right text-zinc-400 text-sm">
                                                {formatDate(issuer.latest_filing_date)}
                                            </td>
                                            <td className="px-6 py-4 text-center">
                                                <Link
                                                    href={`/filer/${filerId}/issuer/${issuer.id}`}
                                                    className="inline-flex items-center gap-1 px-3 py-1.5 bg-indigo-500 hover:bg-indigo-600 text-white text-sm rounded-lg transition-colors"
                                                >
                                                    履歴を見る
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                    </svg>
                                                </Link>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </section>
        </div>
    );
}
