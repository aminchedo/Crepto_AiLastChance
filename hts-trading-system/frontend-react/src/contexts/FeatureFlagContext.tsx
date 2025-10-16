import React, { createContext, useState, useEffect } from 'react';

export interface FeatureFlag {
  name: string;
  enabled: boolean;
  rolloutPercentage: number;
  userGroups?: string[];
  dependencies?: string[];
}

interface FeatureFlagsContextType {
  flags: Record<string, FeatureFlag>;
  isFeatureEnabled: (featureName: string) => boolean;
  toggleFeature: (featureName: string) => void;
}

export const FeatureFlagsContext = createContext<FeatureFlagsContextType | undefined>(undefined);

const DEFAULT_FLAGS: Record<string, FeatureFlag> = {
  // Core Features
  aiPredictions: { name: 'AI Predictions', enabled: true, rolloutPercentage: 100 },
  portfolioManagement: { name: 'Portfolio Management', enabled: true, rolloutPercentage: 100 },
  realTimeCharts: { name: 'Real-time Charts', enabled: true, rolloutPercentage: 100 },
  newsFeed: { name: 'News Feed', enabled: true, rolloutPercentage: 100 },
  marketSentiment: { name: 'Market Sentiment', enabled: true, rolloutPercentage: 100 },
  trainingDashboard: { name: 'Training Dashboard', enabled: true, rolloutPercentage: 100 },

  // Advanced Features
  advancedCharts: { name: 'Advanced Charts', enabled: true, rolloutPercentage: 50 },
  backtesting: { name: 'Backtesting', enabled: true, rolloutPercentage: 25 },
  riskManagement: { name: 'Risk Management', enabled: true, rolloutPercentage: 30 },
  whaleTracking: { name: 'Whale Tracking', enabled: true, rolloutPercentage: 20 },
  paperTrading: { name: 'Paper Trading', enabled: true, rolloutPercentage: 40 },
  alertsSystem: { name: 'Alerts System', enabled: true, rolloutPercentage: 60 },

  // Experimental
  quantumAI: { name: 'Quantum AI', enabled: true, rolloutPercentage: 5 },
  blockchainAnalysis: { name: 'Blockchain Analysis', enabled: true, rolloutPercentage: 10 }
};

export const FeatureFlagsProvider: React.FC<{ children: React.ReactNode }> = ({
  children
}) => {
  const [flags, setFlags] = useState<Record<string, FeatureFlag>>(DEFAULT_FLAGS);

  useEffect(() => {
    // Load flags from localStorage
    const saved = localStorage.getItem('featureFlags');
    if (saved) {
      try {
        setFlags(JSON.parse(saved));
      } catch (error) {
        console.error('Error loading feature flags:', error);
      }
    }
  }, []);

  const isFeatureEnabled = (featureName: string): boolean => {
    const flag = flags[featureName];
    if (!flag) return false;

    if (!flag.enabled) return false;

    // Check rollout percentage
    const userId = Math.random(); // Simulate user ID
    if (userId * 100 > flag.rolloutPercentage) return false;

    return true;
  };

  const toggleFeature = (featureName: string) => {
    setFlags(prev => {
      const updated = {
        ...prev,
        [featureName]: {
          ...prev[featureName],
          enabled: !prev[featureName].enabled
        }
      };
      localStorage.setItem('featureFlags', JSON.stringify(updated));
      return updated;
    });
  };

  return (
    <FeatureFlagsContext.Provider value={{ flags, isFeatureEnabled, toggleFeature }}>
      {children}
    </FeatureFlagsContext.Provider>
  );
};
