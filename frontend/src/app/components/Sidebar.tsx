"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSidebar } from "../context/SidebarContext";

export function Sidebar() {
    const [isMobileOpen, setIsMobileOpen] = useState(false);
    const { isCollapsed, toggleCollapse } = useSidebar();
    const pathname = usePathname();

    // パス変更時にモバイルサイドバーを閉じる
    useEffect(() => {
        if (isMobileOpen) {
            setIsMobileOpen(false);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [pathname]);

    // 画面リサイズ時の処理
    useEffect(() => {
        const handleResize = () => {
            if (window.innerWidth >= 1024) {
                setIsMobileOpen(false);
            }
        };
        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, []);

    // オーバーレイクリック時にサイドバーを閉じる
    const handleOverlayClick = () => {
        setIsMobileOpen(false);
    };

    return (
        <>
            {/* モバイルヘッダー (lg未満で表示) */}
            <header className="lg:hidden fixed top-0 left-0 right-0 z-40 bg-white border-b border-gray-200 px-4 py-3">
                <div className="flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                        </div>
                        <span className="text-base font-bold text-indigo-600">EDINET Viewer</span>
                    </Link>
                    <button
                        onClick={() => setIsMobileOpen(!isMobileOpen)}
                        className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
                        aria-label="メニューを開く"
                    >
                        {isMobileOpen ? (
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        ) : (
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        )}
                    </button>
                </div>
            </header>

            {/* モバイル用スペーサー */}
            <div className="lg:hidden h-14" />

            {/* オーバーレイ (モバイル時のみ) */}
            {isMobileOpen && (
                <div
                    className="lg:hidden fixed inset-0 z-40 bg-black/50 transition-opacity"
                    onClick={handleOverlayClick}
                />
            )}

            {/* サイドバー */}
            <aside
                className={`
                    fixed top-0 left-0 z-50 h-full bg-[#f8f9fc] border-r border-gray-200
                    transform transition-all duration-300 ease-in-out
                    ${isMobileOpen ? "translate-x-0 w-64" : "-translate-x-full w-64"}
                    lg:translate-x-0
                    ${isCollapsed ? "lg:w-16" : "lg:w-64"}
                `}
            >
                <div className={`p-4 pt-4 lg:pt-6 ${isCollapsed ? "lg:p-2 lg:pt-6" : "lg:p-6"}`}>
                    {/* ロゴ */}
                    <Link href="/" className={`flex items-center gap-3 mb-8 ${isCollapsed ? "lg:justify-center" : ""}`}>
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shrink-0">
                            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                        </div>
                        <span className={`text-lg font-bold text-indigo-600 whitespace-nowrap transition-opacity ${isCollapsed ? "lg:hidden" : ""}`}>
                            EDINET Viewer
                        </span>
                    </Link>

                    {/* ナビゲーション */}
                    <nav className="space-y-2">
                        <Link
                            href="/"
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${isCollapsed ? "lg:justify-center lg:px-2" : ""} ${pathname === "/"
                                ? "bg-indigo-50 text-indigo-600"
                                : "text-gray-600 hover:bg-gray-100"
                                }`}
                            title="ダッシュボード"
                        >
                            <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                            <span className={`whitespace-nowrap ${isCollapsed ? "lg:hidden" : ""}`}>ダッシュボード</span>
                        </Link>
                    </nav>
                </div>

                {/* 折りたたみボタン（デスクトップのみ） */}
                <button
                    onClick={toggleCollapse}
                    className="hidden lg:flex absolute bottom-6 left-1/2 -translate-x-1/2 w-8 h-8 items-center justify-center rounded-full bg-white border border-gray-200 shadow-sm hover:bg-gray-50 transition-colors"
                    title={isCollapsed ? "サイドバーを展開" : "サイドバーを折りたたむ"}
                >
                    <svg
                        className={`w-4 h-4 text-gray-500 transition-transform ${isCollapsed ? "rotate-180" : ""}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                </button>
            </aside>
        </>
    );
}


