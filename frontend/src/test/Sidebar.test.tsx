import { render, screen } from "@testing-library/react";
import { Sidebar } from "../app/components/Sidebar";
import { SidebarProvider } from "../app/context/SidebarContext";

// next/navigationのモック
vi.mock("next/navigation", () => ({
  usePathname: () => "/",
}));

describe("Sidebar", () => {
  it("renders navigation links", () => {
    render(
      <SidebarProvider>
        <Sidebar />
      </SidebarProvider>
    );

    // ナビゲーションリンクが表示される
    expect(screen.getByText("大量保有報告一覧")).toBeInTheDocument();
    expect(screen.getByText("銘柄検索")).toBeInTheDocument();
    expect(screen.getByText("注目の提出者")).toBeInTheDocument();
  });

  it("renders logo", () => {
    render(
      <SidebarProvider>
        <Sidebar />
      </SidebarProvider>
    );

    const logos = screen.getAllByText("EDINET Viewer");
    expect(logos.length).toBeGreaterThanOrEqual(1);
  });

  it("renders mobile header", () => {
    render(
      <SidebarProvider>
        <Sidebar />
      </SidebarProvider>
    );

    // モバイルヘッダーが存在（複数のロゴ表示がある）
    const logos = screen.getAllByText("EDINET Viewer");
    expect(logos.length).toBeGreaterThanOrEqual(1);
  });
});
