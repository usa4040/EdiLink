"use client";

import { api, IssuerOwnershipResponse } from "@/lib/api";
import { useAsyncData } from "./useAsyncData";

interface UseIssuerOwnershipsResult {
  data: IssuerOwnershipResponse | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * 銘柄の保有投資家一覧を取得するカスタムフック
 * @param issuerId 銘柄ID
 * @returns 保有投資家データと関連状態
 */
export function useIssuerOwnerships(
  issuerId: number | string | null
): UseIssuerOwnershipsResult {
  const numericId =
    typeof issuerId === "string" ? parseInt(issuerId, 10) : issuerId;

  const { data, loading, error, refetch } = useAsyncData<IssuerOwnershipResponse>(
    async () => {
      if (numericId === null || isNaN(numericId)) {
        throw new Error("有効なIDを指定してください");
      }
      return api.getIssuerOwnerships(numericId);
    },
    [numericId],
    { enabled: numericId !== null && !isNaN(numericId) }
  );

  // 404エラーの場合は親切なメッセージに変更
  const displayError = error
    ? error.includes("404")
      ? "銘柄が見つかりませんでした"
      : error
    : null;

  return {
    data: data ?? null,
    loading,
    error: displayError,
    refetch,
  };
}
