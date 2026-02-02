import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useFilers } from '@/hooks/useFilers';
import { api } from '@/lib/api';

// APIのモック
vi.mock('@/lib/api', () => ({
  api: {
    getFilers: vi.fn(),
  },
}));

describe('useFilers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch filers on mount', async () => {
    const mockFilers = {
      items: [
        { id: 1, name: 'Test Filer 1', edinet_code: 'E001', sec_code: '1234', filing_count: 5, issuer_count: 3, latest_filing_date: '2024-01-01' },
        { id: 2, name: 'Test Filer 2', edinet_code: 'E002', sec_code: '5678', filing_count: 3, issuer_count: 2, latest_filing_date: '2024-01-02' },
      ],
      total: 2,
      skip: 0,
      limit: 50,
    };

    (api.getFilers as ReturnType<typeof vi.fn>).mockResolvedValue(mockFilers);

    const { result } = renderHook(() => useFilers());

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.filers).toEqual(mockFilers.items);
    expect(result.current.totalCount).toBe(2);
    expect(api.getFilers).toHaveBeenCalledWith(0, 50, undefined);
  });

  it('should handle search query', async () => {
    const mockFilers = {
      items: [{ id: 1, name: 'Test', edinet_code: 'E001', sec_code: null, filing_count: 1, issuer_count: 1, latest_filing_date: null }],
      total: 1,
      skip: 0,
      limit: 50,
    };

    (api.getFilers as ReturnType<typeof vi.fn>).mockResolvedValue(mockFilers);

    const { result } = renderHook(() => useFilers());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    result.current.setSearchQuery('test');

    await waitFor(() => {
      expect(api.getFilers).toHaveBeenCalledWith(0, 50, 'test');
    });
  });

  it('should handle error', async () => {
    (api.getFilers as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useFilers());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Network error');
  });
});
