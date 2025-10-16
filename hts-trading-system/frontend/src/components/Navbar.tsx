import React from 'react';
import {
  BarChart3,
  TrendingUp,
  Zap,
  Briefcase,
  Newspaper,
  Settings,
  Brain,
  Activity
} from 'lucide-react';
import { NavbarProps, ViewType } from '../types';
import { useFeatureFlags } from '../contexts/FeatureFlagContext';

const Navbar: React.FC<NavbarProps> = ({ activeView, onViewChange }) => {
  const { isFeatureEnabled } = useFeatureFlags();

  const navItems = [
    { 
      id: 'dashboard' as ViewType, 
      label: 'Dashboard', 
      icon: BarChart3, 
      enabled: true,
      description: 'Main trading dashboard'
    },
    { 
      id: 'charts' as ViewType, 
      label: 'Charts', 
      icon: TrendingUp, 
      enabled: isFeatureEnabled('realTimeCharts'),
      description: 'Advanced charting tools'
    },
    { 
      id: 'training' as ViewType, 
      label: 'AI Training', 
      icon: Brain, 
      enabled: isFeatureEnabled('trainingDashboard'),
      description: 'AI model training and monitoring'
    },
    { 
      id: 'portfolio' as ViewType, 
      label: 'Portfolio', 
      icon: Briefcase, 
      enabled: isFeatureEnabled('portfolioManagement'),
      description: 'Portfolio management and tracking'
    },
    { 
      id: 'news' as ViewType, 
      label: 'News', 
      icon: Newspaper, 
      enabled: isFeatureEnabled('newsFeed'),
      description: 'Latest cryptocurrency news'
    },
    { 
      id: 'settings' as ViewType, 
      label: 'Settings', 
      icon: Settings, 
      enabled: true,
      description: 'Application settings and preferences'
    }
  ];

  const enabledItems = navItems.filter(item => item.enabled);

  return (
    <nav className="sticky top-0 bg-gray-900/95 border-b border-gray-800 backdrop-blur-sm z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Brain className="text-white" size={20} />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-xl font-bold text-white">
                  <span className="text-gradient">HTS</span> Trading
                </h1>
                <p className="text-xs text-gray-400">AI-Powered Analysis</p>
              </div>
            </div>
          </div>

          {/* Navigation Items */}
          <div className="flex items-center space-x-1 overflow-x-auto scrollbar-hide">
            {enabledItems.map(({ id, label, icon: Icon, description }) => {
              const isActive = activeView === id;
              
              return (
                <button
                  key={id}
                  onClick={() => onViewChange(id)}
                  className={`group flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 whitespace-nowrap ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/25'
                      : 'text-gray-400 hover:text-white hover:bg-gray-800'
                  }`}
                  title={description}
                >
                  <Icon 
                    size={20} 
                    className={`transition-transform duration-200 ${
                      isActive ? 'scale-110' : 'group-hover:scale-105'
                    }`}
                  />
                  <span className="hidden md:inline">{label}</span>
                  
                  {/* Active indicator */}
                  {isActive && (
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Status Indicator */}
          <div className="hidden lg:flex items-center space-x-2">
            <div className="flex items-center space-x-1 px-2 py-1 bg-green-900/30 border border-green-700 rounded-full">
              <Activity size={14} className="text-green-400 animate-pulse" />
              <span className="text-green-400 text-xs font-medium">Live</span>
            </div>
          </div>
        </div>

        {/* Mobile Navigation (if needed) */}
        <div className="lg:hidden border-t border-gray-800 pt-2 pb-2">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-400">
              {enabledItems.length} features enabled
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-xs text-gray-400">Real-time</span>
            </div>
          </div>
        </div>
      </div>

      {/* Scroll indicator for mobile */}
      <div className="lg:hidden absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-blue-500 opacity-50"></div>
    </nav>
  );
};

export default Navbar;