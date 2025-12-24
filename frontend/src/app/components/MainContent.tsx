"use client";

import { useSidebar } from "../context/SidebarContext";
import { ReactNode } from "react";

export function MainContent({ children }: { children: ReactNode }) {
    const { isCollapsed } = useSidebar();

    return (
        <main
            className={`flex-1 w-full transition-all duration-300 ${isCollapsed ? "lg:ml-16" : "lg:ml-64"}`}
        >
            <div className="p-4 sm:p-6 lg:p-8">
                {children}
            </div>
        </main>
    );
}
