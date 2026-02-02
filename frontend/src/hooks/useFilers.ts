"use client";

import { useState } from "react";
import { api, Filer, PaginatedResponse } from "@/lib/api";
import { useDebounce } from "./useDebounce";
import { useAsyncData } from "./useAsyncData";

const ITEMS_PER_PAGE = 50;

type SetState<T> = React.Dispatch<React.SetStateAction<T>>;

interface UseFilersResult {
  filers: Filer[];
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
 * 提出者一覧を取得するカスタムフック
 * @param initialPage 初期ページ（デフォルト: 1）
 * @param initialSearch 初期検索クエリ（デフォルト: 空文字）
 * @returns 提出者一覧と関連状態
 */
export function useFilers(
  initialPage: number = 1,
  initialSearch: string = ""
): UseFilersResult {
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [searchQuery, setSearchQuery] = useState(initialSearch);
  const debouncedSearch = useDebounce(searchQuery, 300);

  const { data, loading, error, refetch } = useAsyncData<
    PaginatedResponse<Filer>
  >(
    async () => {
      const skip = (currentPage - 1) * ITEMS_PER_PAGE;
      return api.getFilers(skip, ITEMS_PER_PAGE, debouncedSearch || undefined);
    },
    [currentPage, debouncedSearch]
  );

  // 検索クエリが変更されたらページをリセット
  const handleSetSearchQuery = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
  };

  const totalCount = data?.total ?? 0;
  const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE);
  const filers = data?.items ?? [];

  return {
    filers,
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
