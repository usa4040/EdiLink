"use client";

import { useState } from "react";
import { api, Issuer, PaginatedResponse } from "@/lib/api";
import { useDebounce } from "./useDebounce";
import { useAsyncData } from "./useAsyncData";

const ITEMS_PER_PAGE = 50;

type SetState<T> = React.Dispatch<React.SetStateAction<T>>;

interface UseFilerIssuersResult {
  issuers: Issuer[];
  loading: boolean;
  error: string | null;
  currentPage: number;
  setCurrentPage: SetState<number>;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  totalCount: number;
  totalPages: number;
  refetch: () => void;
}

/**
 * 提出者の保有銘柄一覧を取得するカスタムフック
 * @param filerId 提出者ID
 * @param initialPage 初期ページ（デフォルト: 1）
 * @param initialSearch 初期検索クエリ（デフォルト: 空文字）
 * @returns 保有銘柄一覧と関連状態
 */
export function useFilerIssuers(
  filerId: number | string | null,
  initialPage: number = 1,
  initialSearch: string = ""
): UseFilerIssuersResult {
  const numericId = typeof filerId === "string" ? parseInt(filerId, 10) : filerId;
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [searchQuery, setSearchQuery] = useState(initialSearch);
  const debouncedSearch = useDebounce(searchQuery, 300);

  const { data, loading, error, refetch } = useAsyncData<
    PaginatedResponse<Issuer>
  >(
    async () => {
      if (numericId === null || isNaN(numericId)) {
        throw new Error("有効なIDを指定してください");
      }
      const skip = (currentPage - 1) * ITEMS_PER_PAGE;
      return api.getIssuersByFiler(
        numericId,
        skip,
        ITEMS_PER_PAGE,
        debouncedSearch || undefined
      );
    },
    [numericId, currentPage, debouncedSearch],
    { enabled: numericId !== null && !isNaN(numericId) }
  );

  // 検索クエリが変更されたらページをリセット
  const handleSetSearchQuery = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
  };

  const totalCount = data?.total ?? 0;
  const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE);
  const issuers = data?.items ?? [];

  return {
    issuers,
    loading,
    error,
    currentPage,
    setCurrentPage,
    searchQuery,
    setSearchQuery: handleSetSearchQuery,
    totalCount,
    totalPages,
    refetch,
  };
}
