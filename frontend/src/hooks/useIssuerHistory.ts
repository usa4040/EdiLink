"use client";

import { api, IssuerHistoryResponse } from "@/lib/api";
import { useAsyncData } from "./useAsyncData";

interface UseIssuerHistoryResult {
  data: IssuerHistoryResponse | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * 銘柄の報告書履歴を取得するカスタムフック
 * @param filerId 提出者ID
 * @param issuerId 銘柄ID
 * @returns 履歴データと関連状態
 */
export function useIssuerHistory(
  filerId: number | string | null,
  issuerId: number | string | null
): UseIssuerHistoryResult {
  const numericFilerId =
    typeof filerId === "string" ? parseInt(filerId, 10) : filerId;
  const numericIssuerId =
    typeof issuerId === "string" ? parseInt(issuerId, 10) : issuerId;

  const { data, loading, error, refetch } = useAsyncData<IssuerHistoryResponse>(
    async () => {
      if (
        numericFilerId === null ||
        isNaN(numericFilerId) ||
        numericIssuerId === null ||
        isNaN(numericIssuerId)
      ) {
        throw new Error("有効なIDを指定してください");
      }
      return api.getIssuerHistory(numericFilerId, numericIssuerId);
    },
    [numericFilerId, numericIssuerId],
    {
      enabled:
        numericFilerId !== null &&
        !isNaN(numericFilerId) &&
        numericIssuerId !== null &&
        !isNaN(numericIssuerId),
    }
  );

  return {
    data: data ?? null,
    loading,
    error,
    refetch,
  };
}
