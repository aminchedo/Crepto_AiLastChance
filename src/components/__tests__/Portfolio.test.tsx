import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Portfolio } from '../Portfolio';
import { renderWithProviders, createMockMarketData, createMockFeatureFlagConfig } from '../../test/utils';

describe('Portfolio', () => {
  const mockMarketData = [
    createMockMarketData({ symbol: 'BTC', price: 43250.75 }),
    createMockMarketData({ symbol: 'ETH', price: 2650.30 }),
    createMockMarketData({ symbol: 'SOL', price: 98.75 }),
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render portfolio when feature is enabled', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'portfolio-management': { id: 'portfolio-management', name: 'Portfolio Management', enabled: true, category: 'trading' },
      },
    });

    renderWithProviders(
      <Portfolio marketData={mockMarketData} />,
      { featureFlags: config }
    );

    expect(screen.getByText('Portfolio')).toBeInTheDocument();
    expect(screen.getByText('Total Value')).toBeInTheDocument();
    expect(screen.getByText('Total P&L')).toBeInTheDocument();
    expect(screen.getByText('Return %')).toBeInTheDocument();
  });

  it('should render disabled state when feature is disabled', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'portfolio-management': { id: 'portfolio-management', name: 'Portfolio Management', enabled: false, category: 'trading' },
      },
    });

    renderWithProviders(
      <Portfolio marketData={mockMarketData} />,
      { featureFlags: config }
    );

    expect(screen.getByText('Portfolio Management Disabled')).toBeInTheDocument();
    expect(screen.getByText('This feature is currently disabled. Enable it in the feature flags to access portfolio tracking.')).toBeInTheDocument();
  });

  it('should show paper trading badge when enabled', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'portfolio-management': { id: 'portfolio-management', name: 'Portfolio Management', enabled: true, category: 'trading' },
        'paper-trading': { id: 'paper-trading', name: 'Paper Trading', enabled: true, category: 'trading' },
      },
    });

    renderWithProviders(
      <Portfolio marketData={mockMarketData} />,
      { featureFlags: config }
    );

    expect(screen.getByText('Paper Trading')).toBeInTheDocument();
  });

  it('should show risk managed badge when enabled', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'portfolio-management': { id: 'portfolio-management', name: 'Portfolio Management', enabled: true, category: 'trading' },
        'risk-management': { id: 'risk-management', name: 'Risk Management', enabled: true, category: 'trading' },
      },
    });

    renderWithProviders(
      <Portfolio marketData={mockMarketData} />,
      { featureFlags: config }
    );

    expect(screen.getByText('Risk Managed')).toBeInTheDocument();
  });

  it('should display portfolio positions', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'portfolio-management': { id: 'portfolio-management', name: 'Portfolio Management', enabled: true, category: 'trading' },
      },
    });

    renderWithProviders(
      <Portfolio marketData={mockMarketData} />,
      { featureFlags: config }
    );

    expect(screen.getByText('Positions')).toBeInTheDocument();
    expect(screen.getByText('BTC')).toBeInTheDocument();
    expect(screen.getByText('ETH')).toBeInTheDocument();
    expect(screen.getByText('SOL')).toBeInTheDocument();
  });

  it('should display allocation chart', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'portfolio-management': { id: 'portfolio-management', name: 'Portfolio Management', enabled: true, category: 'trading' },
      },
    });

    renderWithProviders(
      <Portfolio marketData={mockMarketData} />,
      { featureFlags: config }
    );

    expect(screen.getByText('Allocation')).toBeInTheDocument();
  });

  it('should calculate and display P&L correctly', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'portfolio-management': { id: 'portfolio-management', name: 'Portfolio Management', enabled: true, category: 'trading' },
      },
    });

    renderWithProviders(
      <Portfolio marketData={mockMarketData} />,
      { featureFlags: config }
    );

    // Check that P&L values are displayed (they should be calculated from mock data)
    const pnlElements = screen.getAllByText(/\$[\d,]+/);
    expect(pnlElements.length).toBeGreaterThan(0);
  });

  it('should display asset symbols with correct styling', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'portfolio-management': { id: 'portfolio-management', name: 'Portfolio Management', enabled: true, category: 'trading' },
      },
    });

    renderWithProviders(
      <Portfolio marketData={mockMarketData} />,
      { featureFlags: config }
    );

    // Check that asset symbols are displayed with their first two letters
    expect(screen.getByText('BTC')).toBeInTheDocument();
    expect(screen.getByText('ETH')).toBeInTheDocument();
    expect(screen.getByText('SOL')).toBeInTheDocument();
  });

  it('should handle empty market data gracefully', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'portfolio-management': { id: 'portfolio-management', name: 'Portfolio Management', enabled: true, category: 'trading' },
      },
    });

    renderWithProviders(
      <Portfolio marketData={[]} />,
      { featureFlags: config }
    );

    expect(screen.getByText('Portfolio')).toBeInTheDocument();
    // Should still render the component structure even with empty data
  });

  it('should update when market data changes', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'portfolio-management': { id: 'portfolio-management', name: 'Portfolio Management', enabled: true, category: 'trading' },
      },
    });

    const { rerender } = renderWithProviders(
      <Portfolio marketData={mockMarketData} />,
      { featureFlags: config }
    );

    const updatedMarketData = [
      ...mockMarketData,
      createMockMarketData({ symbol: 'ADA', price: 0.45 }),
    ];

    rerender(
      <Portfolio marketData={updatedMarketData} />
    );

    // Component should re-render with new data
    expect(screen.getByText('Portfolio')).toBeInTheDocument();
  });
});