import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../../App';
import { renderWithProviders, createMockFeatureFlagConfig, mockMarketData, mockPredictions } from '../utils';

// Mock the services
vi.mock('../../services/marketDataService', () => ({
  marketDataService: {
    initialize: vi.fn().mockResolvedValue(undefined),
    subscribe: vi.fn().mockReturnValue(() => { }),
    getCandlestickData: vi.fn().mockResolvedValue([]),
    getTechnicalIndicators: vi.fn().mockResolvedValue({}),
    getNews: vi.fn().mockResolvedValue([]),
  },
}));

vi.mock('../../services/aiPredictionService', () => ({
  aiPredictionService: {
    initialize: vi.fn().mockResolvedValue(undefined),
    subscribeToPredictions: vi.fn().mockReturnValue(() => { }),
    subscribeToTraining: vi.fn().mockReturnValue(() => { }),
    getIsTraining: vi.fn().mockReturnValue(false),
    startTraining: vi.fn(),
    stopTraining: vi.fn(),
  },
}));

describe('Feature Flag Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('Navigation Integration', () => {
    it('should show only enabled navigation items', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: true, category: 'ai' },
          'portfolio-management': { id: 'portfolio-management', name: 'Portfolio Management', enabled: false, category: 'trading' },
          'training-dashboard': { id: 'training-dashboard', name: 'Training Dashboard', enabled: true, category: 'ai' },
          'news-feed': { id: 'news-feed', name: 'News Feed', enabled: false, category: 'analytics' },
          'real-time-charts': { id: 'real-time-charts', name: 'Real-time Charts', enabled: true, category: 'ui' },
        },
      });

      renderWithProviders(<App />, { featureFlags: config });

      // Should show enabled features
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('AI Training')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();

      // Should not show disabled features
      expect(screen.queryByText('Portfolio')).not.toBeInTheDocument();
      expect(screen.queryByText('News')).not.toBeInTheDocument();
    });

    it('should show enhanced crypto when charts are enabled', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'real-time-charts': { id: 'real-time-charts', name: 'Real-time Charts', enabled: true, category: 'ui' },
        },
      });

      renderWithProviders(<App />, { featureFlags: config });

      expect(screen.getByText('Enhanced Crypto')).toBeInTheDocument();
    });

    it('should hide enhanced crypto when no charts are enabled', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'real-time-charts': { id: 'real-time-charts', name: 'Real-time Charts', enabled: false, category: 'ui' },
          'advanced-charts': { id: 'advanced-charts', name: 'Advanced Charts', enabled: false, category: 'ui' },
        },
      });

      renderWithProviders(<App />, { featureFlags: config });

      expect(screen.queryByText('Enhanced Crypto')).not.toBeInTheDocument();
    });
  });

  describe('Component Rendering Integration', () => {
    it('should render components based on feature flags in dashboard view', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: true, category: 'ai' },
          'real-time-charts': { id: 'real-time-charts', name: 'Real-time Charts', enabled: true, category: 'ui' },
          'market-sentiment': { id: 'market-sentiment', name: 'Market Sentiment', enabled: true, category: 'analytics' },
        },
      });

      renderWithProviders(<App />, { featureFlags: config });

      // Should render enabled components
      expect(screen.getByText('AI Predictions')).toBeInTheDocument();
      expect(screen.getByText('Assets')).toBeInTheDocument();
    });

    it('should show disabled states for disabled features', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: false, category: 'ai' },
          'real-time-charts': { id: 'real-time-charts', name: 'Real-time Charts', enabled: false, category: 'ui' },
        },
      });

      renderWithProviders(<App />, { featureFlags: config });

      expect(screen.getByText('AI Predictions Disabled')).toBeInTheDocument();
    });
  });

  describe('Feature Flag Manager Integration', () => {
    it('should open feature flag manager when settings button is clicked', () => {
      const config = createMockFeatureFlagConfig();

      renderWithProviders(<App />, { featureFlags: config });

      // Click the settings button (should be in the bottom right)
      const settingsButton = screen.getByTitle('Feature Flags');
      fireEvent.click(settingsButton);

      expect(screen.getByText('Feature Flags')).toBeInTheDocument();
      expect(screen.getByText('Environment: test | Groups: default')).toBeInTheDocument();
    });

    it('should allow toggling feature flags in the manager', async () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: true, category: 'ai' },
        },
      });

      renderWithProviders(<App />, { featureFlags: config });

      // Open feature flag manager
      const settingsButton = screen.getByTitle('Feature Flags');
      fireEvent.click(settingsButton);

      // Find the toggle for AI predictions
      const toggle = screen.getByRole('checkbox', { name: /ai predictions/i });
      expect(toggle).toBeChecked();

      // Toggle it off
      fireEvent.click(toggle);

      await waitFor(() => {
        expect(toggle).not.toBeChecked();
      });
    });

    it('should filter features by category', () => {
      const config = createMockFeatureFlagConfig();

      renderWithProviders(<App />, { featureFlags: config });

      // Open feature flag manager
      const settingsButton = screen.getByTitle('Feature Flags');
      fireEvent.click(settingsButton);

      // Filter by AI category
      const categoryFilter = screen.getByDisplayValue('All Categories');
      fireEvent.change(categoryFilter, { target: { value: 'ai' } });

      // Should only show AI features
      expect(screen.getByText('AI Predictions')).toBeInTheDocument();
      expect(screen.getByText('Training Dashboard')).toBeInTheDocument();
      expect(screen.getByText('AI Optimization')).toBeInTheDocument();
    });

    it('should search features by name', () => {
      const config = createMockFeatureFlagConfig();

      renderWithProviders(<App />, { featureFlags: config });

      // Open feature flag manager
      const settingsButton = screen.getByTitle('Feature Flags');
      fireEvent.click(settingsButton);

      // Search for portfolio
      const searchInput = screen.getByPlaceholderText('Search features...');
      fireEvent.change(searchInput, { target: { value: 'portfolio' } });

      // Should only show portfolio-related features
      expect(screen.getByText('Portfolio Management')).toBeInTheDocument();
    });
  });

  describe('Feature Dependencies Integration', () => {
    it('should handle feature dependencies correctly', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'portfolio-management': { id: 'portfolio-management', name: 'Portfolio Management', enabled: true, category: 'trading' },
          'backtesting': { id: 'backtesting', name: 'Backtesting', enabled: true, category: 'trading', dependencies: ['portfolio-management'] },
        },
      });

      renderWithProviders(<App />, { featureFlags: config });

      // Both features should be enabled since dependency is met
      expect(screen.getByText('Portfolio Management')).toBeInTheDocument();
    });

    it('should disable dependent features when dependency is missing', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'portfolio-management': { id: 'portfolio-management', name: 'Portfolio Management', enabled: false, category: 'trading' },
          'backtesting': { id: 'backtesting', name: 'Backtesting', enabled: true, category: 'trading', dependencies: ['portfolio-management'] },
        },
      });

      renderWithProviders(<App />, { featureFlags: config });

      // Backtesting should be disabled due to missing dependency
      expect(screen.queryByText('Backtesting')).not.toBeInTheDocument();
    });
  });

  describe('Real-time Updates Integration', () => {
    it('should update UI when feature flags change', async () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: false, category: 'ai' },
        },
      });

      const { rerender } = renderWithProviders(<App />, { featureFlags: config });

      // Initially disabled
      expect(screen.getByText('AI Predictions Disabled')).toBeInTheDocument();

      // Update config to enable feature
      const updatedConfig = createMockFeatureFlagConfig({
        flags: {
          'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: true, category: 'ai' },
        },
      });

      rerender(<App />);

      // Should now show the enabled component
      await waitFor(() => {
        expect(screen.getByText('AI Predictions')).toBeInTheDocument();
      });
    });
  });

  describe('Persistence Integration', () => {
    it('should persist feature flag changes to localStorage', () => {
      const config = createMockFeatureFlagConfig();

      renderWithProviders(<App />, { featureFlags: config });

      // Open feature flag manager
      const settingsButton = screen.getByTitle('Feature Flags');
      fireEvent.click(settingsButton);

      // Toggle a feature
      const toggle = screen.getByRole('checkbox', { name: /ai predictions/i });
      fireEvent.click(toggle);

      // Check that it was saved to localStorage
      const savedFlags = JSON.parse(localStorage.getItem('feature-flags') || '{}');
      expect(savedFlags['ai-predictions'].enabled).toBe(false);
    });

    it('should load feature flags from localStorage on app start', () => {
      // Pre-populate localStorage
      const savedFlags = {
        'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: false, category: 'ai' },
      };
      localStorage.setItem('feature-flags', JSON.stringify(savedFlags));

      const config = createMockFeatureFlagConfig();

      renderWithProviders(<App />, { featureFlags: config });

      // Should show disabled state due to localStorage
      expect(screen.getByText('AI Predictions Disabled')).toBeInTheDocument();
    });
  });

  describe('Error Handling Integration', () => {
    it('should handle invalid feature flag data gracefully', () => {
      // Set invalid JSON in localStorage
      localStorage.setItem('feature-flags', 'invalid-json');

      const config = createMockFeatureFlagConfig();

      renderWithProviders(<App />, { featureFlags: config });

      // Should still render the app with default flags
      expect(screen.getByText('Bolt AI Crypto')).toBeInTheDocument();
    });

    it('should handle missing feature flags gracefully', () => {
      const config = createMockFeatureFlagConfig({
        flags: {},
      });

      renderWithProviders(<App />, { featureFlags: config });

      // Should still render the app
      expect(screen.getByText('Bolt AI Crypto')).toBeInTheDocument();
    });
  });
});