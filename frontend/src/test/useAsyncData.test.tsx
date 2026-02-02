import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useAsyncData } from '@/hooks/useAsyncData';

describe('useAsyncData', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch data on mount', async () => {
    const mockData = { id: 1, name: 'Test' };
    const fetcher = vi.fn().mockResolvedValue(mockData);

    const { result } = renderHook(() => useAsyncData(fetcher, []));

    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBeNull();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it('should not fetch when enabled is false', async () => {
    const fetcher = vi.fn().mockResolvedValue({});

    const { result } = renderHook(() =>
      useAsyncData(fetcher, [], { enabled: false })
    );

    expect(result.current.loading).toBe(false);
    expect(fetcher).not.toHaveBeenCalled();
  });

  it('should handle errors', async () => {
    const fetcher = vi.fn().mockRejectedValue(new Error('Fetch failed'));

    const { result } = renderHook(() => useAsyncData(fetcher, []));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Fetch failed');
    expect(result.current.data).toBeNull();
  });

  it('should refetch when refetch is called', async () => {
    const mockData = { count: 1 };
    const fetcher = vi.fn().mockResolvedValue(mockData);

    const { result } = renderHook(() => useAsyncData(fetcher, []));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(fetcher).toHaveBeenCalledTimes(1);

    result.current.refetch();

    await waitFor(() => {
      expect(fetcher).toHaveBeenCalledTimes(2);
    });
  });
});
