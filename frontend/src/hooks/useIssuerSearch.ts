"use client";

import { useState, useCallback } from "react";
import { api, Issuer } from "@/lib/api";
import { useAsyncData } from "./useAsyncData";

interface UseIssuerSearchResult {
  issuers: Issuer[];
  loading: boolean;
  error: string | null;
  search: string;
  setSearch: (query: string) => void;
  executeSearch: () => void;
  totalCount: number;
}

/**
 * 銘柄検索（逆引き）用のカスタムフック
 * @param initialSearch 初期検索クエリ
 * @returns 検索結果と関連状態
 */
export function useIssuerSearch(initialSearch: string = ""): UseIssuerSearchResult {
  const [search, setSearch] = useState(initialSearch);
  const [executeSearchTrigger, setExecuteSearchTrigger] = useState(0);

  const { data, loading, error } = useAsyncData<Issuer[]>(
    async () => {
      if (!search.trim()) {
        return [];
      }
      return api.searchIssuers(search, 20);
    },
    [search, executeSearchTrigger],
    { enabled: executeSearchTrigger > 0 || !!initialSearch }
  );

  const executeSearch = useCallback(() => {
    setExecuteSearchTrigger((prev) => prev + 1);
  }, []);

  const issuers = data ?? [];
  const totalCount = issuers.length;

  return {
    issuers,
    loading,
    error,
    search,
    setSearch,
    executeSearch,
    totalCount,
  };
}
