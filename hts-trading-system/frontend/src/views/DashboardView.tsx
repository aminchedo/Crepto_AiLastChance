import React, { useState, useEffect } from 'react';
import PriceCard from '../components/PriceCard';
import RSIGauge from '../components/RSIGauge';
import MACDChart from '../components/MACDChart';
import SentimentGauge from '../components/SentimentGauge';
import AIPredictor from '../components/AIPredictor';
import NewsCard from '../components/NewsCard';
import { 
  WebSocketPriceUpdate, 
  SentimentData, 
  NewsArticle,
  ChartDataPoint 
} from '../types';
import { useFeatureFlags } from '../contexts/FeatureFlagContext';
import { FeatureGate, FeatureGateSimple } from '../contexts/FeatureFlagContext';

interface DashboardViewProps {
  priceData: Map<string, WebSocketPriceUpdate>;
  sentiment: SentimentData | null;
  news: NewsArticle[];
  symbols: string[];
  isLoading: boolean;
}

const DashboardView: React.FC<DashboardViewProps> = ({ 
  priceData, 
  sentiment, 
  news, 
  symbols, 
  isLoading 
}) => {
  const { isFeatureEnabled } = useFeatureFlags();
  const [chartHistory, setChartHistory] = useState<Map<string, ChartDataPoint[]>>(new Map());
  const [selectedSymbol, setSelectedSymbol] = useState('BTC');

  // Update chart history when price data changes
  useEffect(() => {
    priceData.forEach((data, symbol) => {
      setChartHistory(prev => {
        const history = prev.get(symbol) || [];
        const newPoint: ChartDataPoint = {
          time: Date.now(),
          macd: data.macd,
          signal: data.signal,
          histogram: data.histogram
        };

        // Keep only last 50 data points
        const updatedHistory = [...history, newPoint].slice(-50);
        return new Map(prev).set(symbol, updatedHistory);
      });
    });
  }, [priceData]);

  // Get current price data for selected symbol
  const currentPriceData = priceData.get(selectedSymbol);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            Trading Dashboard
          </h1>
          <p className="text-gray-400">
            Real-time cryptocurrency analysis and AI-powered insights
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-400">Live Data</span>
        </div>
      </div>

      {/* Price Cards */}
      <FeatureGateSimple feature="realTimeCharts">
        <section>
          <h2 className="text-2xl font-bold mb-4 flex items-center space-x-2">
            <span>💰</span>
            <span>Cryptocurrency Prices</span>
          </h2>
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[1, 2, 3].map(i => (
                <PriceCard
                  key={i}
                  symbol="BTC"
                  price={0}
                  change24h={0}
                  volume={0}
                  isLoading={true}
                />
              ))}
            </div>
          ) : symbols.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {symbols.slice(0, 6).map(symbol => {
                const data = priceData.get(symbol);
                return data ? (
                  <PriceCard
                    key={symbol}
                    symbol={symbol}
                    price={data.currentPrice}
                    change24h={0} // This would come from the data
                    volume={0} // This would come from the data
                  />
                ) : null;
              })}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <div className="text-6xl mb-4">📊</div>
              <p>No price data available</p>
              <p className="text-sm">Connecting to data sources...</p>
            </div>
          )}
        </section>
      </FeatureGateSimple>

      {/* Sentiment & AI Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Market Sentiment */}
        <FeatureGateSimple feature="marketSentiment">
          <div>
            <h3 className="text-xl font-bold mb-4 flex items-center space-x-2">
              <span>📊</span>
              <span>Market Sentiment</span>
            </h3>
            {sentiment ? (
              <SentimentGauge
                score={sentiment.overallScore}
                fearGreed={sentiment.fearGreed}
                reddit={sentiment.redditSentiment}
                coinGecko={sentiment.coinGeckoSentiment}
                trend={sentiment.trend}
                isLoading={isLoading}
              />
            ) : (
              <div className="sentiment-gauge animate-pulse">
                <div className="h-48 bg-gray-700 rounded-xl"></div>
              </div>
            )}
          </div>
        </FeatureGateSimple>

        {/* AI Predictor */}
        <FeatureGateSimple feature="aiPredictions">
          <div>
            <h3 className="text-xl font-bold mb-4 flex items-center space-x-2">
              <span>🤖</span>
              <span>AI Analysis</span>
            </h3>
            {currentPriceData ? (
              <AIPredictor
                symbol={selectedSymbol}
                prediction={currentPriceData.prediction}
                isLoading={isLoading}
              />
            ) : (
              <div className="ai-predictor animate-pulse">
                <div className="h-48 bg-gray-700 rounded-xl"></div>
              </div>
            )}
          </div>
        </FeatureGateSimple>
      </div>

      {/* Technical Analysis */}
      <FeatureGateSimple feature="realTimeCharts">
        <section>
          <h2 className="text-2xl font-bold mb-4 flex items-center space-x-2">
            <span>📈</span>
            <span>Technical Analysis</span>
          </h2>
          
          {/* Symbol Selection */}
          <div className="mb-6">
            <div className="flex flex-wrap gap-2">
              {symbols.map(symbol => (
                <button
                  key={symbol}
                  onClick={() => setSelectedSymbol(symbol)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    selectedSymbol === symbol
                      ? 'bg-blue-600 text-white shadow-lg'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  {symbol}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* RSI Gauge */}
            {currentPriceData ? (
              <div>
                <h3 className="text-lg font-semibold mb-3 flex items-center space-x-2">
                  <span>{selectedSymbol}</span>
                  <span className="text-gray-400">- RSI</span>
                </h3>
                <RSIGauge 
                  rsi={currentPriceData.rsi} 
                  trend={currentPriceData.rsiTrend}
                  isLoading={isLoading}
                />
              </div>
            ) : (
              <div className="sentiment-gauge animate-pulse">
                <div className="h-48 bg-gray-700 rounded-xl"></div>
              </div>
            )}

            {/* MACD Chart */}
            {currentPriceData && chartHistory.has(selectedSymbol) ? (
              <div>
                <h3 className="text-lg font-semibold mb-3 flex items-center space-x-2">
                  <span>{selectedSymbol}</span>
                  <span className="text-gray-400">- MACD</span>
                </h3>
                <MACDChart
                  data={chartHistory.get(selectedSymbol) || []}
                  currentMACD={{
                    macd: currentPriceData.macd,
                    signal: currentPriceData.signal,
                    histogram: currentPriceData.histogram,
                    trend: currentPriceData.macdTrend
                  }}
                  isLoading={isLoading}
                />
              </div>
            ) : (
              <div className="sentiment-gauge animate-pulse">
                <div className="h-48 bg-gray-700 rounded-xl"></div>
              </div>
            )}
          </div>
        </section>
      </FeatureGateSimple>

      {/* News Feed */}
      <FeatureGateSimple feature="newsFeed">
        <section>
          <h2 className="text-2xl font-bold mb-4 flex items-center space-x-2">
            <span>📰</span>
            <span>Latest News</span>
          </h2>
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="news-card animate-pulse">
                  <div className="h-40 bg-gray-700"></div>
                  <div className="p-4 space-y-2">
                    <div className="h-4 bg-gray-700 rounded w-3/4"></div>
                    <div className="h-3 bg-gray-700 rounded w-1/2"></div>
                    <div className="h-3 bg-gray-700 rounded w-1/4"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : news.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {news.slice(0, 6).map(article => (
                <NewsCard key={article.id} {...article} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <div className="text-6xl mb-4">📰</div>
              <p>No news articles available</p>
              <p className="text-sm">Loading latest news...</p>
            </div>
          )}
        </section>
      </FeatureGateSimple>

      {/* Feature Flags Info */}
      <FeatureGate feature="settings" showFeatureInfo={true}>
        <section className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 text-yellow-400">
            🚀 Advanced Features Available
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span>AI Predictions: Enabled</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span>Real-time Charts: Enabled</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span>Market Sentiment: Enabled</span>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                <span>Advanced Charts: 50% Rollout</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                <span>Alerts System: 60% Rollout</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                <span>Quantum AI: 5% Rollout</span>
              </div>
            </div>
          </div>
        </section>
      </FeatureGate>
    </div>
  );
};

export default DashboardView;