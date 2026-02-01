/**
 * APIクライアント - バックエンドAPIとの通信を抽象化
 */

// APIベースURL（環境変数から取得、デフォルトはlocalhost）
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// エラークラス
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// 型定義
export interface Filer {
  id: number;
  edinet_code: string;
  name: string;
  sec_code: string | null;
  filing_count: number;
  issuer_count: number;
  latest_filing_date: string | null;
}

export interface Issuer {
  id: number;
  edinet_code: string;
  name: string | null;
  sec_code: string | null;
  latest_filing_date: string | null;
  latest_ratio: number | null;
  latest_purpose: string | null;
  ratio_change: number | null;
  filing_count: number | null;
}

export interface FilingHistoryItem {
  doc_id: string;
  submit_date: string | null;
  doc_description: string | null;
  shares_held: number | null;
  holding_ratio: number | null;
  ratio_change: number | null;
}

export interface IssuerHistoryResponse {
  issuer: Issuer;
  filer: Filer;
  history: FilingHistoryItem[];
}

export interface IssuerOwnershipResponse {
  issuer: Issuer;
  ownerships: Array<{
    filer_id: number;
    filer_name: string;
    latest_submit_date: string | null;
    shares_held: number | null;
    holding_ratio: number | null;
    purpose: string | null;
  }>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

// APIクライアントクラス
class ApiClient {
  private async fetch<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
      },
      ...options,
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => "Unknown error");
      throw new ApiError(
        response.status,
        `API request failed: ${response.status} ${response.statusText} - ${errorText}`
      );
    }

    return response.json();
  }

  private buildQueryString(params: Record<string, string | number | undefined>): string {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        searchParams.append(key, String(value));
      }
    });
    const queryString = searchParams.toString();
    return queryString ? `?${queryString}` : "";
  }

  // === Filers ===
  async getFilers(
    skip: number = 0,
    limit: number = 50,
    search?: string
  ): Promise<PaginatedResponse<Filer>> {
    const query = this.buildQueryString({ skip, limit, search });
    return this.fetch<PaginatedResponse<Filer>>(`/api/filers${query}`);
  }

  async getFiler(id: number): Promise<Filer> {
    return this.fetch<Filer>(`/api/filers/${id}`);
  }

  // === Issuers ===
  async getIssuersByFiler(
    filerId: number,
    skip: number = 0,
    limit: number = 50,
    search?: string
  ): Promise<PaginatedResponse<Issuer>> {
    const query = this.buildQueryString({ skip, limit, search });
    return this.fetch<PaginatedResponse<Issuer>>(`/api/filers/${filerId}/issuers${query}`);
  }

  async searchIssuers(query: string, limit: number = 20): Promise<Issuer[]> {
    const searchParams = this.buildQueryString({ search: query, limit });
    return this.fetch<Issuer[]>(`/api/issuers${searchParams}`);
  }

  async getIssuerOwnerships(id: number): Promise<IssuerOwnershipResponse> {
    return this.fetch<IssuerOwnershipResponse>(`/api/issuers/${id}/ownerships`);
  }

  // === History ===
  async getIssuerHistory(
    filerId: number,
    issuerId: number
  ): Promise<IssuerHistoryResponse> {
    return this.fetch<IssuerHistoryResponse>(
      `/api/filers/${filerId}/issuers/${issuerId}/history`
    );
  }
}

// シングルトンインスタンス
export const api = new ApiClient();
