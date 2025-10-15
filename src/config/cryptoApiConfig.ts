/**
 * Crypto API Configuration
 * 
 * SECURITY: All API keys must be stored in .env.local
 * This file reads from environment variables only.
 * 
 * @see env.example for required environment variables
 */

// Environment variable helper with validation
const getEnvVar = (key: string, required: boolean = false): string => {
    const value = import.meta.env[key] || '';

    if (required && !value) {
        console.error(`Missing required environment variable: ${key}`);
        throw new Error(`Configuration error: ${key} is required but not set`);
    }

    return value;
};

// Feature flags
export const FEATURE_FLAGS = {
    USE_REAL_APIS: import.meta.env.VITE_USE_REAL_APIS === 'true',
    ENABLE_CACHE: import.meta.env.VITE_ENABLE_API_CACHE !== 'false', // Default true
    DEBUG_LOGGING: import.meta.env.VITE_API_DEBUG_LOGGING === 'true'
} as const;

// API Keys (read from environment)
export const API_KEYS = {
    // Market Data
    CMC_PRIMARY: getEnvVar('VITE_CMC_API_KEY_PRIMARY'),
    CMC_BACKUP: getEnvVar('VITE_CMC_API_KEY_BACKUP'),
    CRYPTOCOMPARE: getEnvVar('VITE_CRYPTOCOMPARE_KEY'),

    // Block Explorers
    ETHERSCAN: getEnvVar('VITE_ETHERSCAN_KEY'),
    BSCSCAN: getEnvVar('VITE_BSCSCAN_KEY'),
    TRONSCAN: getEnvVar('VITE_TRONSCAN_KEY'),

    // News
    NEWSAPI: getEnvVar('VITE_NEWSAPI_KEY'),

    // Optional
    WHALEALERT: getEnvVar('VITE_WHALEALERT_KEY')
} as const;

// Rate limiting configuration
export const RATE_LIMITS = {
    DEFAULT: parseInt(import.meta.env.VITE_API_RATE_LIMIT || '60', 10), // requests per minute
    COINMARKETCAP: 30, // CMC free tier: 333/day ≈ 14/hour ≈ 0.23/min, be conservative
    COINGECKO: 50, // CoinGecko: 50 calls/min
    NEWSAPI: 100, // NewsAPI: 100 requests/day free tier
    ETHERSCAN: 5 // Etherscan: 5 calls/sec max
} as const;

// Cache configuration
export const CACHE_CONFIG = {
    ENABLED: FEATURE_FLAGS.ENABLE_CACHE,
    TTL: parseInt(import.meta.env.VITE_CACHE_TTL || '30', 10) * 1000, // Convert to ms
    PRICES_TTL: 10 * 1000, // 10 seconds for prices
    NEWS_TTL: 5 * 60 * 1000, // 5 minutes for news
    SENTIMENT_TTL: 5 * 60 * 1000, // 5 minutes for sentiment
    HISTORICAL_TTL: 60 * 60 * 1000 // 1 hour for historical data
} as const;

// Circuit breaker configuration
export const CIRCUIT_BREAKER_CONFIG = {
    THRESHOLD: parseInt(import.meta.env.VITE_CIRCUIT_BREAKER_THRESHOLD || '5', 10),
    TIMEOUT: 60 * 1000, // 1 minute
    RESET_TIMEOUT: 30 * 1000 // 30 seconds
} as const;

// API endpoint configuration
interface ApiEndpoint {
    name: string;
    baseUrl: string;
    getKey: () => string; // Function to get key (not stored directly)
    timeout: number;
    headerName?: string;
    rateLimit: number; // requests per minute
}

interface ApiConfig {
    primary: ApiEndpoint;
    fallbacks: ApiEndpoint[];
}

export const API_CONFIG: {
    blockExplorers: {
        tron: ApiConfig;
        bsc: ApiConfig;
        ethereum: ApiConfig;
    };
    marketData: ApiConfig;
    news: ApiConfig;
    sentiment: ApiConfig;
    whaleTracking: ApiConfig;
} = {
    blockExplorers: {
        tron: {
            primary: {
                name: 'TronScan',
                baseUrl: 'https://api.tronscan.org/api',
                getKey: () => API_KEYS.TRONSCAN,
                timeout: 10000,
                rateLimit: RATE_LIMITS.DEFAULT
            },
            fallbacks: [
                {
                    name: 'TronGrid',
                    baseUrl: 'https://api.trongrid.io/v1',
                    getKey: () => '',
                    timeout: 10000,
                    rateLimit: RATE_LIMITS.DEFAULT
                }
            ]
        },
        bsc: {
            primary: {
                name: 'BscScan',
                baseUrl: 'https://api.bscscan.com/api',
                getKey: () => API_KEYS.BSCSCAN,
                timeout: 10000,
                rateLimit: RATE_LIMITS.DEFAULT
            },
            fallbacks: []
        },
        ethereum: {
            primary: {
                name: 'Etherscan',
                baseUrl: 'https://api.etherscan.io/api',
                getKey: () => API_KEYS.ETHERSCAN,
                timeout: 10000,
                rateLimit: RATE_LIMITS.ETHERSCAN
            },
            fallbacks: [
                {
                    name: 'Covalent',
                    baseUrl: 'https://api.covalenthq.com/v1/1',
                    getKey: () => '',
                    timeout: 10000,
                    rateLimit: RATE_LIMITS.DEFAULT
                }
            ]
        }
    },
    marketData: {
        primary: {
            name: 'CoinMarketCap',
            baseUrl: 'https://pro-api.coinmarketcap.com/v1',
            getKey: () => API_KEYS.CMC_PRIMARY,
            headerName: 'X-CMC_PRO_API_KEY',
            timeout: 10000,
            rateLimit: RATE_LIMITS.COINMARKETCAP
        },
        fallbacks: [
            {
                name: 'CoinMarketCapBackup',
                baseUrl: 'https://pro-api.coinmarketcap.com/v1',
                getKey: () => API_KEYS.CMC_BACKUP,
                headerName: 'X-CMC_PRO_API_KEY',
                timeout: 10000,
                rateLimit: RATE_LIMITS.COINMARKETCAP
            },
            {
                name: 'CoinGecko',
                baseUrl: 'https://api.coingecko.com/api/v3',
                getKey: () => '',
                timeout: 10000,
                rateLimit: RATE_LIMITS.COINGECKO
            },
            {
                name: 'CryptoCompare',
                baseUrl: 'https://min-api.cryptocompare.com/data',
                getKey: () => API_KEYS.CRYPTOCOMPARE,
                timeout: 10000,
                rateLimit: RATE_LIMITS.DEFAULT
            }
        ]
    },
    news: {
        primary: {
            name: 'NewsAPI',
            baseUrl: 'https://newsapi.org/v2',
            getKey: () => API_KEYS.NEWSAPI,
            timeout: 10000,
            rateLimit: RATE_LIMITS.NEWSAPI
        },
        fallbacks: [
            {
                name: 'CryptoPanic',
                baseUrl: 'https://cryptopanic.com/api/v1',
                getKey: () => '',
                timeout: 10000,
                rateLimit: RATE_LIMITS.DEFAULT
            }
        ]
    },
    sentiment: {
        primary: {
            name: 'AlternativeMe',
            baseUrl: 'https://api.alternative.me',
            getKey: () => '',
            timeout: 10000,
            rateLimit: RATE_LIMITS.DEFAULT
        },
        fallbacks: [
            {
                name: 'CoinGeckoSentiment',
                baseUrl: 'https://api.coingecko.com/api/v3',
                getKey: () => '',
                timeout: 10000,
                rateLimit: RATE_LIMITS.COINGECKO
            }
        ]
    },
    whaleTracking: {
        primary: {
            name: 'WhaleAlert',
            baseUrl: 'https://api.whale-alert.io/v1',
            getKey: () => API_KEYS.WHALEALERT,
            timeout: 15000,
            rateLimit: RATE_LIMITS.DEFAULT
        },
        fallbacks: []
    }
};

// Validate configuration on load (development only)
if (import.meta.env.DEV) {
    console.group('🔐 API Configuration Status');
    console.log('Real APIs Enabled:', FEATURE_FLAGS.USE_REAL_APIS);
    console.log('Cache Enabled:', FEATURE_FLAGS.ENABLE_CACHE);
    console.log('Debug Logging:', FEATURE_FLAGS.DEBUG_LOGGING);

    // Check which keys are configured
    const configuredKeys = Object.entries(API_KEYS)
        .filter(([_, value]) => value && value.length > 0)
        .map(([key]) => key);

    console.log('Configured API Keys:', configuredKeys);

    if (FEATURE_FLAGS.USE_REAL_APIS && configuredKeys.length === 0) {
        console.warn('⚠️  Real APIs enabled but no API keys configured!');
    }

    console.groupEnd();
}

export default API_CONFIG;
