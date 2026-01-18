"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface SidebarContextType {
    isCollapsed: boolean;
    toggleCollapse: () => void;
}

const SidebarContext = createContext<SidebarContextType | undefined>(undefined);

export function SidebarProvider({ children }: { children: ReactNode }) {
    const [isCollapsed, setIsCollapsed] = useState(false);

    // ローカルストレージから折りたたみ状態を復元
    useEffect(() => {
        const saved = localStorage.getItem("sidebarCollapsed");
        if (saved === "true") {
            // Hydration mismatchを防ぐため初期値はfalseにし、マウント後に非同期で更新
            setTimeout(() => setIsCollapsed(true), 0);
        }
    }, []);

    // 折りたたみ状態を保存
    const toggleCollapse = () => {
        const newState = !isCollapsed;
        setIsCollapsed(newState);
        localStorage.setItem("sidebarCollapsed", String(newState));
    };

    return (
        <SidebarContext.Provider value={{ isCollapsed, toggleCollapse }}>
            {children}
        </SidebarContext.Provider>
    );
}

export function useSidebar() {
    const context = useContext(SidebarContext);
    if (context === undefined) {
        throw new Error("useSidebar must be used within a SidebarProvider");
    }
    return context;
}

