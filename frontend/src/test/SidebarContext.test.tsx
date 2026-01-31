import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SidebarProvider, useSidebar } from '@/app/context/SidebarContext';
import userEvent from '@testing-library/user-event';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Test component that uses the context
function TestComponent() {
  const { isCollapsed, toggleCollapse } = useSidebar();
  return (
    <div>
      <span data-testid="collapsed">{isCollapsed ? 'true' : 'false'}</span>
      <button onClick={toggleCollapse}>Toggle</button>
    </div>
  );
}

describe('SidebarContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should provide default collapsed state', () => {
    localStorageMock.getItem.mockReturnValue(null);
    
    render(
      <SidebarProvider>
        <TestComponent />
      </SidebarProvider>
    );

    expect(screen.getByTestId('collapsed').textContent).toBe('false');
  });

  it('should toggle collapsed state', async () => {
    localStorageMock.getItem.mockReturnValue(null);
    const user = userEvent.setup();
    
    render(
      <SidebarProvider>
        <TestComponent />
      </SidebarProvider>
    );

    const button = screen.getByText('Toggle');
    await user.click(button);

    expect(screen.getByTestId('collapsed').textContent).toBe('true');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('sidebarCollapsed', 'true');
  });

  it('should throw error when used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    expect(() => {
      render(<TestComponent />);
    }).toThrow('useSidebar must be used within a SidebarProvider');
    
    consoleSpy.mockRestore();
  });
});
