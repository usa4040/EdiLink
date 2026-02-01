'use client';

import { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams, useRouter } from 'next/navigation';
import { api, Issuer, PaginatedResponse } from "@/lib/api";

function IssuerSearchContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [data, setData] = useState<PaginatedResponse<Issuer> | null>(null);
    const [loading, setLoading] = useState(false);
    const [search, setSearch] = useState(searchParams.get('search') || '');

    const fetchData = async (query: string = '') => {
        setLoading(true);
        try {
            const json = await api.searchIssuers(query, 20);
            setData({ items: json, total: json.length, skip: 0, limit: 20 });
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // URLのクエリパラメータが変わったら再取得
        const query = searchParams.get('search') || '';
        fetchData(query);
        setSearch(query);
    }, [searchParams]);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        router.push(`/issuers?search=${encodeURIComponent(search)}`);
    };

    return (
        <div className="container mx-auto p-8">
            <h1 className="text-3xl font-bold mb-8 text-gray-800">銘柄検索 (逆引き)</h1>

            {/* 検索フォーム */}
            <form onSubmit={handleSearch} className="mb-8 flex gap-4">
                <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="銘柄名、証券コード、EDINETコード"
                    className="flex-1 p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                />
                <button
                    type="submit"
                    disabled={loading}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors shadow-sm font-medium disabled:opacity-50"
                >
                    {loading ? '検索中...' : '検索'}
                </button>
            </form>

            {/* 結果一覧 */}
            {data && (
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                    <div className="p-4 bg-gray-50 border-b border-gray-200">
                        <p className="text-gray-600">
                            検索結果: <span className="font-bold text-gray-900">{data.total}</span> 件
                        </p>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">EDINETコード</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">証券コード</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">銘柄名</th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">アクション</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {data.items.length === 0 ? (
                                    <tr>
                                        <td colSpan={4} className="px-6 py-12 text-center text-gray-500">
                                            該当する銘柄は見つかりませんでした
                                        </td>
                                    </tr>
                                ) : (
                                    data.items.map((issuer) => (
                                        <tr key={issuer.id} className="hover:bg-gray-50 transition-colors">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-600">
                                                {issuer.edinet_code}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-600">
                                                {issuer.sec_code || '-'}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {issuer.name}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                {/* 該当銘柄の詳細ページへのリンク（今回は仮としてボタンのみ配置） */}
                                                <Link
                                                    href={`/issuers/${issuer.id}`}
                                                    className="text-blue-600 hover:text-blue-900 bg-blue-50 px-3 py-1 rounded-md inline-block"
                                                >
                                                    詳細を見る
                                                </Link>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}

export default function IssuersPage() {
    return (
        <Suspense fallback={<div className="container mx-auto p-8 text-center text-gray-500">読み込み中...</div>}>
            <IssuerSearchContent />
        </Suspense>
    );
}
