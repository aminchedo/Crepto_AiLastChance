/**
 * Example Component: Using Proxy API Service
 * This shows how to properly integrate the proxy API in your React components
 */

import React, { useEffect, useState } from 'react';
import { proxyApi } from '../services/ProxyApiService';
import type { FearGreedData, NewsArticle } from '../services/ProxyApiService';

interface MarketData {
  symbol: string;
  name: string;
  price: number;
  change24h: number;
}

export const ProxyApiExample: React.FC = () => {
  const [fearGreed, setFearGreed] = useState<FearGreedData | null>(null);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load Fear & Greed Index
      const fearGreedData = await proxyApi.getFearGreedIndex(1);
      setFearGreed(fearGreedData[0]);

      // Load Top Cryptocurrencies
      const cmcData = await proxyApi.getCMCListings(1, 10);
      const formatted = cmcData.data.map((coin: any) => ({
        symbol: coin.symbol,
        name: coin.name,
        price: coin.quote.USD.price,
        change24h: coin.quote.USD.percent_change_24h,
      }));
      setMarketData(formatted);

      // Load News
      const newsData = await proxyApi.getCryptoNews('cryptocurrency', 5);
      setNews(newsData);

      setLoading(false);
    } catch (err) {
      console.error('Error loading data:', err);
      setError('Failed to load data. Make sure proxy server is running.');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Loading data from proxy...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>
          {error}
          <button onClick={loadData} style={styles.retryButton}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Proxy API Example</h1>

      {/* Fear & Greed Index */}
      {fearGreed && (
        <div style={styles.card}>
          <h2>Market Sentiment</h2>
          <div style={styles.fearGreedValue}>
            {fearGreed.value}/100
          </div>
          <div style={styles.fearGreedLabel}>
            {fearGreed.value_classification}
          </div>
        </div>
      )}

      {/* Market Data */}
      <div style={styles.card}>
        <h2>Top Cryptocurrencies</h2>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Symbol</th>
              <th style={styles.th}>Name</th>
              <th style={styles.th}>Price</th>
              <th style={styles.th}>24h Change</th>
            </tr>
          </thead>
          <tbody>
            {marketData.map((coin) => (
              <tr key={coin.symbol}>
                <td style={styles.td}>{coin.symbol}</td>
                <td style={styles.td}>{coin.name}</td>
                <td style={styles.td}>${coin.price.toLocaleString()}</td>
                <td
                  style={{
                    ...styles.td,
                    color: coin.change24h >= 0 ? '#10b981' : '#ef4444',
                  }}
                >
                  {coin.change24h.toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* News */}
      <div style={styles.card}>
        <h2>Latest News</h2>
        {news.map((article, index) => (
          <div key={index} style={styles.newsItem}>
            <h3 style={styles.newsTitle}>{article.title}</h3>
            <p style={styles.newsDescription}>{article.description}</p>
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              style={styles.newsLink}
            >
              Read more →
            </a>
          </div>
        ))}
      </div>

      <button onClick={loadData} style={styles.refreshButton}>
        Refresh Data
      </button>
    </div>
  );
};

// Styles
const styles: { [key: string]: React.CSSProperties } = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    marginBottom: '30px',
    textAlign: 'center',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '10px',
    padding: '20px',
    marginBottom: '20px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
  },
  loading: {
    textAlign: 'center',
    padding: '50px',
    fontSize: '18px',
  },
  error: {
    textAlign: 'center',
    padding: '50px',
    color: '#ef4444',
    fontSize: '18px',
  },
  retryButton: {
    marginTop: '20px',
    padding: '10px 20px',
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '16px',
  },
  fearGreedValue: {
    fontSize: '48px',
    fontWeight: 'bold',
    textAlign: 'center',
    margin: '20px 0',
  },
  fearGreedLabel: {
    fontSize: '24px',
    textAlign: 'center',
    color: '#666',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  th: {
    textAlign: 'left',
    padding: '12px',
    borderBottom: '2px solid #e5e7eb',
    fontWeight: 'bold',
  },
  td: {
    padding: '12px',
    borderBottom: '1px solid #e5e7eb',
  },
  newsItem: {
    marginBottom: '20px',
    paddingBottom: '20px',
    borderBottom: '1px solid #e5e7eb',
  },
  newsTitle: {
    fontSize: '18px',
    fontWeight: 'bold',
    marginBottom: '10px',
  },
  newsDescription: {
    color: '#666',
    marginBottom: '10px',
  },
  newsLink: {
    color: '#3b82f6',
    textDecoration: 'none',
    fontWeight: 'bold',
  },
  refreshButton: {
    padding: '12px 24px',
    backgroundColor: '#10b981',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '16px',
    display: 'block',
    margin: '20px auto',
  },
};

export default ProxyApiExample;
