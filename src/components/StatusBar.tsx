import React from 'react';
import { Wifi, WifiOff, Clock, Activity, AlertCircle } from 'lucide-react';
import { StatusBarProps } from '../types';

const StatusBar: React.FC<StatusBarProps> = ({ 
  connected, 
  lastUpdate, 
  isLoading = false 
}) => {
  const getTimeDiff = (): string => {
    const diff = Date.now() - lastUpdate;
    if (diff < 1000) return 'just now';
    if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`;
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    return `${Math.floor(diff / 3600000)}h ago`;
  };

  const getConnectionStatus = () => {
    if (isLoading) {
      return {
        icon: Activity,
        text: 'Connecting...',
        color: 'text-yellow-400',
        bgColor: 'bg-yellow-900/30',
        borderColor: 'border-yellow-700',
        animate: 'animate-pulse'
      };
    }

    if (connected) {
      return {
        icon: Wifi,
        text: 'Connected',
        color: 'text-green-400',
        bgColor: 'bg-green-900/30',
        borderColor: 'border-green-700',
        animate: 'animate-pulse'
      };
    }

    return {
      icon: WifiOff,
      text: 'Disconnected',
      color: 'text-red-400',
      bgColor: 'bg-red-900/30',
      borderColor: 'border-red-700',
      animate: ''
    };
  };

  const status = getConnectionStatus();
  const StatusIcon = status.icon;

  return (
    <div className="bg-gray-900/80 border-b border-gray-700 px-6 py-3 backdrop-blur-sm">
      <div className="flex flex-col sm:flex-row items-center justify-between space-y-2 sm:space-y-0">
        {/* Connection Status */}
        <div className="flex items-center space-x-4">
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full border ${status.bgColor} ${status.borderColor}`}>
            <StatusIcon className={`${status.color} ${status.animate}`} size={16} />
            <span className={`text-sm font-medium ${status.color}`}>
              {status.text}
            </span>
          </div>

          {/* Data Status */}
          <div className="flex items-center space-x-2 text-gray-400 text-sm">
            <Clock size={14} />
            <span>Updated: {getTimeDiff()}</span>
          </div>
        </div>

        {/* System Status */}
        <div className="flex items-center space-x-4 text-sm">
          {/* Version */}
          <div className="text-gray-500">
            HTS v1.0.0
          </div>

          {/* Status Indicators */}
          <div className="flex items-center space-x-2">
            {/* WebSocket Status */}
            <div className="flex items-center space-x-1">
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'} ${connected ? 'animate-pulse' : ''}`}></div>
              <span className="text-gray-400 text-xs">WS</span>
            </div>

            {/* API Status */}
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></div>
              <span className="text-gray-400 text-xs">API</span>
            </div>

            {/* AI Status */}
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 rounded-full bg-purple-400 animate-pulse"></div>
              <span className="text-gray-400 text-xs">AI</span>
            </div>
          </div>

          {/* Error Indicator */}
          {!connected && !isLoading && (
            <div className="flex items-center space-x-1 text-red-400">
              <AlertCircle size={14} />
              <span className="text-xs">Connection Error</span>
            </div>
          )}
        </div>
      </div>

      {/* Progress Bar for Loading */}
      {isLoading && (
        <div className="mt-2 w-full bg-gray-700 rounded-full h-1">
          <div className="bg-blue-500 h-1 rounded-full animate-pulse" style={{ width: '60%' }}></div>
        </div>
      )}
    </div>
  );
};

export default StatusBar;