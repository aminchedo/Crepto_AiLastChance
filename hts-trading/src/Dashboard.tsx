import React, { useState, useEffect } from 'react';
import useWebSocket from './hooks/useWebSocket';
import PriceCard from './components/PriceCard';
import RSIGauge from './components/RSIGauge';
import MACDChart from './components/MACDChart';
import SentimentGauge from './components/SentimentGauge';
import NewsCard from './components/NewsCard';
import StatusBar from './components/StatusBar';

interface ChartData {
  time: number;
  macd: number;
  signal: number;
  histogram: number;
}

const Dashboard: React.FC = () => {
  const { priceData, sentiment, news, connected, lastUpdate } = useWebSocket();
  const [chartHistory, setChartHistory] = useState<Map<string, ChartData[]>>(new Map());
  const [activeTab, setActiveTab] = useState<'overview' | 'charts' | 'news'>('overview');

  useEffect(() => {
    // Build chart history
    priceData.forEach((data, symbol) => {
      setChartHistory(prev => {
        const history = prev.get(symbol) || [];
        const newPoint: ChartData = {
          time: Date.now(),
          macd: data.macd,
          signal: data.signal,
          histogram: data.histogram,
        };

        if (history.length > 50) {
          history.shift();
        }

        return new Map(prev).set(symbol, [...history, newPoint]);
      });
    });
  }, [priceData]);

  const symbols = Array.from(priceData.keys()).sort();

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 via-gray-900 to-gray-950 text-white">
      {/* Status Bar */}
      <StatusBar connected={connected} lastUpdate={lastUpdate} />

      {/* Header */}
      <div className="px-6 py-8 border-b border-gray-800">
        <h1 className="text-4xl font-bold mb-2">
          🚀 Hybrid Trading System
        </h1>
        <p className="text-gray-400">
          Professional algorithmic cryptocurrency trading analysis
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="sticky top-0 bg-gray-900/95 border-b border-gray-800 px-6 z-10">
        <div className="flex gap-2 py-4">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 rounded-lg font-semibold transition-all ${
              activeTab === 'overview'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            📊 Overview
          </button>
          <button
            onClick={() => setActiveTab('charts')}
            className={`px-4 py-2 rounded-lg font-semibold transition-all ${
              activeTab === 'charts'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            📈 Charts
          </button>
          <button
            onClick={() => setActiveTab('news')}
            className={`px-4 py-2 rounded-lg font-semibold transition-all ${
              activeTab === 'news'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            📰 News
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Price Cards */}
            <div>
              <h2 className="text-2xl font-bold mb-4">💰 Cryptocurrency Prices</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {symbols.map(symbol => {
                  const data = priceData.get(symbol);
                  return data ? (
                    <PriceCard
                      key={symbol}
                      symbol={symbol}
                      price={data.currentPrice}
                      change24h={0}
                      volume={0}
                    />
                  ) : null;
                })}
              </div>
            </div>

            {/* Sentiment */}
            {sentiment && (
              <div>
                <h2 className="text-2xl font-bold mb-4">Market Sentiment Analysis</h2>
                <SentimentGauge
                  score={sentiment.overallScore}
                  fearGreed={sentiment.fearGreed}
                  reddit={sentiment.redditSentiment}
                  coinGecko={sentiment.coinGeckoSentiment}
                  trend={sentiment.trend}
                />
              </div>
            )}
          </div>
        )}

        {/* CHARTS TAB */}
        {activeTab === 'charts' && (
          <div>
            <h2 className="text-2xl font-bold mb-4">📊 Technical Analysis</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* RSI Indicators */}
              {symbols.map(symbol => {
                const data = priceData.get(symbol);
                return data ? (
                  <div key={`rsi-${symbol}`}>
                    <h3 className="text-lg font-semibold mb-3">{symbol} - RSI</h3>
                    <RSIGauge rsi={data.rsi} trend={data.rsiTrend} />
                  </div>
                ) : null;
              })}

              {/* MACD Charts */}
              {symbols.map(symbol => {
                const data = priceData.get(symbol);
                const history = chartHistory.get(symbol) || [];
                return data && history.length > 0 ? (
                  <div key={`macd-${symbol}`}>
                    <h3 className="text-lg font-semibold mb-3">{symbol} - MACD</h3>
                    <MACDChart
                      data={history}
                      currentMACD={{
                        macd: data.macd,
                        signal: data.signal,
                        histogram: data.histogram,
                        trend: data.macdTrend
                      }}
                    />
                  </div>
                ) : null;
              })}
            </div>
          </div>
        )}

        {/* NEWS TAB */}
        {activeTab === 'news' && (
          <div>
            <h2 className="text-2xl font-bold mb-4">📰 Latest Crypto News</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {news.map(article => (
                <NewsCard
                  key={article.id}
                  title={article.title}
                  description={article.description}
                  image={article.image}
                  url={article.url}
                  source={article.source}
                  published={article.published}
                  sentiment={article.sentiment}
                />
              ))}
            </div>
          </div>
        )}

        {/* Loading State */}
        {!connected && (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-400">Connecting to trading system...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;