"use client";

import { api, Filer } from "@/lib/api";
import { useAsyncData } from "./useAsyncData";

interface UseFilerResult {
  filer: Filer | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * 提出者詳細を取得するカスタムフック
 * @param filerId 提出者ID
 * @returns 提出者詳細と関連状態
 */
export function useFiler(filerId: number | string | null): UseFilerResult {
  const numericId = typeof filerId === "string" ? parseInt(filerId, 10) : filerId;

  const { data, loading, error, refetch } = useAsyncData<Filer>(
    async () => {
      if (numericId === null || isNaN(numericId)) {
        throw new Error("有効なIDを指定してください");
      }
      return api.getFiler(numericId);
    },
    [numericId],
    { enabled: numericId !== null && !isNaN(numericId) }
  );

  return {
    filer: data ?? null,
    loading,
    error,
    refetch,
  };
}
