import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  FeatureWrapper,
  ConditionalFeature,
  FeatureGroup,
  FeatureStyleWrapper,
  FeatureNavItem,
  FeatureBadge,
} from '../FeatureWrapper';
import { renderWithProviders, createMockFeatureFlagConfig } from '../../test/utils';

describe('FeatureWrapper', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('FeatureWrapper', () => {
    it('should render children when feature is enabled', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'test-feature': { id: 'test-feature', name: 'Test Feature', enabled: true, category: 'ui' },
        },
      });

      renderWithProviders(
        <FeatureWrapper featureId="test-feature">
          <div data-testid="test-content">Test Content</div>
        </FeatureWrapper>,
        { featureFlags: config }
      );

      expect(screen.getByTestId('test-content')).toBeInTheDocument();
    });

    it('should render fallback when feature is disabled', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'test-feature': { id: 'test-feature', name: 'Test Feature', enabled: false, category: 'ui' },
        },
      });

      renderWithProviders(
        <FeatureWrapper 
          featureId="test-feature" 
          fallback={<div data-testid="fallback-content">Fallback Content</div>}
        >
          <div data-testid="test-content">Test Content</div>
        </FeatureWrapper>,
        { featureFlags: config }
      );

      expect(screen.getByTestId('fallback-content')).toBeInTheDocument();
      expect(screen.queryByTestId('test-content')).not.toBeInTheDocument();
    });

    it('should render disabled state when showDisabledState is true', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'test-feature': { id: 'test-feature', name: 'Test Feature', enabled: false, category: 'ui' },
        },
      });

      renderWithProviders(
        <FeatureWrapper featureId="test-feature" showDisabledState={true}>
          <div data-testid="test-content">Test Content</div>
        </FeatureWrapper>,
        { featureFlags: config }
      );

      expect(screen.getByText('Feature Disabled')).toBeInTheDocument();
      expect(screen.getByText('Test Feature')).toBeInTheDocument();
    });

    it('should not render anything when showDisabledState is false', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'test-feature': { id: 'test-feature', name: 'Test Feature', enabled: false, category: 'ui' },
        },
      });

      const { container } = renderWithProviders(
        <FeatureWrapper featureId="test-feature" showDisabledState={false}>
          <div data-testid="test-content">Test Content</div>
        </FeatureWrapper>,
        { featureFlags: config }
      );

      expect(container.firstChild).toBeNull();
    });

    it('should check requireAll dependencies', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'test-feature': { id: 'test-feature', name: 'Test Feature', enabled: true, category: 'ui' },
          'dependency-1': { id: 'dependency-1', name: 'Dependency 1', enabled: true, category: 'ui' },
          'dependency-2': { id: 'dependency-2', name: 'Dependency 2', enabled: false, category: 'ui' },
        },
      });

      renderWithProviders(
        <FeatureWrapper 
          featureId="test-feature" 
          requireAll={['dependency-1', 'dependency-2']}
          showDisabledState={true}
        >
          <div data-testid="test-content">Test Content</div>
        </FeatureWrapper>,
        { featureFlags: config }
      );

      expect(screen.getByText('Feature Disabled')).toBeInTheDocument();
      expect(screen.getByText('Also requires: dependency-1, dependency-2')).toBeInTheDocument();
    });

    it('should check requireAny dependencies', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'test-feature': { id: 'test-feature', name: 'Test Feature', enabled: true, category: 'ui' },
          'optional-1': { id: 'optional-1', name: 'Optional 1', enabled: false, category: 'ui' },
          'optional-2': { id: 'optional-2', name: 'Optional 2', enabled: true, category: 'ui' },
        },
      });

      renderWithProviders(
        <FeatureWrapper 
          featureId="test-feature" 
          requireAny={['optional-1', 'optional-2']}
        >
          <div data-testid="test-content">Test Content</div>
        </FeatureWrapper>,
        { featureFlags: config }
      );

      expect(screen.getByTestId('test-content')).toBeInTheDocument();
    });
  });

  describe('ConditionalFeature', () => {
    it('should render children when feature is enabled', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'test-feature': { id: 'test-feature', name: 'Test Feature', enabled: true, category: 'ui' },
        },
      });

      renderWithProviders(
        <ConditionalFeature featureId="test-feature">
          <div data-testid="test-content">Test Content</div>
        </ConditionalFeature>,
        { featureFlags: config }
      );

      expect(screen.getByTestId('test-content')).toBeInTheDocument();
    });

    it('should render fallback when feature is disabled', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'test-feature': { id: 'test-feature', name: 'Test Feature', enabled: false, category: 'ui' },
        },
      });

      renderWithProviders(
        <ConditionalFeature 
          featureId="test-feature" 
          fallback={<div data-testid="fallback-content">Fallback Content</div>}
        >
          <div data-testid="test-content">Test Content</div>
        </ConditionalFeature>,
        { featureFlags: config }
      );

      expect(screen.getByTestId('fallback-content')).toBeInTheDocument();
      expect(screen.queryByTestId('test-content')).not.toBeInTheDocument();
    });
  });

  describe('FeatureGroup', () => {
    it('should render children when all features are enabled (mode: all)', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'feature-1': { id: 'feature-1', name: 'Feature 1', enabled: true, category: 'ui' },
          'feature-2': { id: 'feature-2', name: 'Feature 2', enabled: true, category: 'ui' },
        },
      });

      renderWithProviders(
        <FeatureGroup features={['feature-1', 'feature-2']} mode="all">
          <div data-testid="group-content">Group Content</div>
        </FeatureGroup>,
        { featureFlags: config }
      );

      expect(screen.getByTestId('group-content')).toBeInTheDocument();
    });

    it('should not render children when not all features are enabled (mode: all)', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'feature-1': { id: 'feature-1', name: 'Feature 1', enabled: true, category: 'ui' },
          'feature-2': { id: 'feature-2', name: 'Feature 2', enabled: false, category: 'ui' },
        },
      });

      renderWithProviders(
        <FeatureGroup features={['feature-1', 'feature-2']} mode="all" showDisabledState={true}>
          <div data-testid="group-content">Group Content</div>
        </FeatureGroup>,
        { featureFlags: config }
      );

      expect(screen.getByText('Feature Group Disabled')).toBeInTheDocument();
      expect(screen.queryByTestId('group-content')).not.toBeInTheDocument();
    });

    it('should render children when any feature is enabled (mode: any)', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'feature-1': { id: 'feature-1', name: 'Feature 1', enabled: false, category: 'ui' },
          'feature-2': { id: 'feature-2', name: 'Feature 2', enabled: true, category: 'ui' },
        },
      });

      renderWithProviders(
        <FeatureGroup features={['feature-1', 'feature-2']} mode="any">
          <div data-testid="group-content">Group Content</div>
        </FeatureGroup>,
        { featureFlags: config }
      );

      expect(screen.getByTestId('group-content')).toBeInTheDocument();
    });

    it('should not render children when no features are enabled (mode: any)', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'feature-1': { id: 'feature-1', name: 'Feature 1', enabled: false, category: 'ui' },
          'feature-2': { id: 'feature-2', name: 'Feature 2', enabled: false, category: 'ui' },
        },
      });

      renderWithProviders(
        <FeatureGroup features={['feature-1', 'feature-2']} mode="any" showDisabledState={true}>
          <div data-testid="group-content">Group Content</div>
        </FeatureGroup>,
        { featureFlags: config }
      );

      expect(screen.getByText('Feature Group Disabled')).toBeInTheDocument();
      expect(screen.queryByTestId('group-content')).not.toBeInTheDocument();
    });
  });

  describe('FeatureStyleWrapper', () => {
    it('should apply enabled className when feature is enabled', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'test-feature': { id: 'test-feature', name: 'Test Feature', enabled: true, category: 'ui' },
        },
      });

      renderWithProviders(
        <FeatureStyleWrapper
          featureId="test-feature"
          enabledClassName="opacity-100"
          disabledClassName="opacity-50"
        >
          <div data-testid="test-content">Test Content</div>
        </FeatureStyleWrapper>,
        { featureFlags: config }
      );

      const content = screen.getByTestId('test-content');
      expect(content.parentElement).toHaveClass('opacity-100');
    });

    it('should apply disabled className when feature is disabled', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'test-feature': { id: 'test-feature', name: 'Test Feature', enabled: false, category: 'ui' },
        },
      });

      renderWithProviders(
        <FeatureStyleWrapper
          featureId="test-feature"
          enabledClassName="opacity-100"
          disabledClassName="opacity-50"
        >
          <div data-testid="test-content">Test Content</div>
        </FeatureStyleWrapper>,
        { featureFlags: config }
      );

      const content = screen.getByTestId('test-content');
      expect(content.parentElement).toHaveClass('opacity-50');
    });

    it('should render fallback when feature is disabled and fallback provided', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'test-feature': { id: 'test-feature', name: 'Test Feature', enabled: false, category: 'ui' },
        },
      });

      renderWithProviders(
        <FeatureStyleWrapper
          featureId="test-feature"
          enabledClassName="opacity-100"
          disabledClassName="opacity-50"
          fallback={<div data-testid="fallback-content">Fallback Content</div>}
        >
          <div data-testid="test-content">Test Content</div>
        </FeatureStyleWrapper>,
        { featureFlags: config }
      );

      expect(screen.getByTestId('fallback-content')).toBeInTheDocument();
      expect(screen.queryByTestId('test-content')).not.toBeInTheDocument();
    });
  });

  describe('FeatureNavItem', () => {
    it('should render children when feature is enabled', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'test-feature': { id: 'test-feature', name: 'Test Feature', enabled: true, category: 'ui' },
        },
      });

      renderWithProviders(
        <FeatureNavItem featureId="test-feature">
          <div data-testid="nav-item">Nav Item</div>
        </FeatureNavItem>,
        { featureFlags: config }
      );

      expect(screen.getByTestId('nav-item')).toBeInTheDocument();
    });

    it('should not render children when feature is disabled', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'test-feature': { id: 'test-feature', name: 'Test Feature', enabled: false, category: 'ui' },
        },
      });

      const { container } = renderWithProviders(
        <FeatureNavItem featureId="test-feature">
          <div data-testid="nav-item">Nav Item</div>
        </FeatureNavItem>,
        { featureFlags: config }
      );

      expect(container.firstChild).toBeNull();
    });
  });

  describe('FeatureBadge', () => {
    it('should render badge when feature is enabled', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'test-feature': { id: 'test-feature', name: 'Test Feature', enabled: true, category: 'ui' },
        },
      });

      renderWithProviders(
        <FeatureBadge featureId="test-feature" badgeText="New">
          <div data-testid="test-content">Test Content</div>
        </FeatureBadge>,
        { featureFlags: config }
      );

      expect(screen.getByText('New')).toBeInTheDocument();
      expect(screen.getByTestId('test-content')).toBeInTheDocument();
    });

    it('should not render badge when feature is disabled', () => {
      const config = createMockFeatureFlagConfig({
        flags: {
          'test-feature': { id: 'test-feature', name: 'Test Feature', enabled: false, category: 'ui' },
        },
      });

      renderWithProviders(
        <FeatureBadge featureId="test-feature" badgeText="New">
          <div data-testid="test-content">Test Content</div>
        </FeatureBadge>,
        { featureFlags: config }
      );

      expect(screen.queryByText('New')).not.toBeInTheDocument();
      expect(screen.getByTestId('test-content')).toBeInTheDocument();
    });
  });
});