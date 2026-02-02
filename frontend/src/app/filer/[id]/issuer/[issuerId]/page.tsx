"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { formatDate } from "@/utils/date";
import { useIssuerHistory } from "@/hooks";

export default function IssuerHistory() {
    const params = useParams();
    const filerId = params.id as string;
    const issuerId = params.issuerId as string;

    const { data, loading, error } = useIssuerHistory(filerId, issuerId);

    const formatNumber = (num: number | null) => {
        if (num === null) return "-";
        return num.toLocaleString();
    };

    const formatRatio = (ratio: number | null) => {
        if (ratio === null) return "-";
        return `${ratio.toFixed(2)}%`;
    };

    const getDocTypeStyle = (description: string | null) => {
        if (!description) return "bg-gray-100 text-gray-600";
        if (description.includes("大量保有報告書")) return "bg-emerald-100 text-emerald-700";
        if (description.includes("変更報告書")) return "bg-indigo-100 text-indigo-700";
        if (description.includes("訂正")) return "bg-amber-100 text-amber-700";
        return "bg-gray-100 text-gray-600";
    };

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto">
                <div className="flex items-center justify-center min-h-[400px]">
                    <div className="flex flex-col items-center gap-4">
                        <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                        <p className="text-gray-500">履歴データを読み込み中...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="max-w-7xl mx-auto">
                <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
                    <p className="text-red-600">{error || "データが見つかりません"}</p>
                    <Link
                        href={`/filer/${filerId}`}
                        className="mt-4 inline-block px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors"
                    >
                        銘柄一覧に戻る
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto">
            {/* パンくずリスト */}
            <nav className="mb-4 sm:mb-6 overflow-x-auto">
                <ol className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm whitespace-nowrap">
                    <li>
                        <Link href="/" className="text-gray-400 hover:text-gray-600 transition-colors">
                            ホーム
                        </Link>
                    </li>
                    <li className="text-gray-300">/</li>
                    <li>
                        <Link href={`/filer/${filerId}`} className="text-gray-400 hover:text-gray-600 transition-colors truncate max-w-[120px] sm:max-w-none inline-block align-bottom">
                            {data.filer.name}
                        </Link>
                    </li>
                    <li className="text-gray-300">/</li>
                    <li className="text-gray-900 font-medium truncate max-w-[120px] sm:max-w-none">{data.issuer.name || data.issuer.edinet_code}</li>
                </ol>
            </nav>

            {/* 銘柄情報ヘッダー */}
            <section className="mb-6 sm:mb-8">
                <div className="bg-white border border-gray-200 rounded-xl sm:rounded-2xl p-4 sm:p-8 shadow-sm">
                    <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                        <div className="flex items-start gap-3 sm:gap-6">
                            <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-xl sm:rounded-2xl bg-linear-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg sm:text-2xl shrink-0">
                                {(data.issuer.name || data.issuer.edinet_code).charAt(0)}
                            </div>
                            <div className="min-w-0 flex-1">
                                <h1 className="text-lg sm:text-2xl font-bold text-gray-900 mb-0.5 sm:mb-1 truncate">
                                    {data.issuer.name || data.issuer.edinet_code}
                                </h1>
                                {data.issuer.sec_code && (
                                    <p className="text-gray-500 text-xs sm:text-sm">
                                        <span className="px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded text-xs font-medium">
                                            {data.issuer.sec_code.slice(0, 4)}
                                        </span>
                                    </p>
                                )}
                                <p className="text-gray-500 mt-1 sm:mt-2 text-xs sm:text-base truncate">
                                    提出者: <span className="text-gray-700 font-medium">{data.filer.name}</span>
                                </p>
                            </div>
                        </div>
                        <div className="text-left sm:text-right pl-15 sm:pl-0">
                            <p className="text-2xl sm:text-4xl font-bold text-indigo-600">{data.history.length}</p>
                            <p className="text-xs sm:text-sm text-gray-500">報告書数</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* 履歴タイムライン */}
            <section>
                <div className="flex items-center gap-2 mb-4 sm:mb-6">
                    <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <h2 className="text-lg sm:text-xl font-bold text-gray-900">報告書履歴</h2>
                </div>

                {data.history.length === 0 ? (
                    <div className="bg-gray-50 border border-gray-200 rounded-xl sm:rounded-2xl p-8 sm:p-12 text-center">
                        <p className="text-gray-500">履歴データがありません</p>
                    </div>
                ) : (
                    <div className="space-y-3 sm:space-y-4">
                        {data.history.map((item) => (
                            <div
                                key={item.doc_id}
                                className="bg-white border border-gray-200 rounded-xl p-4 sm:p-6 hover:border-indigo-300 hover:shadow-md transition-all"
                            >
                                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 sm:gap-0">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 sm:gap-3 mb-2 flex-wrap">
                                            <span className={`px-2 py-0.5 sm:py-1 text-[10px] sm:text-xs font-medium rounded-full ${getDocTypeStyle(item.doc_description)}`}>
                                                {item.doc_description || "報告書"}
                                            </span>
                                            <span className="text-xs sm:text-sm text-gray-500">
                                                {formatDate(item.submit_date)}
                                            </span>
                                        </div>

                                        <div className="grid grid-cols-3 gap-2 sm:gap-4 mt-3 sm:mt-4">
                                            <div>
                                                <p className="text-[10px] sm:text-xs text-gray-400 mb-0.5 sm:mb-1">保有株数</p>
                                                <p className="text-sm sm:text-lg font-semibold text-gray-900">
                                                    {item.shares_held !== null ? (
                                                        <><span className="hidden sm:inline">{formatNumber(item.shares_held)}</span><span className="sm:hidden">{(item.shares_held / 1000).toFixed(0)}K</span> 株</>
                                                    ) : "-"}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-[10px] sm:text-xs text-gray-400 mb-0.5 sm:mb-1">保有比率</p>
                                                <p className="text-sm sm:text-lg font-bold text-indigo-600">
                                                    {item.holding_ratio !== null ? formatRatio(item.holding_ratio) : "-"}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-[10px] sm:text-xs text-gray-400 mb-0.5 sm:mb-1">増減</p>
                                                <p className={`text-sm sm:text-lg font-semibold ${item.ratio_change === null ? "text-gray-400" :
                                                    item.ratio_change > 0 ? "text-emerald-500" :
                                                        item.ratio_change < 0 ? "text-red-500" : "text-gray-400"
                                                    }`}>
                                                    {item.ratio_change !== null ? (
                                                        <>
                                                            {item.ratio_change > 0 ? "+" : ""}
                                                            {formatRatio(item.ratio_change)}
                                                        </>
                                                    ) : "-"}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </section>
        </div>
    );
}
