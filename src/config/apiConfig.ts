export const API_CONFIG = {
  // ========================================
  // 1. BLOCKCHAIN EXPLORER APIs
  // ========================================
  blockchain: {
    tronscan: {
      primary: {
        name: 'tronscan',
        baseUrl: 'https://api.tronscan.org/api',
        key: '7ae72726-bffe-4e74-9c33-97b761eeea21',
        timeout: 10000,
        priority: 1
      },
      fallback: {
        name: 'trongrid',
        baseUrl: 'https://api.trongrid.io',
        key: '7ae72726-bffe-4e74-9c33-97b761eeea21',
        timeout: 10000,
        priority: 2
      }
    },
    bscscan: {
      primary: {
        name: 'bscscan',
        baseUrl: 'https://api.bscscan.com/api',
        key: 'K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT',
        timeout: 10000,
        priority: 1
      },
      fallback: {
        name: 'ankrscan',
        baseUrl: 'https://rpc.ankr.com/bsc',
        key: '',
        timeout: 10000,
        priority: 2
      }
    },
    etherscan: {
      primary: {
        name: 'etherscan',
        baseUrl: 'https://api.etherscan.io/api',
        key: 'SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2',
        timeout: 10000,
        priority: 1
      },
      fallback: {
        name: 'etherscan_2',
        baseUrl: 'https://api.etherscan.io/api',
        key: 'T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45',
        timeout: 10000,
        priority: 2
      }
    }
  },

  // ========================================
  // 2. MARKET DATA APIs
  // ========================================
  marketData: {
    coinmarketcap: {
      primary: {
        name: 'coinmarketcap',
        baseUrl: 'https://pro-api.coinmarketcap.com/v1',
        key: 'b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c',
        timeout: 10000,
        priority: 1
      },
      fallback: {
        name: 'coinmarketcap_alt',
        baseUrl: 'https://pro-api.coinmarketcap.com/v1',
        key: '04cf4b5b-9868-465c-8ba0-9f2e78c92eb1',
        timeout: 10000,
        priority: 2
      }
    },
    cryptocompare: {
      primary: {
        name: 'cryptocompare',
        baseUrl: 'https://min-api.cryptocompare.com/data',
        key: 'e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f',
        timeout: 10000,
        priority: 1
      }
    },
    coingecko: {
      primary: {
        name: 'coingecko',
        baseUrl: 'https://api.coingecko.com/api/v3',
        key: '', // Free API, no key needed
        timeout: 10000,
        priority: 2
      }
    },
    coinapi: {
      primary: {
        name: 'coinapi',
        baseUrl: 'https://rest.coinapi.io/v1',
        key: '', // Add key if available
        timeout: 10000,
        priority: 3
      }
    },
    nomics: {
      primary: {
        name: 'nomics',
        baseUrl: 'https://api.nomics.com/v1',
        key: '', // Add key if available
        timeout: 10000,
        priority: 3
      }
    },
    messari: {
      primary: {
        name: 'messari',
        baseUrl: 'https://data.messari.io/api/v1',
        key: '', // Free tier available
        timeout: 10000,
        priority: 3
      }
    }
  },

  // ========================================
  // 3. NEWS & AGGREGATORS APIs
  // ========================================
  news: {
    newsapi: {
      primary: {
        name: 'newsapi',
        baseUrl: 'https://newsapi.org/v2',
        key: 'pub_346789abc123def456789ghi012345jkl',
        timeout: 10000,
        priority: 1
      }
    },
    cryptopanic: {
      primary: {
        name: 'cryptopanic',
        baseUrl: 'https://cryptopanic.com/api/v1',
        key: '', // Free tier available
        timeout: 10000,
        priority: 2
      }
    },
    cryptocontrol: {
      primary: {
        name: 'cryptocontrol',
        baseUrl: 'https://cryptocontrol.io/api/v1',
        key: '', // Add key if available
        timeout: 10000,
        priority: 3
      }
    },
    coindesk: {
      primary: {
        name: 'coindesk',
        baseUrl: 'https://www.coindesk.com/arc/outboundfeeds',
        key: '', // RSS feed, no key needed
        timeout: 10000,
        priority: 3
      }
    }
  },

  // ========================================
  // 4. SENTIMENT & SOCIAL APIs
  // ========================================
  sentiment: {
    fearGreed: {
      primary: {
        name: 'alternative_me',
        baseUrl: 'https://api.alternative.me/fng',
        key: '',
        timeout: 10000,
        priority: 1
      }
    },
    coingecko: {
      primary: {
        name: 'coingecko_sentiment',
        baseUrl: 'https://api.coingecko.com/api/v3',
        key: '',
        timeout: 10000,
        priority: 2
      }
    },
    lunarcrush: {
      primary: {
        name: 'lunarcrush',
        baseUrl: 'https://api.lunarcrush.com/v2',
        key: '', // Add key if available
        timeout: 10000,
        priority: 2
      }
    },
    reddit: {
      primary: {
        name: 'reddit',
        baseUrl: 'https://www.reddit.com',
        key: '',
        timeout: 10000,
        priority: 3
      }
    },
    twitter: {
      primary: {
        name: 'twitter_crypto',
        baseUrl: 'https://api.twitter.com/2',
        key: '', // Add key if available
        timeout: 10000,
        priority: 3
      }
    }
  },

  // ========================================
  // 5. WHALE TRACKING APIs
  // ========================================
  whale: {
    whaleAlert: {
      primary: {
        name: 'whale_alert',
        baseUrl: 'https://api.whale-alert.io/v1',
        key: '', // Add key if available
        timeout: 10000,
        priority: 1
      }
    },
    etherscan: {
      primary: {
        name: 'etherscan_whale',
        baseUrl: 'https://api.etherscan.io/api',
        key: 'SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2',
        timeout: 10000,
        priority: 2
      }
    },
    bscscan: {
      primary: {
        name: 'bscscan_whale',
        baseUrl: 'https://api.bscscan.com/api',
        key: 'K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT',
        timeout: 10000,
        priority: 2
      }
    }
  },

  // Legacy structure for backward compatibility
  tronscan: {
    primary: {
      name: 'tronscan',
      baseUrl: 'https://api.tronscan.org/api',
      key: '7ae72726-bffe-4e74-9c33-97b761eeea21',
      timeout: 10000
    },
    fallback: {
      name: 'trongrid',
      baseUrl: 'https://api.trongrid.io',
      key: '7ae72726-bffe-4e74-9c33-97b761eeea21',
      timeout: 10000
    }
  },
  bscscan: {
    primary: {
      name: 'bscscan',
      baseUrl: 'https://api.bscscan.com/api',
      key: 'K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT',
      timeout: 10000
    },
    fallback: {
      name: 'ankrscan',
      baseUrl: 'https://rpc.ankr.com/bsc',
      key: '',
      timeout: 10000
    }
  },
  etherscan: {
    primary: {
      name: 'etherscan',
      baseUrl: 'https://api.etherscan.io/api',
      key: 'SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2',
      timeout: 10000
    },
    fallback: {
      name: 'etherscan_2',
      baseUrl: 'https://api.etherscan.io/api',
      key: 'T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45',
      timeout: 10000
    }
  },
  coinmarketcap: {
    primary: {
      name: 'coinmarketcap',
      baseUrl: 'https://pro-api.coinmarketcap.com/v1',
      key: 'b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c',
      timeout: 10000
    },
    fallback: {
      name: 'coinmarketcap_alt',
      baseUrl: 'https://pro-api.coinmarketcap.com/v1',
      key: '04cf4b5b-9868-465c-8ba0-9f2e78c92eb1',
      timeout: 10000
    }
  },
  cryptocompare: {
    primary: {
      name: 'cryptocompare',
      baseUrl: 'https://min-api.cryptocompare.com/data',
      key: 'e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f',
      timeout: 10000
    }
  },
  newsapi: {
    primary: {
      name: 'newsapi',
      baseUrl: 'https://newsapi.org/v2',
      key: 'pub_346789abc123def456789ghi012345jkl',
      timeout: 10000
    },
    fallback: {
      name: 'cryptopanic',
      baseUrl: 'https://cryptopanic.com/api/v1',
      key: '',
      timeout: 10000
    }
  }
};

// CORS Proxy for development (DISABLED - causes header blocking issues)
// Using direct API calls instead - only use proxy for specific cases
export const CORS_PROXY = ''; // Disabled - was: 'https://api.allorigins.win/raw?url='
export const CORS_PROXY_FALLBACK = ''; // Disabled - use direct calls
export const USE_CORS_PROXY = false; // Global toggle to disable CORS proxies

// Centralized API URLs for easier management
export const API_URLS = {
  FEAR_GREED: {
    PRIMARY: 'https://api.allorigins.win/raw?url=https://api.alternative.me/fng/?limit=1&format=json',
    FALLBACK: 'https://corsproxy.io/?https://api.alternative.me/fng/?limit=1&format=json',
    DIRECT: 'https://api.alternative.me/fng/?limit=1&format=json'
  }
};

// Request configuration
export const REQUEST_CONFIG = {
  TIMEOUT: 10000, // 10 seconds
  MAX_RETRIES: 3,
  RETRY_DELAY_BASE: 1000, // 1 second base delay for exponential backoff
};

// Fallback values when APIs fail
export const FALLBACK_VALUES = {
  FEAR_GREED: { 
    data: [{ 
      value: '50', 
      value_classification: 'Neutral',
      timestamp: String(Math.floor(Date.now() / 1000)),
      time_until_update: '0'
    }]
  },
  DEFAULT_SENTIMENT: 50
};

// Rate limiting configuration
export const RATE_LIMITS = {
  coinmarketcap: { requests: 333, window: 86400000 }, // 333 requests per day
  cryptocompare: { requests: 100000, window: 2592000000 }, // 100k per month
  newsapi: { requests: 1000, window: 86400000 }, // 1000 per day
  coingecko: { requests: 50, window: 60000 }, // 50 per minute
  etherscan: { requests: 5, window: 1000 }, // 5 per second
  bscscan: { requests: 5, window: 1000 }, // 5 per second
  feargreed: { requests: 100, window: 60000 }, // 100 per minute
};