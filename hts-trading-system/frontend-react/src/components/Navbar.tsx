import React from 'react';
import {
  BarChart3,
  TrendingUp,
  Zap,
  Briefcase,
  Newspaper,
  Settings
} from 'lucide-react';

interface Props {
  activeView: string;
  onViewChange: (view: any) => void;
}

const Navbar: React.FC<Props> = ({ activeView, onViewChange }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'charts', label: 'Charts', icon: TrendingUp },
    { id: 'training', label: 'Training', icon: Zap },
    { id: 'portfolio', label: 'Portfolio', icon: Briefcase },
    { id: 'news', label: 'News', icon: Newspaper },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  return (
    <nav className="sticky top-0 bg-gray-900/95 border-b border-gray-800 backdrop-blur-sm z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center gap-2 py-4 overflow-x-auto">
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = activeView === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onViewChange(item.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                <Icon size={20} />
                {item.label}
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
