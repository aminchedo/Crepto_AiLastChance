# 🚩 Feature Flags System

A comprehensive feature flag system for the Bolt AI Crypto application that allows for dynamic feature toggling, A/B testing, and gradual rollouts.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Best Practices](#best-practices)

## 🎯 Overview

The feature flag system provides:

- **Dynamic Feature Toggling**: Enable/disable features without code deployment
- **Gradual Rollouts**: Control feature availability by percentage
- **User Group Targeting**: Show features to specific user groups
- **Environment Controls**: Different settings per environment
- **Dependency Management**: Features can depend on other features
- **Real-time Updates**: Changes take effect immediately
- **Persistence**: Settings are saved to localStorage

## 🏗️ Architecture

### Core Components

```
src/
├── contexts/
│   └── FeatureFlagContext.tsx     # Main context and provider
├── components/
│   ├── FeatureWrapper.tsx         # Basic wrapper components
│   ├── FeatureGate.tsx           # Advanced gate components
│   ├── FeatureFlagManager.tsx    # UI for managing flags
│   └── FeatureFlagDemo.tsx       # Demo component
├── hooks/
│   └── useFeatureFlags.ts        # Convenience hooks
└── App.tsx                       # Main app with feature integration
```

### Data Flow

```
FeatureFlagProvider
    ↓
FeatureFlagContext
    ↓
useFeatureFlag / useFeatureFlags
    ↓
FeatureWrapper / FeatureGate
    ↓
Conditional Rendering
```

## 🧩 Components

### 1. FeatureFlagProvider

The main provider that wraps your application and manages feature flag state.

```tsx
import { FeatureFlagProvider } from './contexts/FeatureFlagContext';

function App() {
  return (
    <FeatureFlagProvider>
      <YourApp />
    </FeatureFlagProvider>
  );
}
```

### 2. Basic Wrappers

#### FeatureWrapper
The most flexible wrapper component with advanced options.

```tsx
import { FeatureWrapper } from './components/FeatureWrapper';

<FeatureWrapper
  featureId="ai-predictions"
  fallback={<div>Feature disabled</div>}
  showDisabledState={true}
  requireAll={['portfolio-management']}
  requireAny={['advanced-charts']}
>
  <AIPredictor />
</FeatureWrapper>
```

#### ConditionalFeature
Simple show/hide based on feature flag.

```tsx
import { ConditionalFeature } from './components/FeatureWrapper';

<ConditionalFeature 
  featureId="news-feed"
  fallback={<div>News not available</div>}
>
  <NewsFeed />
</ConditionalFeature>
```

### 3. Advanced Gates

#### FeatureGate
Advanced gate with comprehensive options.

```tsx
import { FeatureGate } from './components/FeatureGate';

<FeatureGate
  featureId="training-dashboard"
  requireAll={['ai-predictions']}
  userGroups={['beta-testers']}
  environment="production"
  showFeatureInfo={true}
  showDependencies={true}
>
  <TrainingDashboard />
</FeatureGate>
```

#### FeatureGateSimple
Simplified version of FeatureGate.

```tsx
import { FeatureGateSimple } from './components/FeatureGate';

<FeatureGateSimple featureId="portfolio-management">
  <Portfolio />
</FeatureGateSimple>
```

#### FeatureGateWithDependencies
Gate that requires specific dependencies.

```tsx
import { FeatureGateWithDependencies } from './components/FeatureGate';

<FeatureGateWithDependencies 
  featureId="backtesting"
  dependencies={['portfolio-management', 'real-time-charts']}
>
  <BacktestingModule />
</FeatureGateWithDependencies>
```

### 4. Feature Groups

#### FeatureGroup
Control multiple features with AND/OR logic.

```tsx
import { FeatureGroup } from './components/FeatureWrapper';

{/* All features must be enabled */}
<FeatureGroup 
  features={['ai-predictions', 'training-dashboard']}
  mode="all"
>
  <CompleteAISuite />
</FeatureGroup>

{/* Any feature can be enabled */}
<FeatureGroup 
  features={['advanced-charts', 'real-time-charts']}
  mode="any"
>
  <ChartFeatures />
</FeatureGroup>
```

### 5. Utility Components

#### FeatureStyleWrapper
Apply different styles based on feature state.

```tsx
import { FeatureStyleWrapper } from './components/FeatureWrapper';

<FeatureStyleWrapper
  featureId="alerts-system"
  enabledClassName="opacity-100"
  disabledClassName="opacity-50 grayscale"
>
  <AlertsComponent />
</FeatureStyleWrapper>
```

#### FeatureBadge
Show badges when features are enabled.

```tsx
import { FeatureBadge } from './components/FeatureWrapper';

<FeatureBadge 
  featureId="ai-optimization"
  badgeText="Optimized"
>
  <AIModel />
</FeatureBadge>
```

## 📖 Usage Examples

### 1. Basic Feature Toggle

```tsx
import { useFeature } from './contexts/FeatureFlagContext';

function MyComponent() {
  const isAIPredictionsEnabled = useFeature('ai-predictions');
  
  return (
    <div>
      {isAIPredictionsEnabled ? (
        <AIPredictor />
      ) : (
        <div>AI predictions not available</div>
      )}
    </div>
  );
}
```

### 2. Using Hooks

```tsx
import { useFeatureFlags } from './hooks/useFeatureFlags';

function MyComponent() {
  const {
    isAIPredictionsEnabled,
    isPortfolioEnabled,
    isTrainingDashboardEnabled
  } = useFeatureFlags();
  
  return (
    <div>
      {isAIPredictionsEnabled && <AIPredictor />}
      {isPortfolioEnabled && <Portfolio />}
      {isTrainingDashboardEnabled && <TrainingDashboard />}
    </div>
  );
}
```

### 3. Conditional Rendering in Navigation

```tsx
const navigationItems = [
  { id: 'dashboard', label: 'Dashboard', enabled: true },
  { 
    id: 'training', 
    label: 'AI Training', 
    enabled: isTrainingDashboardEnabled 
  },
  { 
    id: 'portfolio', 
    label: 'Portfolio', 
    enabled: isPortfolioEnabled 
  },
].filter(item => item.enabled);
```

### 4. Feature with Dependencies

```tsx
<FeatureGateWithDependencies 
  featureId="risk-management"
  dependencies={['portfolio-management']}
>
  <RiskManagementCenter />
</FeatureGateWithDependencies>
```

### 5. Experimental Features

```tsx
<FeatureGateExperimental featureId="quantum-ai">
  <QuantumAIComponent />
</FeatureGateExperimental>
```

## ⚙️ Configuration

### Default Feature Flags

The system comes with pre-configured feature flags:

```typescript
const defaultFlags = {
  // Core Features
  'ai-predictions': { enabled: true, category: 'ai' },
  'portfolio-management': { enabled: true, category: 'trading' },
  'real-time-charts': { enabled: true, category: 'ui' },
  'news-feed': { enabled: true, category: 'analytics' },
  'market-sentiment': { enabled: true, category: 'analytics' },
  'training-dashboard': { enabled: true, category: 'ai' },
  
  // Advanced Features
  'advanced-charts': { enabled: false, category: 'ui', rolloutPercentage: 50 },
  'backtesting': { enabled: false, category: 'trading', rolloutPercentage: 25 },
  'risk-management': { enabled: false, category: 'trading', rolloutPercentage: 30 },
  'whale-tracking': { enabled: false, category: 'analytics', rolloutPercentage: 20 },
  'social-sentiment': { enabled: false, category: 'analytics', rolloutPercentage: 15 },
  'ai-optimization': { enabled: false, category: 'ai', rolloutPercentage: 10 },
  'paper-trading': { enabled: false, category: 'trading', rolloutPercentage: 40 },
  'alerts-system': { enabled: false, category: 'functionality', rolloutPercentage: 60 },
  
  // UI Features
  'dark-mode': { enabled: true, category: 'ui' },
  'mobile-responsive': { enabled: true, category: 'ui' },
  
  // Experimental
  'quantum-ai': { enabled: false, category: 'experimental', rolloutPercentage: 5 },
  'blockchain-analysis': { enabled: false, category: 'experimental', rolloutPercentage: 10 },
};
```

### Custom Configuration

```tsx
<FeatureFlagProvider
  initialConfig={{
    userGroups: ['beta-testers', 'premium'],
    environment: 'production',
    userId: 'user-123'
  }}
>
  <YourApp />
</FeatureFlagProvider>
```

## 🎨 UI Management

### Feature Flag Manager

The `FeatureFlagManager` component provides a UI for managing feature flags:

- **Search and Filter**: Find features by name or category
- **Toggle Features**: Enable/disable features with switches
- **View Details**: See rollout percentages, dependencies, and descriptions
- **Real-time Updates**: Changes take effect immediately

### Accessing the Manager

Click the settings button in the bottom-right corner of the application to open the feature flag manager.

## 🔧 Best Practices

### 1. Feature Naming

- Use kebab-case: `ai-predictions`, `portfolio-management`
- Be descriptive: `advanced-charts` not `charts2`
- Group by category: `ai-*`, `trading-*`, `ui-*`

### 2. Dependencies

- Define clear dependencies between features
- Use `requireAll` for mandatory dependencies
- Use `requireAny` for optional enhancements

### 3. Rollout Strategy

- Start with low rollout percentages (10-25%)
- Gradually increase based on feedback
- Use user groups for beta testing

### 4. Fallback Content

- Always provide meaningful fallback content
- Explain why features are disabled
- Guide users to enable features

### 5. Performance

- Use `ConditionalFeature` for simple show/hide
- Use `FeatureWrapper` for complex logic
- Avoid deep nesting of feature wrappers

### 6. Testing

- Test with features enabled and disabled
- Verify fallback content displays correctly
- Check dependency chains work properly

## 🚀 Advanced Usage

### Custom Feature Flag Logic

```tsx
import { useFeatureFlag } from './contexts/FeatureFlagContext';

function CustomFeatureLogic() {
  const { isEnabled, getFlag } = useFeatureFlag();
  
  const isAIPredictionsEnabled = isEnabled('ai-predictions');
  const aiFlag = getFlag('ai-predictions');
  
  // Custom logic based on flag details
  if (aiFlag?.rolloutPercentage && aiFlag.rolloutPercentage < 100) {
    return <div>Feature in beta</div>;
  }
  
  return isAIPredictionsEnabled ? <AIPredictor /> : null;
}
```

### Environment-Specific Features

```tsx
<FeatureGate
  featureId="debug-tools"
  environment="development"
>
  <DebugPanel />
</FeatureGate>
```

### User Group Targeting

```tsx
<FeatureGate
  featureId="premium-features"
  userGroups={['premium', 'enterprise']}
>
  <PremiumFeatures />
</FeatureGate>
```

## 🔍 Debugging

### Check Feature Status

```tsx
import { useFeatureFlag } from './contexts/FeatureFlagContext';

function DebugComponent() {
  const { flags, isEnabled } = useFeatureFlag();
  
  console.log('All flags:', flags);
  console.log('AI predictions enabled:', isEnabled('ai-predictions'));
  
  return <div>Check console for debug info</div>;
}
```

### Feature Flag Manager

The built-in manager shows:
- Current feature states
- Dependencies and conflicts
- Rollout percentages
- User group assignments

## 📝 Migration Guide

### From Hard-coded Features

**Before:**
```tsx
const showAIPredictions = true; // Hard-coded

return showAIPredictions ? <AIPredictor /> : null;
```

**After:**
```tsx
import { useFeature } from './contexts/FeatureFlagContext';

const isAIPredictionsEnabled = useFeature('ai-predictions');

return isAIPredictionsEnabled ? <AIPredictor /> : null;
```

### From Props-based Toggles

**Before:**
```tsx
interface Props {
  enableAI: boolean;
  enablePortfolio: boolean;
}

function App({ enableAI, enablePortfolio }: Props) {
  return (
    <div>
      {enableAI && <AIPredictor />}
      {enablePortfolio && <Portfolio />}
    </div>
  );
}
```

**After:**
```tsx
import { useFeatureFlags } from './hooks/useFeatureFlags';

function App() {
  const { isAIPredictionsEnabled, isPortfolioEnabled } = useFeatureFlags();
  
  return (
    <div>
      {isAIPredictionsEnabled && <AIPredictor />}
      {isPortfolioEnabled && <Portfolio />}
    </div>
  );
}
```

## 🎯 Conclusion

The feature flag system provides a powerful and flexible way to manage features in your application. It enables:

- **Safer Deployments**: Test features with real users before full rollout
- **Better User Experience**: Gradual feature introduction and rollback capability
- **A/B Testing**: Compare different feature implementations
- **Environment Control**: Different features for different environments
- **User Targeting**: Show features to specific user groups

Start with simple feature toggles and gradually adopt more advanced patterns as your needs grow.