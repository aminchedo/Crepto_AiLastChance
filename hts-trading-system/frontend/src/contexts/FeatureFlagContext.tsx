import React, { createContext, useState, useEffect, useContext } from 'react';
import { FeatureFlag, FeatureFlags, FeatureFlagsContextType } from '../types';

// Default feature flags configuration
const DEFAULT_FLAGS: FeatureFlags = {
  // Core Features (100% rollout)
  aiPredictions: { 
    name: 'AI Predictions', 
    enabled: true, 
    rolloutPercentage: 100,
    description: 'AI-powered price predictions and market analysis'
  },
  portfolioManagement: { 
    name: 'Portfolio Management', 
    enabled: true, 
    rolloutPercentage: 100,
    description: 'Track and manage your cryptocurrency portfolio'
  },
  realTimeCharts: { 
    name: 'Real-time Charts', 
    enabled: true, 
    rolloutPercentage: 100,
    description: 'Live price charts with technical indicators'
  },
  newsFeed: { 
    name: 'News Feed', 
    enabled: true, 
    rolloutPercentage: 100,
    description: 'Latest cryptocurrency news and analysis'
  },
  marketSentiment: { 
    name: 'Market Sentiment', 
    enabled: true, 
    rolloutPercentage: 100,
    description: 'Real-time market sentiment analysis'
  },
  trainingDashboard: { 
    name: 'Training Dashboard', 
    enabled: true, 
    rolloutPercentage: 100,
    description: 'AI model training and monitoring'
  },

  // Advanced Features (0-60% rollout)
  advancedCharts: { 
    name: 'Advanced Charts', 
    enabled: false, 
    rolloutPercentage: 50,
    description: 'TradingView integration and advanced charting tools'
  },
  backtesting: { 
    name: 'Backtesting', 
    enabled: false, 
    rolloutPercentage: 25,
    description: 'Strategy backtesting and performance analysis'
  },
  riskManagement: { 
    name: 'Risk Management', 
    enabled: false, 
    rolloutPercentage: 30,
    description: 'Advanced risk management tools and alerts'
  },
  whaleTracking: { 
    name: 'Whale Tracking', 
    enabled: false, 
    rolloutPercentage: 20,
    description: 'Monitor large cryptocurrency transactions'
  },
  paperTrading: { 
    name: 'Paper Trading', 
    enabled: false, 
    rolloutPercentage: 40,
    description: 'Simulate trading without real money'
  },
  alertsSystem: { 
    name: 'Alerts System', 
    enabled: false, 
    rolloutPercentage: 60,
    description: 'Custom price and market alerts'
  },

  // Experimental Features (5-10% rollout)
  quantumAI: { 
    name: 'Quantum AI', 
    enabled: false, 
    rolloutPercentage: 5,
    description: 'Experimental quantum computing integration'
  },
  blockchainAnalysis: { 
    name: 'Blockchain Analysis', 
    enabled: false, 
    rolloutPercentage: 10,
    description: 'On-chain data analysis and insights'
  }
};

// Create context
const FeatureFlagsContext = createContext<FeatureFlagsContextType | undefined>(undefined);

// Provider component
export const FeatureFlagsProvider: React.FC<{ children: React.ReactNode }> = ({
  children
}) => {
  const [flags, setFlags] = useState<FeatureFlags>(DEFAULT_FLAGS);

  // Load flags from localStorage on mount
  useEffect(() => {
    const savedFlags = localStorage.getItem('hts-feature-flags');
    if (savedFlags) {
      try {
        const parsedFlags = JSON.parse(savedFlags);
        setFlags(prevFlags => ({
          ...prevFlags,
          ...parsedFlags
        }));
        console.log('✅ Feature flags loaded from localStorage');
      } catch (error) {
        console.error('❌ Error loading feature flags:', error);
      }
    }
  }, []);

  // Save flags to localStorage when they change
  useEffect(() => {
    localStorage.setItem('hts-feature-flags', JSON.stringify(flags));
  }, [flags]);

  // Check if a feature is enabled
  const isFeatureEnabled = (featureName: string): boolean => {
    const flag = flags[featureName];
    if (!flag) {
      console.warn(`⚠️ Feature flag '${featureName}' not found`);
      return false;
    }

    // Check if feature is explicitly disabled
    if (!flag.enabled) {
      return false;
    }

    // Check rollout percentage
    const userId = getUserId();
    const rolloutHash = hashUserId(userId);
    const userRolloutPercentage = (rolloutHash % 100) + 1;

    return userRolloutPercentage <= flag.rolloutPercentage;
  };

  // Toggle a feature flag
  const toggleFeature = (featureName: string): void => {
    setFlags(prevFlags => {
      const flag = prevFlags[featureName];
      if (!flag) {
        console.warn(`⚠️ Feature flag '${featureName}' not found`);
        return prevFlags;
      }

      const updatedFlags = {
        ...prevFlags,
        [featureName]: {
          ...flag,
          enabled: !flag.enabled
        }
      };

      console.log(`🔄 Feature '${featureName}' ${!flag.enabled ? 'enabled' : 'disabled'}`);
      return updatedFlags;
    });
  };

  // Update rollout percentage
  const updateRolloutPercentage = (featureName: string, percentage: number): void => {
    setFlags(prevFlags => {
      const flag = prevFlags[featureName];
      if (!flag) {
        console.warn(`⚠️ Feature flag '${featureName}' not found`);
        return prevFlags;
      }

      const updatedFlags = {
        ...prevFlags,
        [featureName]: {
          ...flag,
          rolloutPercentage: Math.max(0, Math.min(100, percentage))
        }
      };

      console.log(`🔄 Feature '${featureName}' rollout updated to ${percentage}%`);
      return updatedFlags;
    });
  };

  // Reset all flags to default
  const resetFlags = (): void => {
    setFlags(DEFAULT_FLAGS);
    console.log('🔄 Feature flags reset to default');
  };

  // Get feature flag status
  const getFeatureStatus = (featureName: string) => {
    const flag = flags[featureName];
    if (!flag) return null;

    return {
      ...flag,
      isEnabled: isFeatureEnabled(featureName)
    };
  };

  // Get all enabled features
  const getEnabledFeatures = (): string[] => {
    return Object.keys(flags).filter(featureName => isFeatureEnabled(featureName));
  };

  // Get features by category
  const getFeaturesByCategory = (category: 'core' | 'advanced' | 'experimental') => {
    const categories = {
      core: ['aiPredictions', 'portfolioManagement', 'realTimeCharts', 'newsFeed', 'marketSentiment', 'trainingDashboard'],
      advanced: ['advancedCharts', 'backtesting', 'riskManagement', 'whaleTracking', 'paperTrading', 'alertsSystem'],
      experimental: ['quantumAI', 'blockchainAnalysis']
    };

    return categories[category].map(featureName => ({
      name: featureName,
      ...getFeatureStatus(featureName)
    })).filter(Boolean);
  };

  const contextValue: FeatureFlagsContextType = {
    flags,
    isFeatureEnabled,
    toggleFeature,
    // Additional methods
    updateRolloutPercentage,
    resetFlags,
    getFeatureStatus,
    getEnabledFeatures,
    getFeaturesByCategory
  };

  return (
    <FeatureFlagsContext.Provider value={contextValue}>
      {children}
    </FeatureFlagsContext.Provider>
  );
};

// Custom hook to use feature flags
export const useFeatureFlags = (): FeatureFlagsContextType => {
  const context = useContext(FeatureFlagsContext);
  if (context === undefined) {
    throw new Error('useFeatureFlags must be used within a FeatureFlagsProvider');
  }
  return context;
};

// Utility functions
const getUserId = (): string => {
  // In a real app, this would come from authentication
  // For now, we'll use a stored user ID or generate one
  let userId = localStorage.getItem('hts-user-id');
  if (!userId) {
    userId = Math.random().toString(36).substring(2, 15);
    localStorage.setItem('hts-user-id', userId);
  }
  return userId;
};

const hashUserId = (userId: string): number => {
  let hash = 0;
  for (let i = 0; i < userId.length; i++) {
    const char = userId.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash);
};

// Feature gate component
interface FeatureGateProps {
  feature: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
  showFeatureInfo?: boolean;
}

export const FeatureGate: React.FC<FeatureGateProps> = ({
  feature,
  children,
  fallback = null,
  showFeatureInfo = false
}) => {
  const { isFeatureEnabled, getFeatureStatus } = useFeatureFlags();
  const isEnabled = isFeatureEnabled(feature);
  const featureStatus = getFeatureStatus(feature);

  if (isEnabled) {
    return <>{children}</>;
  }

  if (showFeatureInfo && featureStatus) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 text-center">
        <div className="text-gray-400 text-sm mb-2">
          {featureStatus.description}
        </div>
        <div className="text-xs text-gray-500">
          Rollout: {featureStatus.rolloutPercentage}%
        </div>
      </div>
    );
  }

  return <>{fallback}</>;
};

// Feature gate with dependencies
interface FeatureGateWithDependenciesProps {
  feature: string;
  dependencies: string[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const FeatureGateWithDependencies: React.FC<FeatureGateWithDependenciesProps> = ({
  feature,
  dependencies,
  children,
  fallback = null
}) => {
  const { isFeatureEnabled } = useFeatureFlags();
  
  const isFeatureEnabled_ = isFeatureEnabled(feature);
  const areDependenciesEnabled = dependencies.every(dep => isFeatureEnabled(dep));

  if (isFeatureEnabled_ && areDependenciesEnabled) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
};

// Simple feature gate
interface FeatureGateSimpleProps {
  feature: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const FeatureGateSimple: React.FC<FeatureGateSimpleProps> = ({
  feature,
  children,
  fallback = null
}) => {
  const { isFeatureEnabled } = useFeatureFlags();
  
  return isFeatureEnabled(feature) ? <>{children}</> : <>{fallback}</>;
};

export default FeatureFlagsContext;