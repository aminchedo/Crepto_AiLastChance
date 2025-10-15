import '@testing-library/jest-dom';
import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers);

// Cleanup after each test case
afterEach(() => {
  cleanup();
});

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
};
Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
});

// Mock fetch
global.fetch = vi.fn();

// Mock WebSocket
global.WebSocket = vi.fn().mockImplementation(() => ({
  close: vi.fn(),
  send: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  readyState: WebSocket.OPEN,
}));

// Mock crypto for UUID generation
Object.defineProperty(global, 'crypto', {
  value: {
    randomUUID: vi.fn(() => 'mock-uuid-1234'),
  },
});

// Mock console methods to reduce noise in tests
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;

beforeEach(() => {
  console.error = vi.fn();
  console.warn = vi.fn();
});

afterEach(() => {
  console.error = originalConsoleError;
  console.warn = originalConsoleWarn;
});

// Mock Chart.js
vi.mock('chart.js', () => ({
  Chart: vi.fn().mockImplementation(() => ({
    destroy: vi.fn(),
    update: vi.fn(),
    render: vi.fn(),
  })),
  registerables: [],
}));

// Mock react-chartjs-2
vi.mock('react-chartjs-2', () => ({
  Line: vi.fn(() => <div data-testid="line-chart">Line Chart</div>),
  Bar: vi.fn(() => <div data-testid="bar-chart">Bar Chart</div>),
  Doughnut: vi.fn(() => <div data-testid="doughnut-chart">Doughnut Chart</div>),
  Pie: vi.fn(() => <div data-testid="pie-chart">Pie Chart</div>),
}));

// Mock recharts
vi.mock('recharts', () => ({
  LineChart: vi.fn(() => <div data-testid="recharts-line">Recharts Line</div>),
  BarChart: vi.fn(() => <div data-testid="recharts-bar">Recharts Bar</div>),
  PieChart: vi.fn(() => <div data-testid="recharts-pie">Recharts Pie</div>),
  XAxis: vi.fn(() => <div data-testid="x-axis">X Axis</div>),
  YAxis: vi.fn(() => <div data-testid="y-axis">Y Axis</div>),
  CartesianGrid: vi.fn(() => <div data-testid="cartesian-grid">Grid</div>),
  Tooltip: vi.fn(() => <div data-testid="tooltip">Tooltip</div>),
  Legend: vi.fn(() => <div data-testid="legend">Legend</div>),
  Line: vi.fn(() => <div data-testid="line">Line</div>),
  Bar: vi.fn(() => <div data-testid="bar">Bar</div>),
  Cell: vi.fn(() => <div data-testid="cell">Cell</div>),
}));

// Mock TensorFlow.js
vi.mock('@tensorflow/tfjs', () => ({
  loadLayersModel: vi.fn(),
  tensor: vi.fn(),
  sequential: vi.fn(),
  layers: {
    dense: vi.fn(),
    dropout: vi.fn(),
  },
  losses: {
    meanSquaredError: vi.fn(),
  },
  optimizers: {
    adam: vi.fn(),
  },
  metrics: {
    meanSquaredError: vi.fn(),
  },
  model: vi.fn(),
  dispose: vi.fn(),
  tidy: vi.fn(),
  ready: Promise.resolve(),
}));

// Mock Supabase
vi.mock('@supabase/supabase-js', () => ({
  createClient: vi.fn(() => ({
    from: vi.fn(() => ({
      select: vi.fn().mockReturnThis(),
      insert: vi.fn().mockReturnThis(),
      update: vi.fn().mockReturnThis(),
      delete: vi.fn().mockReturnThis(),
      eq: vi.fn().mockReturnThis(),
      single: vi.fn(),
    })),
    auth: {
      signIn: vi.fn(),
      signOut: vi.fn(),
      getUser: vi.fn(),
    },
  })),
}));

// Mock axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
    })),
  },
}));

// Mock date-fns
vi.mock('date-fns', () => ({
  format: vi.fn((date) => date.toISOString()),
  parseISO: vi.fn((date) => new Date(date)),
  isAfter: vi.fn(() => true),
  isBefore: vi.fn(() => false),
  addDays: vi.fn((date, days) => new Date(date.getTime() + days * 24 * 60 * 60 * 1000)),
  subDays: vi.fn((date, days) => new Date(date.getTime() - days * 24 * 60 * 60 * 1000)),
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Brain: vi.fn(() => <div data-testid="brain-icon">Brain</div>),
  Wallet: vi.fn(() => <div data-testid="wallet-icon">Wallet</div>),
  BarChart3: vi.fn(() => <div data-testid="bar-chart-icon">BarChart3</div>),
  Newspaper: vi.fn(() => <div data-testid="newspaper-icon">Newspaper</div>),
  Settings: vi.fn(() => <div data-testid="settings-icon">Settings</div>),
  Activity: vi.fn(() => <div data-testid="activity-icon">Activity</div>),
  TrendingUp: vi.fn(() => <div data-testid="trending-up-icon">TrendingUp</div>),
  TrendingDown: vi.fn(() => <div data-testid="trending-down-icon">TrendingDown</div>),
  Minus: vi.fn(() => <div data-testid="minus-icon">Minus</div>),
  AlertTriangle: vi.fn(() => <div data-testid="alert-triangle-icon">AlertTriangle</div>),
  Lock: vi.fn(() => <div data-testid="lock-icon">Lock</div>),
  Eye: vi.fn(() => <div data-testid="eye-icon">Eye</div>),
  EyeOff: vi.fn(() => <div data-testid="eye-off-icon">EyeOff</div>),
  CheckCircle: vi.fn(() => <div data-testid="check-circle-icon">CheckCircle</div>),
  Play: vi.fn(() => <div data-testid="play-icon">Play</div>),
  Square: vi.fn(() => <div data-testid="square-icon">Square</div>),
  RotateCcw: vi.fn(() => <div data-testid="rotate-ccw-icon">RotateCcw</div>),
  Zap: vi.fn(() => <div data-testid="zap-icon">Zap</div>),
  Shield: vi.fn(() => <div data-testid="shield-icon">Shield</div>),
  DollarSign: vi.fn(() => <div data-testid="dollar-sign-icon">DollarSign</div>),
  PieChart: vi.fn(() => <div data-testid="pie-chart-icon">PieChart</div>),
  ExternalLink: vi.fn(() => <div data-testid="external-link-icon">ExternalLink</div>),
  Target: vi.fn(() => <div data-testid="target-icon">Target</div>),
  Filter: vi.fn(() => <div data-testid="filter-icon">Filter</div>),
  Search: vi.fn(() => <div data-testid="search-icon">Search</div>),
  Toggle: vi.fn(() => <div data-testid="toggle-icon">Toggle</div>),
  Clock: vi.fn(() => <div data-testid="clock-icon">Clock</div>),
}));