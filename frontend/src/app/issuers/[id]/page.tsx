'use client';

import { useState, useEffect, use } from 'react';
import Link from 'next/link';

interface OwnershipItem {
    filer_id: number;
    filer_name: string;
    latest_submit_date: string;
    shares_held: number | null;
    holding_ratio: number | null;
    purpose: string | null;
}

interface IssuerDetail {
    id: number;
    edinet_code: string;
    name: string;
    sec_code?: string;
}

interface IssuerOwnershipResponse {
    issuer: IssuerDetail;
    ownerships: OwnershipItem[];
}

export default function IssuerDetailPage({ params }: { params: Promise<{ id: string }> }) {
    // Next.js 15+ (Wait for params)
    const { id } = use(params);

    const [data, setData] = useState<IssuerOwnershipResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch(`http://localhost:8000/api/issuers/${id}/ownerships`);
                if (!res.ok) {
                    if (res.status === 404) throw new Error('銘柄が見つかりませんでした');
                    throw new Error('データの取得に失敗しました');
                }
                const json = await res.json();
                setData(json);
            } catch (err: unknown) {
                if (err instanceof Error) {
                    setError(err.message);
                } else {
                    setError('予期せぬエラーが発生しました');
                }
            } finally {
                setLoading(false);
            }
        };

        if (id) {
            fetchData();
        }
    }, [id]);

    if (loading) return <div className="container mx-auto p-8 text-center text-gray-500">読み込み中...</div>;
    if (error) return <div className="container mx-auto p-8 text-center text-red-500">{error}</div>;
    if (!data) return null;

    return (
        <div className="container mx-auto p-8">
            <div className="mb-8">
                <Link href="/issuers" className="text-gray-500 hover:text-gray-700 flex items-center gap-1 mb-4">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    銘柄検索に戻る
                </Link>
                <div className="flex items-baseline gap-4">
                    <h1 className="text-3xl font-bold text-gray-900">{data.issuer.name}</h1>
                    <span className="text-xl text-gray-500 font-mono">({data.issuer.sec_code})</span>
                    <span className="text-sm bg-gray-100 text-gray-600 px-2 py-1 rounded font-mono">
                        {data.issuer.edinet_code}
                    </span>
                </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-4 bg-gray-50 border-b border-gray-200">
                    <h2 className="font-bold text-gray-800 flex items-center gap-2">
                        <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                        保有投資家リスト ({data.ownerships.length})
                    </h2>
                </div>

                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">投資家名</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">保有比率</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">保有株数</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最終報告日</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">アクション</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {data.ownerships.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                                        現在この銘柄を保有している投資家はいません
                                    </td>
                                </tr>
                            ) : (
                                data.ownerships.map((item) => (
                                    <tr key={item.filer_id} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                            {item.filer_name}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-mono font-bold text-gray-900">
                                            {item.holding_ratio != null ? `${item.holding_ratio}%` : '-'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-mono text-gray-600">
                                            {item.shares_held != null ? item.shares_held.toLocaleString() : '-'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                            {item.latest_submit_date ? new Date(item.latest_submit_date).toLocaleDateString() : '-'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                                            <Link
                                                href={`/filer/${item.filer_id}`}
                                                className="text-blue-600 hover:text-blue-900 font-medium"
                                            >
                                                投資家詳細 &rarr;
                                            </Link>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
