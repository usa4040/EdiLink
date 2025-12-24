"use client";

import { ReactNode } from "react";
import { SidebarProvider } from "../context/SidebarContext";
import { Sidebar } from "./Sidebar";
import { MainContent } from "./MainContent";

export function ClientLayout({ children }: { children: ReactNode }) {
    return (
        <SidebarProvider>
            <div className="min-h-screen bg-white flex">
                <Sidebar />
                <MainContent>{children}</MainContent>
            </div>
        </SidebarProvider>
    );
}
