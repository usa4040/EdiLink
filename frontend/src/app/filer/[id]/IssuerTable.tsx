"use client";

import Link from "next/link";
import { formatDate } from "@/utils/date";

interface Issuer {
    id: number;
    edinet_code: string;
    name: string | null;
    sec_code: string | null;
    latest_filing_date: string | null;
    filing_count: number | null;
    latest_ratio?: number | null;
    latest_purpose?: string | null;
    ratio_change?: number | null;
}

interface IssuerTableProps {
    issuers: Issuer[];
    filerId: string;
    sortKey: "date" | "ratio" | "name";
    sortOrder: "asc" | "desc";
    onSort: (key: "date" | "ratio" | "name") => void;
}

const SortIcon = ({ active, order }: { active: boolean; order: "asc" | "desc" }) => {
    if (!active) return <span className="opacity-20 ml-1">⇅</span>;
    return <span className="ml-1 text-indigo-500">{order === "asc" ? "↑" : "↓"}</span>;
};

export function IssuerTable({ issuers, filerId, sortKey, sortOrder, onSort }: IssuerTableProps) {
    const formatRatio = (ratio: number | null | undefined) => {
        if (ratio === null || ratio === undefined) return "-";
        return `${ratio.toFixed(2)}%`;
    };



    return (
        <div className="overflow-x-auto bg-white border border-gray-200 rounded-xl shadow-sm">
            <table className="w-full text-left text-sm whitespace-nowrap">
                <thead className="bg-gray-50 text-gray-600 font-medium">
                    <tr>
                        <th
                            className="px-4 py-3 cursor-pointer hover:bg-gray-100 transition-colors"
                            onClick={() => onSort("name")}
                        >
                            銘柄名 <SortIcon active={sortKey === "name"} order={sortOrder} />
                        </th>
                        <th className="px-4 py-3">コード</th>
                        <th
                            className="px-4 py-3 cursor-pointer hover:bg-gray-100 transition-colors text-right"
                            onClick={() => onSort("ratio")}
                        >
                            保有比率 <SortIcon active={sortKey === "ratio"} order={sortOrder} />
                        </th>
                        <th className="px-4 py-3 text-right">報告数</th>
                        <th
                            className="px-4 py-3 cursor-pointer hover:bg-gray-100 transition-colors"
                            onClick={() => onSort("date")}
                        >
                            更新日 <SortIcon active={sortKey === "date"} order={sortOrder} />
                        </th>
                        <th className="px-4 py-3 max-w-[200px]">保有目的</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                    {issuers.map((issuer) => (
                        <tr
                            key={issuer.id}
                            className="hover:bg-indigo-50/30 transition-colors group"
                        >
                            <td className="px-4 py-3">
                                <Link
                                    href={`/filer/${filerId}/issuer/${issuer.id}`}
                                    className="font-medium text-indigo-600 hover:text-indigo-800 flex items-center gap-2"
                                >
                                    {issuer.name || issuer.edinet_code}
                                    {issuer.filing_count === 1 && (
                                        <span className="px-1.5 py-0.5 bg-emerald-100 text-emerald-600 text-[10px] font-bold rounded">New</span>
                                    )}
                                </Link>
                            </td>
                            <td className="px-4 py-3 text-gray-500">
                                {issuer.sec_code ? (
                                    <span className="font-mono bg-gray-100 px-1.5 py-0.5 rounded text-xs">{issuer.sec_code.slice(0, 4)}</span>
                                ) : (
                                    "-"
                                )}
                            </td>
                            <td className="px-4 py-3 text-right font-semibold text-gray-900">
                                {formatRatio(issuer.latest_ratio)}
                            </td>
                            <td className="px-4 py-3 text-right text-gray-600">
                                {issuer.filing_count}
                            </td>
                            <td className="px-4 py-3 text-gray-500">
                                {formatDate(issuer.latest_filing_date)}
                            </td>
                            <td className="px-4 py-3 text-gray-500 max-w-[200px] truncate" title={issuer.latest_purpose || ""}>
                                {issuer.latest_purpose || "-"}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
