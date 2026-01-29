"use client";

import Link from "next/link";

export default function FeaturedFilersPage() {
    return (
        <div>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6 sm:mb-8">
                <div>
                    <h1 className="text-xl sm:text-2xl font-bold text-gray-900">注目の提出者</h1>
                    <p className="text-sm sm:text-base text-gray-500 mt-1">
                        市場で影響力を持つ主要な投資家リスト
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <Link
                    href="/filer/1"
                    className="group flex flex-col h-full p-5 bg-linear-to-br from-indigo-50 to-white hover:from-white hover:to-indigo-50 border border-indigo-100 hover:border-indigo-300 rounded-xl shadow-sm hover:shadow-md transition-all"
                >
                    <div className="flex items-center gap-4 mb-3">
                        <div className="w-12 h-12 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xl shadow-lg shadow-indigo-200 group-hover:scale-110 transition-transform">
                            光
                        </div>
                        <div>
                            <h3 className="font-bold text-gray-900 text-lg">株式会社光通信</h3>
                            <p className="text-xs text-gray-500">E04948 / 94350</p>
                        </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">
                        純投資・アクティビスト活動で知られる主要投資家。最新の保有銘柄と動向をチェックできます。
                    </p>
                    <div className="mt-auto flex items-center text-indigo-600 text-sm font-medium group-hover:translate-x-1 transition-transform">
                        ダッシュボードを見る
                        <svg
                            className="w-4 h-4 ml-1"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M17 8l4 4m0 0l-4 4m4-4H3"
                            />
                        </svg>
                    </div>
                </Link>
                <Link
                    href="/filer/5557"
                    className="group flex flex-col h-full p-5 bg-linear-to-br from-indigo-50 to-white hover:from-white hover:to-indigo-50 border border-indigo-100 hover:border-indigo-300 rounded-xl shadow-sm hover:shadow-md transition-all"
                >
                    <div className="flex items-center gap-4 mb-3">
                        <div className="w-12 h-12 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xl shadow-lg shadow-indigo-200 group-hover:scale-110 transition-transform">
                            F
                        </div>
                        <div>
                            <h3 className="font-bold text-gray-900 text-lg">Fundnote株式会社</h3>
                            <p className="text-xs text-gray-500">E40155</p>
                        </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">
                        積極的な投資活動を行う機関投資家。
                    </p>
                    <div className="mt-auto flex items-center text-indigo-600 text-sm font-medium group-hover:translate-x-1 transition-transform">
                        ダッシュボードを見る
                        <svg
                            className="w-4 h-4 ml-1"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M17 8l4 4m0 0l-4 4m4-4H3"
                            />
                        </svg>
                    </div>
                </Link>
            </div>
        </div>
    );
}
