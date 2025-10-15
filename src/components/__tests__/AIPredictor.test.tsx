import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AIPredictor } from '../AIPredictor';
import { renderWithProviders, createMockPredictionData, createMockFeatureFlagConfig } from '../../test/utils';

describe('AIPredictor', () => {
  const mockPredictions = {
    BTC: createMockPredictionData({ symbol: 'BTC', prediction: 'BULL', confidence: 0.85 }),
    ETH: createMockPredictionData({ symbol: 'ETH', prediction: 'BEAR', confidence: 0.72 }),
    SOL: createMockPredictionData({ symbol: 'SOL', prediction: 'NEUTRAL', confidence: 0.45 }),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render AI predictions when feature is enabled', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: true, category: 'ai' },
      },
    });

    renderWithProviders(
      <AIPredictor predictions={mockPredictions} />,
      { featureFlags: config }
    );

    expect(screen.getByText('AI Predictions')).toBeInTheDocument();
    expect(screen.getByText('BULL')).toBeInTheDocument();
    expect(screen.getByText('85.0% Confidence')).toBeInTheDocument();
  });

  it('should render disabled state when feature is disabled', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: false, category: 'ai' },
      },
    });

    renderWithProviders(
      <AIPredictor predictions={mockPredictions} />,
      { featureFlags: config }
    );

    expect(screen.getByText('AI Predictions Disabled')).toBeInTheDocument();
    expect(screen.getByText('This feature is currently disabled. Enable it in the feature flags to access AI-powered predictions.')).toBeInTheDocument();
  });

  it('should show optimization badge when AI optimization is enabled', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: true, category: 'ai' },
        'ai-optimization': { id: 'ai-optimization', name: 'AI Optimization', enabled: true, category: 'ai' },
      },
    });

    renderWithProviders(
      <AIPredictor predictions={mockPredictions} />,
      { featureFlags: config }
    );

    expect(screen.getByText('Optimized')).toBeInTheDocument();
  });

  it('should allow symbol selection', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: true, category: 'ai' },
      },
    });

    renderWithProviders(
      <AIPredictor predictions={mockPredictions} />,
      { featureFlags: config }
    );

    const select = screen.getByDisplayValue('BTC');
    expect(select).toBeInTheDocument();

    fireEvent.change(select, { target: { value: 'ETH' } });
    expect(screen.getByText('BEAR')).toBeInTheDocument();
    expect(screen.getByText('72.0% Confidence')).toBeInTheDocument();
  });

  it('should display probability distribution', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: true, category: 'ai' },
      },
    });

    renderWithProviders(
      <AIPredictor predictions={mockPredictions} />,
      { featureFlags: config }
    );

    expect(screen.getByText('Probability Distribution')).toBeInTheDocument();
    expect(screen.getByText('Bullish')).toBeInTheDocument();
    expect(screen.getByText('Bearish')).toBeInTheDocument();
    expect(screen.getByText('Neutral')).toBeInTheDocument();
  });

  it('should display risk assessment', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: true, category: 'ai' },
      },
    });

    renderWithProviders(
      <AIPredictor predictions={mockPredictions} />,
      { featureFlags: config }
    );

    expect(screen.getByText('Risk Assessment')).toBeInTheDocument();
    expect(screen.getByText('30.0%')).toBeInTheDocument();
  });

  it('should display trading signal', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: true, category: 'ai' },
      },
    });

    renderWithProviders(
      <AIPredictor predictions={mockPredictions} />,
      { featureFlags: config }
    );

    expect(screen.getByText('Trading Signal')).toBeInTheDocument();
    expect(screen.getByText('LONG')).toBeInTheDocument();
  });

  it('should show waiting state when no predictions available', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: true, category: 'ai' },
      },
    });

    renderWithProviders(
      <AIPredictor predictions={{}} />,
      { featureFlags: config }
    );

    expect(screen.getByText('Waiting for AI predictions...')).toBeInTheDocument();
  });

  it('should handle different prediction types correctly', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: true, category: 'ai' },
      },
    });

    const bearPredictions = {
      BTC: createMockPredictionData({ symbol: 'BTC', prediction: 'BEAR', confidence: 0.8 }),
    };

    renderWithProviders(
      <AIPredictor predictions={bearPredictions} />,
      { featureFlags: config }
    );

    expect(screen.getByText('BEAR')).toBeInTheDocument();
    expect(screen.getByText('SHORT')).toBeInTheDocument();
  });

  it('should handle neutral predictions correctly', () => {
    const config = createMockFeatureFlagConfig({
      flags: {
        'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: true, category: 'ai' },
      },
    });

    const neutralPredictions = {
      BTC: createMockPredictionData({ symbol: 'BTC', prediction: 'NEUTRAL', confidence: 0.5 }),
    };

    renderWithProviders(
      <AIPredictor predictions={neutralPredictions} />,
      { featureFlags: config }
    );

    expect(screen.getByText('NEUTRAL')).toBeInTheDocument();
    expect(screen.getByText('HOLD')).toBeInTheDocument();
  });
});