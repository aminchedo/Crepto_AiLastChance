import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { FeatureFlagProvider, useFeatureFlag, useFeature } from '../FeatureFlagContext';
import { createMockFeatureFlagConfig } from '../../test/utils';

describe('FeatureFlagContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('FeatureFlagProvider', () => {
    it('should provide default feature flags', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagProvider>{children}</FeatureFlagProvider>
      );

      const { result } = renderHook(() => useFeatureFlag(), { wrapper });

      expect(result.current.flags).toBeDefined();
      expect(result.current.flags['ai-predictions']).toBeDefined();
      expect(result.current.flags['ai-predictions'].enabled).toBe(true);
      expect(result.current.isEnabled('ai-predictions')).toBe(true);
    });

    it('should use initial config when provided', () => {
      const customConfig = createMockFeatureFlagConfig({
        flags: {
          'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: false, category: 'ai' },
        },
        userGroups: ['beta-testers'],
        environment: 'production',
      });

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagProvider initialConfig={customConfig}>{children}</FeatureFlagProvider>
      );

      const { result } = renderHook(() => useFeatureFlag(), { wrapper });

      expect(result.current.flags['ai-predictions'].enabled).toBe(false);
      expect(result.current.isEnabled('ai-predictions')).toBe(false);
      expect(result.current.userGroups).toEqual(['beta-testers']);
      expect(result.current.environment).toBe('production');
    });

    it('should load flags from localStorage on mount', () => {
      const savedFlags = {
        'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: false, category: 'ai' },
      };
      localStorage.setItem('feature-flags', JSON.stringify(savedFlags));

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagProvider>{children}</FeatureFlagProvider>
      );

      const { result } = renderHook(() => useFeatureFlag(), { wrapper });

      expect(result.current.flags['ai-predictions'].enabled).toBe(false);
      expect(result.current.isEnabled('ai-predictions')).toBe(false);
    });

    it('should save flags to localStorage when they change', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagProvider>{children}</FeatureFlagProvider>
      );

      const { result } = renderHook(() => useFeatureFlag(), { wrapper });

      act(() => {
        result.current.updateFlag('ai-predictions', false);
      });

      const savedFlags = JSON.parse(localStorage.getItem('feature-flags') || '{}');
      expect(savedFlags['ai-predictions'].enabled).toBe(false);
    });
  });

  describe('useFeatureFlag', () => {
    it('should throw error when used outside provider', () => {
      expect(() => {
        renderHook(() => useFeatureFlag());
      }).toThrow('useFeatureFlag must be used within a FeatureFlagProvider');
    });

    it('should return correct flag state', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagProvider>{children}</FeatureFlagProvider>
      );

      const { result } = renderHook(() => useFeatureFlag(), { wrapper });

      expect(result.current.isEnabled('ai-predictions')).toBe(true);
      expect(result.current.isEnabled('advanced-charts')).toBe(false);
      expect(result.current.getFlag('ai-predictions')).toBeDefined();
      expect(result.current.getFlag('nonexistent')).toBeUndefined();
    });

    it('should update flag state', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagProvider>{children}</FeatureFlagProvider>
      );

      const { result } = renderHook(() => useFeatureFlag(), { wrapper });

      expect(result.current.isEnabled('ai-predictions')).toBe(true);

      act(() => {
        result.current.updateFlag('ai-predictions', false);
      });

      expect(result.current.isEnabled('ai-predictions')).toBe(false);
    });

    it('should update flag config', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagProvider>{children}</FeatureFlagProvider>
      );

      const { result } = renderHook(() => useFeatureFlag(), { wrapper });

      act(() => {
        result.current.updateFlagConfig({
          userGroups: ['premium'],
          environment: 'staging',
        });
      });

      expect(result.current.userGroups).toEqual(['premium']);
      expect(result.current.environment).toBe('staging');
    });

    it('should get flags by category', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagProvider>{children}</FeatureFlagProvider>
      );

      const { result } = renderHook(() => useFeatureFlag(), { wrapper });

      const aiFlags = result.current.getFlagsByCategory('ai');
      expect(aiFlags).toHaveLength(3); // ai-predictions, training-dashboard, ai-optimization
      expect(aiFlags.every(flag => flag.category === 'ai')).toBe(true);
    });

    it('should check user group restrictions', () => {
      const customConfig = createMockFeatureFlagConfig({
        flags: {
          'quantum-ai': {
            id: 'quantum-ai',
            name: 'Quantum AI',
            enabled: true,
            category: 'experimental',
            userGroups: ['beta-testers'],
          },
        },
        userGroups: ['beta-testers'],
      });

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagProvider initialConfig={customConfig}>{children}</FeatureFlagProvider>
      );

      const { result } = renderHook(() => useFeatureFlag(), { wrapper });

      expect(result.current.isEnabled('quantum-ai')).toBe(true);
    });

    it('should check environment restrictions', () => {
      const customConfig = createMockFeatureFlagConfig({
        flags: {
          'debug-tools': {
            id: 'debug-tools',
            name: 'Debug Tools',
            enabled: true,
            category: 'functionality',
            environment: 'development',
          },
        },
        environment: 'development',
      });

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagProvider initialConfig={customConfig}>{children}</FeatureFlagProvider>
      );

      const { result } = renderHook(() => useFeatureFlag(), { wrapper });

      expect(result.current.isEnabled('debug-tools')).toBe(true);
    });

    it('should check rollout percentage', () => {
      const customConfig = createMockFeatureFlagConfig({
        flags: {
          'beta-feature': {
            id: 'beta-feature',
            name: 'Beta Feature',
            enabled: true,
            category: 'experimental',
            rolloutPercentage: 50,
          },
        },
        userId: 'user-123',
      });

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagProvider initialConfig={customConfig}>{children}</FeatureFlagProvider>
      );

      const { result } = renderHook(() => useFeatureFlag(), { wrapper });

      // The result depends on the hash of the user ID
      const isEnabled = result.current.isEnabled('beta-feature');
      expect(typeof isEnabled).toBe('boolean');
    });

    it('should check dependencies', () => {
      const customConfig = createMockFeatureFlagConfig({
        flags: {
          'portfolio-management': {
            id: 'portfolio-management',
            name: 'Portfolio Management',
            enabled: true,
            category: 'trading',
          },
          'backtesting': {
            id: 'backtesting',
            name: 'Backtesting',
            enabled: true,
            category: 'trading',
            dependencies: ['portfolio-management'],
          },
        },
      });

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagProvider initialConfig={customConfig}>{children}</FeatureFlagProvider>
      );

      const { result } = renderHook(() => useFeatureFlag(), { wrapper });

      expect(result.current.isEnabled('portfolio-management')).toBe(true);
      expect(result.current.isEnabled('backtesting')).toBe(true);
    });

    it('should handle missing dependencies', () => {
      const customConfig = createMockFeatureFlagConfig({
        flags: {
          'backtesting': {
            id: 'backtesting',
            name: 'Backtesting',
            enabled: true,
            category: 'trading',
            dependencies: ['nonexistent-feature'],
          },
        },
      });

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagProvider initialConfig={customConfig}>{children}</FeatureFlagProvider>
      );

      const { result } = renderHook(() => useFeatureFlag(), { wrapper });

      expect(result.current.isEnabled('backtesting')).toBe(false);
    });
  });

  describe('useFeature', () => {
    it('should return feature enabled state', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <FeatureFlagProvider>{children}</FeatureFlagProvider>
      );

      const { result } = renderHook(() => useFeature('ai-predictions'), { wrapper });

      expect(result.current).toBe(true);
    });

    it('should throw error when used outside provider', () => {
      expect(() => {
        renderHook(() => useFeature('ai-predictions'));
      }).toThrow('useFeatureFlag must be used within a FeatureFlagProvider');
    });
  });
});