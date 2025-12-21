"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

interface Filer {
    id: number;
    edinet_code: string;
    name: string;
}

interface Issuer {
    id: number;
    edinet_code: string;
    name: string;
    sec_code: string | null;
}

interface HistoryItem {
    doc_id: string;
    submit_date: string | null;
    doc_description: string | null;
    shares_held: number | null;
    holding_ratio: number | null;
    ratio_change: number | null;
}

interface HistoryResponse {
    filer: Filer;
    issuer: Issuer;
    history: HistoryItem[];
}

export default function IssuerHistory() {
    const params = useParams();
    const filerId = params.id as string;
    const issuerId = params.issuerId as string;

    const [data, setData] = useState<HistoryResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (filerId && issuerId) {
            fetchHistory();
        }
    }, [filerId, issuerId]);

    const fetchHistory = async () => {
        try {
            const response = await fetch(
                `http://localhost:8000/api/filers/${filerId}/issuers/${issuerId}/history`
            );
            if (!response.ok) throw new Error("データが見つかりません");
            const result = await response.json();
            setData(result);
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

    const formatNumber = (num: number | null) => {
        if (num === null) return "-";
        return num.toLocaleString();
    };

    const formatRatio = (ratio: number | null) => {
        if (ratio === null) return "-";
        return `${ratio.toFixed(2)}%`;
    };

    const getDocTypeColor = (description: string | null) => {
        if (!description) return "bg-zinc-500/20 text-zinc-400";
        if (description.includes("大量保有報告書")) return "bg-emerald-500/20 text-emerald-400";
        if (description.includes("変更報告書")) return "bg-indigo-500/20 text-indigo-400";
        if (description.includes("訂正")) return "bg-amber-500/20 text-amber-400";
        return "bg-zinc-500/20 text-zinc-400";
    };

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto px-6">
                <div className="flex items-center justify-center min-h-[400px]">
                    <div className="flex flex-col items-center gap-4">
                        <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                        <p className="text-zinc-400">履歴データを読み込み中...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="max-w-7xl mx-auto px-6">
                <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-6 text-center">
                    <p className="text-red-400">{error || "データが見つかりません"}</p>
                    <Link
                        href={`/filer/${filerId}`}
                        className="mt-4 inline-block px-4 py-2 bg-zinc-700 hover:bg-zinc-600 text-white rounded-lg transition-colors"
                    >
                        銘柄一覧に戻る
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-6">
            {/* パンくずリスト */}
            <nav className="mb-6 animate-fade-in">
                <ol className="flex items-center gap-2 text-sm flex-wrap">
                    <li>
                        <Link href="/" className="text-zinc-400 hover:text-white transition-colors">
                            ホーム
                        </Link>
                    </li>
                    <li className="text-zinc-600">/</li>
                    <li>
                        <Link href={`/filer/${filerId}`} className="text-zinc-400 hover:text-white transition-colors">
                            {data.filer.name}
                        </Link>
                    </li>
                    <li className="text-zinc-600">/</li>
                    <li className="text-white">{data.issuer.name || data.issuer.edinet_code}</li>
                </ol>
            </nav>

            {/* 銘柄情報ヘッダー */}
            <section className="mb-8 animate-fade-in">
                <div className="bg-[#1a1a2e] border border-[#2d2d44] rounded-2xl p-8">
                    <div className="flex items-start justify-between">
                        <div className="flex items-start gap-6">
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white font-bold text-2xl">
                                {(data.issuer.name || data.issuer.edinet_code).charAt(0)}
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-white mb-1">
                                    {data.issuer.name || data.issuer.edinet_code}
                                </h1>
                                <div className="flex items-center gap-3 text-sm">
                                    <span className="px-2 py-0.5 bg-zinc-700 text-zinc-300 rounded">
                                        {data.issuer.edinet_code}
                                    </span>
                                    {data.issuer.sec_code && (
                                        <span className="text-zinc-400">証券コード: {data.issuer.sec_code}</span>
                                    )}
                                </div>
                                <p className="text-zinc-500 mt-2">
                                    提出者: <span className="text-zinc-300">{data.filer.name}</span>
                                </p>
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="text-4xl font-bold text-indigo-400">{data.history.length}</p>
                            <p className="text-sm text-zinc-500">報告書数</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* 履歴タイムライン */}
            <section className="animate-fade-in" style={{ animationDelay: "0.1s" }}>
                <h2 className="text-xl font-bold text-white mb-6">報告書履歴</h2>

                {data.history.length === 0 ? (
                    <div className="bg-[#1a1a2e] border border-[#2d2d44] rounded-2xl p-12 text-center">
                        <p className="text-zinc-400">履歴データがありません</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {data.history.map((item, index) => (
                            <div
                                key={item.doc_id}
                                className="bg-[#1a1a2e] border border-[#2d2d44] rounded-xl p-6 hover:border-indigo-500/50 transition-all"
                                style={{ animationDelay: `${index * 0.05}s` }}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            <span className={`px-2 py-1 text-xs rounded-full ${getDocTypeColor(item.doc_description)}`}>
                                                {item.doc_description || "報告書"}
                                            </span>
                                            <span className="text-sm text-zinc-500">
                                                {formatDate(item.submit_date)}
                                            </span>
                                        </div>

                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                                            <div>
                                                <p className="text-xs text-zinc-500 mb-1">保有株数</p>
                                                <p className="text-lg font-semibold text-white">
                                                    {item.shares_held !== null ? formatNumber(item.shares_held) + " 株" : "未取得"}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-xs text-zinc-500 mb-1">保有比率</p>
                                                <p className="text-lg font-semibold text-indigo-400">
                                                    {item.holding_ratio !== null ? formatRatio(item.holding_ratio) : "未取得"}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-xs text-zinc-500 mb-1">増減</p>
                                                <p className={`text-lg font-semibold ${item.ratio_change === null ? "text-zinc-400" :
                                                        item.ratio_change > 0 ? "text-emerald-400" :
                                                            item.ratio_change < 0 ? "text-red-400" : "text-zinc-400"
                                                    }`}>
                                                    {item.ratio_change !== null ? (
                                                        <>
                                                            {item.ratio_change > 0 ? "+" : ""}
                                                            {formatRatio(item.ratio_change)}
                                                        </>
                                                    ) : "-"}
                                                </p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-xs text-zinc-500 mb-1">書類ID</p>
                                                <a
                                                    href={`https://disclosure.edinet-fsa.go.jp/E01EW/BLMainController.jsp?uji.verb=W1E63011CXW1E6A011DSPSub&uji.bean=ek.bean.parent.EKW1E6A011FBParentDSPBean&TID=W1E63011&PID=W1E63011&SESSIONKEY=null&lgKbn=2&pkbn=1&skbn=1&dskb=&askb=&dflg=0&iflg=0&preId=1&sec=${item.doc_id}`}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="text-sm text-indigo-400 hover:text-indigo-300 font-mono"
                                                >
                                                    {item.doc_id}
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </section>

            {/* EDINET原本へのリンク */}
            <section className="mt-8 animate-fade-in" style={{ animationDelay: "0.2s" }}>
                <div className="bg-indigo-500/10 border border-indigo-500/30 rounded-xl p-6">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center">
                            <svg className="w-6 h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                        </div>
                        <div>
                            <p className="text-white font-medium">EDINETで原本を確認</p>
                            <p className="text-sm text-zinc-400">
                                各報告書のdocIDをクリックすると、EDINET公式サイトで原本を閲覧できます
                            </p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
