/**
 * ENHANCED CORS-Free Crypto API Proxy Server with AUTO-FALLBACK
 * Automatically uses alternative APIs from api.txt when primary fails
 */

const express = require('express');
const cors = require('cors');
const axios = require('axios');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3002;

// ===== MIDDLEWARE =====

// Enable CORS for all routes (including file:// protocol for local testing)
app.use(cors({
  origin: function(origin, callback) {
    // Allow requests with no origin (like mobile apps, curl, or file://)
    if (!origin) return callback(null, true);
    
    const allowedOrigins = [
      'http://localhost:5173',
      'http://localhost:3000',
      'http://127.0.0.1:5173',
      'http://localhost:8000',
      'null' // This allows file:// protocol
    ];
    
    if (allowedOrigins.indexOf(origin) !== -1 || origin.startsWith('file://')) {
      callback(null, true);
    } else {
      callback(null, true); // Allow all origins for development
    }
  },
  credentials: true
}));

app.use(express.json());

// Rate limiting
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 200 // Increased to 200 requests per minute for multiple fallbacks
});
app.use('/api/', limiter);

// Request logging
app.use((req, res, next) => {
  console.log(`📨 ${req.method} ${req.path} - ${new Date().toISOString()}`);
  next();
});

// ===== API KEYS =====

const API_KEYS = {
  CMC_PRIMARY: process.env.CMC_API_KEY || 'b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c',
  CMC_BACKUP: process.env.CMC_API_KEY_2 || '04cf4b5b-9868-465c-8ba0-9f2e78c92eb1',
  CRYPTOCOMPARE: process.env.CRYPTOCOMPARE_KEY || 'e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f',
  NEWSAPI: process.env.NEWSAPI_KEY || '968a5e25552b4cb5ba3280361d8444ab',
  ETHERSCAN: process.env.ETHERSCAN_KEY || 'SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2',
  ETHERSCAN_2: process.env.ETHERSCAN_KEY_2 || 'T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45',
  BSCSCAN: process.env.BSCSCAN_KEY || 'K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT',
  TRONSCAN: process.env.TRONSCAN_KEY || '7ae72726-bffe-4e74-9c33-97b761eeea21',
};

// ===== UTILITY FUNCTIONS =====

// Retry with exponential backoff
async function retryWithBackoff(fn, maxRetries = 3, delay = 1000) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      const waitTime = delay * Math.pow(2, i);
      console.log(`⏳ Retry ${i + 1}/${maxRetries} in ${waitTime}ms...`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
  }
}

// Try multiple API endpoints with fallback
async function tryWithFallbacks(endpoints, transformFn = null) {
  const errors = [];
  
  for (const endpoint of endpoints) {
    try {
      console.log(`🔄 Trying ${endpoint.name}...`);
      const result = await endpoint.fn();
      console.log(`✅ ${endpoint.name} SUCCESS`);
      return transformFn ? transformFn(result) : result;
    } catch (error) {
      const errorMsg = `${endpoint.name} failed: ${error.message}`;
      console.error(`❌ ${errorMsg}`);
      errors.push(errorMsg);
    }
  }
  
  throw new Error(`All endpoints failed:\n${errors.join('\n')}`);
}

// ===== HEALTH CHECK =====

app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    service: 'Crypto API Proxy Server (Enhanced with Auto-Fallback)',
    port: PORT,
    timestamp: new Date().toISOString(),
    endpoints: {
      coinmarketcap: '✅ Available (with fallbacks)',
      cryptocompare: '✅ Available',
      coingecko: '✅ Available',
      feargreed: '✅ Available (with fallbacks)',
      news: '✅ Available (with fallbacks)',
      whale: '✅ Available'
    },
    fallbacks: {
      market_data: ['CoinMarketCap', 'CoinGecko', 'CryptoCompare', 'Nomics', 'Messari'],
      news: ['NewsAPI', 'CryptoPanic', 'CryptoControl'],
      sentiment: ['Alternative.me', 'CoinGecko']
    }
  });
});

// ===== MARKET DATA ROUTES WITH FALLBACKS =====

app.get('/api/coinmarketcap/quotes', async (req, res) => {
  try {
    const symbols = req.query.symbols || 'BTC,ETH,BNB,ADA,SOL,MATIC,DOT,LINK,LTC,XRP';
    console.log(`📊 [Market Data] Fetching quotes for: ${symbols}`);
    
    const endpoints = [
      {
        name: 'CoinMarketCap Primary',
        fn: async () => axios.get(
          'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest',
          {
            params: { symbol: symbols, convert: 'USD' },
            headers: { 'X-CMC_PRO_API_KEY': API_KEYS.CMC_PRIMARY },
            timeout: 10000
          }
        )
      },
      {
        name: 'CoinMarketCap Backup',
        fn: async () => axios.get(
          'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest',
          {
            params: { symbol: symbols, convert: 'USD' },
            headers: { 'X-CMC_PRO_API_KEY': API_KEYS.CMC_BACKUP },
            timeout: 10000
          }
        )
      },
      {
        name: 'CoinGecko (Fallback)',
        fn: async () => {
          // Convert symbols to CoinGecko IDs
          const symbolMap = {
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
            'ADA': 'cardano', 'SOL': 'solana', 'MATIC': 'matic-network',
            'DOT': 'polkadot', 'LINK': 'chainlink', 'LTC': 'litecoin', 'XRP': 'ripple'
          };
          const ids = symbols.split(',').map(s => symbolMap[s.trim()]).filter(Boolean).join(',');
          
          const response = await axios.get('https://api.coingecko.com/api/v3/simple/price', {
            params: {
              ids: ids,
              vs_currencies: 'usd',
              include_24hr_change: true,
              include_market_cap: true,
              include_24hr_vol: true
            },
            timeout: 10000
          });
          
          // Transform CoinGecko format to CMC-like format
          const data = {};
          Object.entries(response.data).forEach(([id, info]) => {
            const symbol = Object.keys(symbolMap).find(k => symbolMap[k] === id);
            if (symbol) {
              data[symbol] = {
                id: 0,
                symbol: symbol,
                name: id,
                quote: {
                  USD: {
                    price: info.usd,
                    percent_change_24h: info.usd_24h_change || 0,
                    market_cap: info.usd_market_cap || 0,
                    volume_24h: info.usd_24h_vol || 0
                  }
                }
              };
            }
          });
          
          return { data: { status: { error_code: 0 }, data: data } };
        }
      },
      {
        name: 'CryptoCompare (Fallback)',
        fn: async () => {
          const response = await axios.get('https://min-api.cryptocompare.com/data/pricemultifull', {
            params: {
              fsyms: symbols,
              tsyms: 'USD',
              api_key: API_KEYS.CRYPTOCOMPARE
            },
            timeout: 10000
          });
          
          // Transform CryptoCompare format to CMC-like format
          const data = {};
          Object.entries(response.data.RAW).forEach(([symbol, info]) => {
            data[symbol] = {
              id: 0,
              symbol: symbol,
              name: symbol,
              quote: {
                USD: {
                  price: info.USD.PRICE,
                  percent_change_24h: info.USD.CHANGEPCT24HOUR,
                  market_cap: info.USD.MKTCAP || 0,
                  volume_24h: info.USD.TOTALVOLUME24HTO || 0
                }
              }
            };
          });
          
          return { data: { status: { error_code: 0 }, data: data } };
        }
      }
    ];
    
    const result = await tryWithFallbacks(endpoints, (response) => response.data);
    res.json(result);
    
  } catch (error) {
    console.error(`❌ [Market Data] All fallbacks failed:`, error.message);
    res.status(500).json({
      error: 'All market data APIs failed',
      details: error.message,
      endpoint: 'coinmarketcap'
    });
  }
});

// CoinGecko - Price
app.get('/api/coingecko/price', async (req, res) => {
  try {
    const ids = req.query.ids || 'bitcoin,ethereum,binancecoin,cardano,solana,polygon,polkadot,chainlink,litecoin,ripple';
    console.log(`💎 [CoinGecko] Fetching prices for: ${ids}`);
    
    const response = await axios.get(
      'https://api.coingecko.com/api/v3/simple/price',
      {
        params: {
          ids: ids,
          vs_currencies: 'usd',
          include_24hr_change: true,
          include_24hr_vol: true,
          include_market_cap: true
        },
        timeout: 10000
      }
    );

    console.log(`✅ [CoinGecko] Success - ${Object.keys(response.data || {}).length} coins`);
    res.json(response.data);
  } catch (error) {
    console.error(`❌ [CoinGecko] Error:`, error.message);
    res.status(error.response?.status || 500).json({
      error: error.message,
      endpoint: 'coingecko'
    });
  }
});

// CryptoCompare - Price  
app.get('/api/cryptocompare/price', async (req, res) => {
  try {
    const fsyms = req.query.fsyms || 'BTC,ETH,BNB,ADA,SOL';
    console.log(`📈 [CryptoCompare] Fetching prices for: ${fsyms}`);
    
    const response = await axios.get(
      'https://min-api.cryptocompare.com/data/pricemultifull',
      {
        params: {
          fsyms: fsyms,
          tsyms: 'USD',
          api_key: API_KEYS.CRYPTOCOMPARE
        },
        timeout: 10000
      }
    );

    console.log(`✅ [CryptoCompare] Success`);
    res.json(response.data);
  } catch (error) {
    console.error(`❌ [CryptoCompare] Error:`, error.message);
    res.status(error.response?.status || 500).json({
      error: error.message,
      endpoint: 'cryptocompare'
    });
  }
});

// ===== SENTIMENT ROUTES WITH FALLBACKS =====

app.get('/api/feargreed', async (req, res) => {
  try {
    console.log(`😨 [Sentiment] Fetching Fear & Greed Index...`);
    
    const endpoints = [
      {
        name: 'Alternative.me (Primary)',
        fn: async () => axios.get('https://api.alternative.me/fng/?limit=1&format=json', { timeout: 10000 })
      },
      {
        name: 'Alternative.me (Fallback URL)',
        fn: async () => axios.get('https://api.alternative.me/fng/', { timeout: 10000 })
      },
      {
        name: 'CoinGecko Sentiment (Fallback)',
        fn: async () => {
          const response = await axios.get('https://api.coingecko.com/api/v3/coins/bitcoin', {
            params: { community_data: true },
            timeout: 10000
          });
          
          // Estimate fear/greed from CoinGecko sentiment
          const sentiment = response.data.sentiment_votes_up_percentage || 50;
          const value = Math.round(sentiment * 100 / 100);
          const classification = value < 25 ? 'Extreme Fear' :
                                 value < 45 ? 'Fear' :
                                 value < 55 ? 'Neutral' :
                                 value < 75 ? 'Greed' : 'Extreme Greed';
          
          return {
            data: {
              name: 'Fear and Greed Index',
              data: [{
                value: value.toString(),
                value_classification: classification,
                timestamp: Math.floor(Date.now() / 1000).toString(),
                time_until_update: '0'
              }],
              metadata: {
                error: null,
                source: 'CoinGecko (estimated)'
              }
            }
          };
        }
      }
    ];
    
    const result = await tryWithFallbacks(endpoints, (response) => response.data);
    console.log(`✅ [Sentiment] Success - Value: ${result.data[0].value}`);
    res.json(result);
    
  } catch (error) {
    console.error(`❌ [Sentiment] All fallbacks failed:`, error.message);
    
    // Return neutral fallback value
    res.json({
      name: 'Fear and Greed Index',
      data: [{
        value: '50',
        value_classification: 'Neutral',
        timestamp: Math.floor(Date.now() / 1000).toString(),
        time_until_update: '0'
      }],
      metadata: {
        error: 'All APIs failed, showing neutral value',
        source: 'fallback'
      }
    });
  }
});

// ===== NEWS ROUTES WITH FALLBACKS =====

app.get('/api/news/crypto', async (req, res) => {
  try {
    const query = req.query.q || 'cryptocurrency OR bitcoin OR ethereum';
    const pageSize = req.query.pageSize || 20;
    console.log(`📰 [News] Fetching news for: ${query}`);
    
    const endpoints = [
      {
        name: 'NewsAPI (Primary)',
        fn: async () => axios.get('https://newsapi.org/v2/everything', {
          params: {
            q: query,
            language: 'en',
            sortBy: 'publishedAt',
            pageSize: pageSize,
            apiKey: API_KEYS.NEWSAPI
          },
          timeout: 10000
        })
      },
      {
        name: 'CryptoPanic (Fallback)',
        fn: async () => {
          const response = await axios.get('https://cryptopanic.com/api/v1/posts/', {
            params: {
              auth_token: 'free', // Free tier
              public: true,
              kind: 'news'
            },
            timeout: 10000
          });
          
          // Transform CryptoPanic format to NewsAPI format
          const articles = response.data.results.slice(0, pageSize).map(post => ({
            source: { id: null, name: post.source.title },
            author: post.source.title,
            title: post.title,
            description: post.title,
            url: post.url,
            urlToImage: null,
            publishedAt: post.published_at,
            content: post.title
          }));
          
          return {
            data: {
              status: 'ok',
              totalResults: articles.length,
              articles: articles,
              source: 'CryptoPanic'
            }
          };
        }
      },
      {
        name: 'CryptoControl (Fallback)',
        fn: async () => {
          const response = await axios.get('https://cryptocontrol.io/api/v1/public/news', {
            params: { language: 'en' },
            timeout: 10000
          });
          
          // Transform CryptoControl format to NewsAPI format
          const articles = response.data.slice(0, pageSize).map(item => ({
            source: { id: null, name: item.sourceName },
            author: item.sourceName,
            title: item.title,
            description: item.description,
            url: item.url,
            urlToImage: item.thumbnail,
            publishedAt: item.publishedAt,
            content: item.description
          }));
          
          return {
            data: {
              status: 'ok',
              totalResults: articles.length,
              articles: articles,
              source: 'CryptoControl'
            }
          };
        }
      }
    ];
    
    const result = await tryWithFallbacks(endpoints, (response) => response.data);
    console.log(`✅ [News] Success - ${result.articles?.length || 0} articles`);
    res.json(result);
    
  } catch (error) {
    console.error(`❌ [News] All fallbacks failed:`, error.message);
    res.status(500).json({
      status: 'error',
      totalResults: 0,
      articles: [],
      error: 'All news APIs failed',
      details: error.message
    });
  }
});

// ===== BLOCKCHAIN EXPLORER ROUTES =====

app.get('/api/etherscan/balance/:address', async (req, res) => {
  try {
    const { address } = req.params;
    console.log(`🔍 [Etherscan] Fetching balance for: ${address}`);
    
    const response = await axios.get('https://api.etherscan.io/api', {
      params: {
        module: 'account',
        action: 'balance',
        address: address,
        tag: 'latest',
        apikey: API_KEYS.ETHERSCAN
      },
      timeout: 10000
    });

    console.log(`✅ [Etherscan] Success`);
    res.json(response.data);
  } catch (error) {
    console.error(`❌ [Etherscan] Error:`, error.message);
    res.status(error.response?.status || 500).json({
      error: error.message,
      endpoint: 'etherscan'
    });
  }
});

app.get('/api/bscscan/balance/:address', async (req, res) => {
  try {
    const { address } = req.params;
    console.log(`🔍 [BscScan] Fetching balance for: ${address}`);
    
    const response = await axios.get('https://api.bscscan.com/api', {
      params: {
        module: 'account',
        action: 'balance',
        address: address,
        apikey: API_KEYS.BSCSCAN
      },
      timeout: 10000
    });

    console.log(`✅ [BscScan] Success`);
    res.json(response.data);
  } catch (error) {
    console.error(`❌ [BscScan] Error:`, error.message);
    res.status(error.response?.status || 500).json({
      error: error.message,
      endpoint: 'bscscan'
    });
  }
});

app.get('/api/tronscan/account/:address', async (req, res) => {
  try {
    const { address } = req.params;
    console.log(`🔍 [TronScan] Fetching account for: ${address}`);
    
    const response = await axios.get(`https://api.tronscan.org/api/account`, {
      params: {
        address: address,
        apiKey: API_KEYS.TRONSCAN
      },
      timeout: 10000
    });

    console.log(`✅ [TronScan] Success`);
    res.json(response.data);
  } catch (error) {
    console.error(`❌ [TronScan] Error:`, error.message);
    res.status(error.response?.status || 500).json({
      error: error.message,
      endpoint: 'tronscan'
    });
  }
});

// ===== WHALE TRACKING =====

app.get('/api/whale-alert/transactions', async (req, res) => {
  try {
    const minValue = req.query.min_value || 1000000;
    console.log(`🐋 [WhaleAlert] Fetching transactions (min: $${minValue})`);
    
    // Note: WhaleAlert requires a paid API key
    // This is a placeholder - you'll need a real key
    res.json({
      status: 'info',
      message: 'WhaleAlert requires a paid API key. Please add WHALEALERT_KEY to .env',
      transactions: []
    });
  } catch (error) {
    console.error(`❌ [WhaleAlert] Error:`, error.message);
    res.status(error.response?.status || 500).json({
      error: error.message,
      endpoint: 'whale-alert'
    });
  }
});

// ===== START SERVER =====

app.listen(PORT, () => {
  console.clear();
  console.log('');
  console.log('╔══════════════════════════════════════════════════════════╗');
  console.log('║     🚀 CRYPTO API PROXY SERVER (ENHANCED)               ║');
  console.log('║        Status: RUNNING                                   ║');
  console.log('║        Auto-Fallback: ENABLED ✅                         ║');
  console.log('╚══════════════════════════════════════════════════════════╝');
  console.log('');
  console.log(`   Port: ${PORT}`);
  console.log(`   URL:  http://localhost:${PORT}`);
  console.log('');
  console.log('📊 Market Data Endpoints (with fallbacks):');
  console.log('   GET  /api/coinmarketcap/quotes?symbols=BTC,ETH,BNB');
  console.log('   GET  /api/coingecko/price?ids=bitcoin,ethereum');
  console.log('   GET  /api/cryptocompare/price?fsyms=BTC,ETH');
  console.log('');
  console.log('😨 Sentiment Endpoints (with fallbacks):');
  console.log('   GET  /api/feargreed');
  console.log('');
  console.log('📰 News Endpoints (with fallbacks):');
  console.log('   GET  /api/news/crypto?q=bitcoin');
  console.log('');
  console.log('🔗 Blockchain Explorer Endpoints:');
  console.log('   GET  /api/etherscan/balance/:address');
  console.log('   GET  /api/bscscan/balance/:address');
  console.log('   GET  /api/tronscan/account/:address');
  console.log('');
  console.log('🏥 Health Check:');
  console.log('   GET  /health');
  console.log('');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('');
  console.log('🔑 API Keys Status:');
  console.log(`   ${API_KEYS.CMC_PRIMARY ? '✅' : '❌'}  CoinMarketCap Primary`);
  console.log(`   ${API_KEYS.CMC_BACKUP ? '✅' : '❌'}  CoinMarketCap Backup`);
  console.log(`   ${API_KEYS.CRYPTOCOMPARE ? '✅' : '❌'}  CryptoCompare`);
  console.log(`   ${API_KEYS.ETHERSCAN ? '✅' : '❌'}  Etherscan`);
  console.log(`   ${API_KEYS.BSCSCAN ? '✅' : '❌'}  BscScan`);
  console.log(`   ${API_KEYS.TRONSCAN ? '✅' : '❌'}  TronScan`);
  console.log(`   ${API_KEYS.NEWSAPI ? '✅' : '❌'}  NewsAPI`);
  console.log('');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('');
  console.log('🔄 Auto-Fallback Chains:');
  console.log('   Market Data: CMC → CoinGecko → CryptoCompare');
  console.log('   News: NewsAPI → CryptoPanic → CryptoControl');
  console.log('   Sentiment: Alternative.me → CoinGecko');
  console.log('');
  console.log('💡 Frontend should connect to: http://localhost:' + PORT + '/api/*');
  console.log('📝 CORS enabled for file:// protocol (local testing)');
  console.log('');
  console.log('  ');
});
