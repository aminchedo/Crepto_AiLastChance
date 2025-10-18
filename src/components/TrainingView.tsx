import React from 'react';
import { Brain, Activity, BarChart3, Zap } from 'lucide-react';

interface TrainingViewProps {
  isLoading: boolean;
}

const TrainingView: React.FC<TrainingViewProps> = ({ isLoading }) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center space-x-2">
            <Brain size={32} />
            <span>AI Training Dashboard</span>
          </h1>
          <p className="text-gray-400">
            Monitor and manage AI model training progress
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-2">
          <Activity size={16} className="text-purple-400 animate-pulse" />
          <span className="text-sm text-gray-400">AI Active</span>
        </div>
      </div>

      {/* Training Status */}
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto mb-4"></div>
              <p className="text-gray-400">Loading training data...</p>
            </div>
          </div>
        ) : (
          <div className="text-center">
            <Brain size={64} className="text-purple-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">
              AI Training System
            </h3>
            <p className="text-gray-400 mb-4">
              Advanced machine learning model training and monitoring
            </p>
            <div className="bg-gray-800 rounded-lg p-4 max-w-md mx-auto">
              <p className="text-sm text-gray-400 mb-2">
                Training features will include:
              </p>
              <ul className="text-sm text-gray-300 space-y-1">
                <li>• Real-time loss monitoring</li>
                <li>• Model performance metrics</li>
                <li>• Training progress visualization</li>
                <li>• Hyperparameter tuning</li>
                <li>• Model validation</li>
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Training Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { name: 'Loss', value: '0.0234', trend: 'down', icon: BarChart3 },
          { name: 'Accuracy', value: '94.2%', trend: 'up', icon: Activity },
          { name: 'Epoch', value: '156', trend: 'up', icon: Zap },
          { name: 'Learning Rate', value: '0.001', trend: 'stable', icon: Brain }
        ].map(metric => (
          <div key={metric.name} className="bg-gray-900 border border-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <metric.icon size={20} className="text-blue-400" />
              <span className={`text-xs px-2 py-1 rounded ${
                metric.trend === 'up' ? 'bg-green-900/30 text-green-400' :
                metric.trend === 'down' ? 'bg-red-900/30 text-red-400' :
                'bg-gray-700 text-gray-400'
              }`}>
                {metric.trend}
              </span>
            </div>
            <div className="text-2xl font-bold text-white">{metric.value}</div>
            <div className="text-sm text-gray-400">{metric.name}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TrainingView;