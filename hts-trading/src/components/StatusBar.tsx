import React from 'react';
import { Wifi, WifiOff, Clock } from 'lucide-react';

interface StatusBarProps {
  connected: boolean;
  lastUpdate: number;
}

const StatusBar: React.FC<StatusBarProps> = ({ connected, lastUpdate }) => {
  const getTimeDiff = () => {
    const diff = Date.now() - lastUpdate;
    if (diff < 1000) return 'just now';
    if (diff < 60000) return `${Math.floor(diff / 1000)}s ago`;
    return `${Math.floor(diff / 60000)}m ago`;
  };

  return (
    <div className="bg-gray-900/80 border-b border-gray-700 px-6 py-3 flex justify-between items-center">
      <div className="flex items-center gap-2">
        {connected ? (
          <>
            <Wifi className="text-green-500 animate-pulse" size={18} />
            <span className="text-green-400 text-sm font-semibold">Connected</span>
          </>
        ) : (
          <>
            <WifiOff className="text-red-500" size={18} />
            <span className="text-red-400 text-sm font-semibold">
              Disconnected
            </span>
          </>
        )}
      </div>

      <div className="flex items-center gap-2 text-gray-400 text-sm">
        <Clock size={16} />
        <span>Updated: {getTimeDiff()}</span>
      </div>

      <div className="text-xs text-gray-500">
        HTS Trading System v1.0
      </div>
    </div>
  );
};

export default StatusBar;