import React, { useState, useEffect } from 'react';
import PriceCard from '../components/PriceCard';
import RSIGauge from '../components/RSIGauge';
import MACDChart from '../components/MACDChart';
import SentimentGauge from '../components/SentimentGauge';
import AIPredictor from '../components/AIPredictor';
import NewsCard from '../components/NewsCard';
import { SentimentData, NewsArticle } from '../types/index';

interface ChartDataPoint {
  time: number;
  macd: number;
  signal: number;
  histogram: number;
}

interface Props {
  priceData: Map<string, any>;
  sentiment: SentimentData | null;
  news: NewsArticle[];
  symbols: string[];
}

const DashboardView: React.FC<Props> = ({ priceData, sentiment, news, symbols }) => {
  const [chartHistory, setChartHistory] = useState<Map<string, ChartDataPoint[]>>(
    new Map()
  );

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

        if (history.length > 50) {
          history.shift();
        }

        return new Map(prev).set(symbol, [...history, newPoint]);
      });
    });
  }, [priceData]);

  return (
    <div className="space-y-8">
      {/* Price Cards */}
      <section>
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
      </section>

      {/* Sentiment & AI */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {sentiment && (
          <div>
            <h3 className="text-xl font-bold mb-4">Market Sentiment</h3>
            <SentimentGauge
              score={sentiment.overallScore}
              fearGreed={sentiment.fearGreed}
              reddit={sentiment.redditSentiment}
              coinGecko={sentiment.coinGeckoSentiment}
              trend={sentiment.trend}
            />
          </div>
        )}

        <div>
          <h3 className="text-xl font-bold mb-4">AI Analysis</h3>
          {symbols.length > 0 && (
            <AIPredictor
              symbol={symbols[0]}
              prediction={priceData.get(symbols[0])?.prediction || null}
            />
          )}
        </div>
      </section>

      {/* Technical Indicators */}
      <section>
        <h2 className="text-2xl font-bold mb-4">📊 Technical Analysis</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {symbols.map(symbol => {
            const data = priceData.get(symbol);
            const history = chartHistory.get(symbol) || [];

            return data && history.length > 0 ? (
              <div key={symbol}>
                <h3 className="text-lg font-semibold mb-3">{symbol} - RSI</h3>
                <RSIGauge rsi={data.rsi} trend={data.rsiTrend} />
              </div>
            ) : null;
          })}

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
      </section>

      {/* News Feed */}
      <section>
        <h2 className="text-2xl font-bold mb-4">📰 Latest News</h2>
        {news.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {news.slice(0, 6).map(article => (
              <NewsCard key={article.id} {...article} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-400">
            Loading news articles...
          </div>
        )}
      </section>
    </div>
  );
};

export default DashboardView;
