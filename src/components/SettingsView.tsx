import React, { useState } from 'react';
import { Settings, ToggleLeft, ToggleRight, Slider, Palette, Bell } from 'lucide-react';
import { useFeatureFlags } from '../contexts/FeatureFlagContext';

const SettingsView: React.FC = () => {
  const { flags, toggleFeature, getFeaturesByCategory } = useFeatureFlags();
  const [activeTab, setActiveTab] = useState<'features' | 'appearance' | 'notifications' | 'advanced'>('features');

  const tabs = [
    { id: 'features', label: 'Features', icon: ToggleLeft },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'advanced', label: 'Advanced', icon: Settings }
  ];

  const coreFeatures = getFeaturesByCategory('core');
  const advancedFeatures = getFeaturesByCategory('advanced');
  const experimentalFeatures = getFeaturesByCategory('experimental');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center space-x-2">
            <Settings size={32} />
            <span>Settings & Features</span>
          </h1>
          <p className="text-gray-400">
            Customize your trading experience and manage feature flags
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-1">
        <div className="flex flex-wrap gap-1">
          {tabs.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
            >
              <Icon size={20} />
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-6">
        {activeTab === 'features' && (
          <div className="space-y-8">
            {/* Core Features */}
            <div>
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span>Core Features</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {coreFeatures.map(feature => (
                  <div
                    key={feature.name}
                    className="bg-gray-800 border border-gray-700 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-semibold">{feature.name}</h4>
                      <button
                        onClick={() => toggleFeature(feature.name)}
                        className="flex items-center space-x-2"
                      >
                        {feature.enabled ? (
                          <ToggleRight size={24} className="text-green-400" />
                        ) : (
                          <ToggleLeft size={24} className="text-gray-400" />
                        )}
                      </button>
                    </div>
                    <p className="text-gray-400 text-sm mb-2">{feature.description}</p>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-500">Rollout: {feature.rolloutPercentage}%</span>
                      <span className={`px-2 py-1 rounded ${
                        feature.isEnabled ? 'bg-green-900/30 text-green-400' : 'bg-gray-700 text-gray-400'
                      }`}>
                        {feature.isEnabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Advanced Features */}
            <div>
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                <span>Advanced Features</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {advancedFeatures.map(feature => (
                  <div
                    key={feature.name}
                    className="bg-gray-800 border border-gray-700 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-semibold">{feature.name}</h4>
                      <button
                        onClick={() => toggleFeature(feature.name)}
                        className="flex items-center space-x-2"
                      >
                        {feature.enabled ? (
                          <ToggleRight size={24} className="text-green-400" />
                        ) : (
                          <ToggleLeft size={24} className="text-gray-400" />
                        )}
                      </button>
                    </div>
                    <p className="text-gray-400 text-sm mb-2">{feature.description}</p>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-500">Rollout: {feature.rolloutPercentage}%</span>
                      <span className={`px-2 py-1 rounded ${
                        feature.isEnabled ? 'bg-green-900/30 text-green-400' : 'bg-gray-700 text-gray-400'
                      }`}>
                        {feature.isEnabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Experimental Features */}
            <div>
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                <span>Experimental Features</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {experimentalFeatures.map(feature => (
                  <div
                    key={feature.name}
                    className="bg-gray-800 border border-gray-700 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-semibold">{feature.name}</h4>
                      <button
                        onClick={() => toggleFeature(feature.name)}
                        className="flex items-center space-x-2"
                      >
                        {feature.enabled ? (
                          <ToggleRight size={24} className="text-green-400" />
                        ) : (
                          <ToggleLeft size={24} className="text-gray-400" />
                        )}
                      </button>
                    </div>
                    <p className="text-gray-400 text-sm mb-2">{feature.description}</p>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-500">Rollout: {feature.rolloutPercentage}%</span>
                      <span className={`px-2 py-1 rounded ${
                        feature.isEnabled ? 'bg-green-900/30 text-green-400' : 'bg-gray-700 text-gray-400'
                      }`}>
                        {feature.isEnabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'appearance' && (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white mb-4">Appearance Settings</h3>
            <div className="space-y-4">
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <h4 className="text-white font-semibold mb-2">Theme</h4>
                <p className="text-gray-400 text-sm mb-4">Choose your preferred color scheme</p>
                <div className="flex space-x-2">
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg">Dark</button>
                  <button className="px-4 py-2 bg-gray-700 text-gray-400 rounded-lg">Light</button>
                  <button className="px-4 py-2 bg-gray-700 text-gray-400 rounded-lg">Auto</button>
                </div>
              </div>
              
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <h4 className="text-white font-semibold mb-2">Chart Style</h4>
                <p className="text-gray-400 text-sm mb-4">Customize chart appearance</p>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Candlestick Charts</span>
                    <ToggleRight size={24} className="text-green-400" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Dark Theme</span>
                    <ToggleRight size={24} className="text-green-400" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'notifications' && (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white mb-4">Notification Settings</h3>
            <div className="space-y-4">
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <h4 className="text-white font-semibold mb-2">Price Alerts</h4>
                <p className="text-gray-400 text-sm mb-4">Get notified when prices reach your targets</p>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Email Notifications</span>
                    <ToggleRight size={24} className="text-green-400" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Push Notifications</span>
                    <ToggleLeft size={24} className="text-gray-400" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'advanced' && (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white mb-4">Advanced Settings</h3>
            <div className="space-y-4">
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <h4 className="text-white font-semibold mb-2">API Configuration</h4>
                <p className="text-gray-400 text-sm mb-4">Configure external API connections</p>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">Binance API</span>
                    <span className="text-green-400 text-sm">Connected</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-300">News API</span>
                    <span className="text-yellow-400 text-sm">Limited</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SettingsView;