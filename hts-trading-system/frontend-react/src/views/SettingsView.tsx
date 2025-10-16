import React, { useContext } from 'react';
import { FeatureFlagsContext } from '../contexts/FeatureFlagContext';

const SettingsView: React.FC = () => {
  const context = useContext(FeatureFlagsContext);

  if (!context) return null;

  const { flags, toggleFeature } = context;

  const coreFeatures = Object.entries(flags).filter(([_, flag]) =>
    ['aiPredictions', 'portfolioManagement', 'realTimeCharts', 'newsFeed', 'marketSentiment', 'trainingDashboard'].includes(flag.name.replace(/\s/g, '').toLowerCase())
  );

  const advancedFeatures = Object.entries(flags).filter(([_, flag]) =>
    ['advancedCharts', 'backtesting', 'riskManagement', 'whaleTracking', 'paperTrading', 'alertsSystem'].includes(flag.name.replace(/\s/g, '').toLowerCase())
  );

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Settings & Features</h1>

      {/* Core Features */}
      <section>
        <h2 className="text-2xl font-bold mb-4">🔧 Core Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {coreFeatures.map(([key, flag]) => (
            <div
              key={key}
              className="bg-gray-900 border border-gray-700 rounded-lg p-4 flex justify-between items-center"
            >
              <div>
                <h3 className="text-white font-semibold">{flag.name}</h3>
                <p className="text-gray-400 text-sm">
                  Rollout: {flag.rolloutPercentage}%
                </p>
              </div>
              <button
                onClick={() => toggleFeature(key)}
                className={`px-4 py-2 rounded font-semibold transition-all ${
                  flag.enabled
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-700 text-gray-400'
                }`}
              >
                {flag.enabled ? 'ON' : 'OFF'}
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Advanced Features */}
      <section>
        <h2 className="text-2xl font-bold mb-4">⚡ Advanced Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {advancedFeatures.map(([key, flag]) => (
            <div
              key={key}
              className="bg-gray-900 border border-gray-700 rounded-lg p-4 flex justify-between items-center"
            >
              <div>
                <h3 className="text-white font-semibold">{flag.name}</h3>
                <p className="text-gray-400 text-sm">
                  Rollout: {flag.rolloutPercentage}%
                </p>
              </div>
              <button
                onClick={() => toggleFeature(key)}
                className={`px-4 py-2 rounded font-semibold transition-all ${
                  flag.enabled
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-700 text-gray-400'
                }`}
              >
                {flag.enabled ? 'ON' : 'OFF'}
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default SettingsView;
