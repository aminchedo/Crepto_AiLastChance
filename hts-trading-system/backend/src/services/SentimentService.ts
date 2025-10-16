import axios, { AxiosResponse } from 'axios';
import { SentimentData } from '../types/index.js';
import { TradingSystemError } from '../types/index.js';

class SentimentService {
  private fearGreedApi: string;
  private coinGeckoApi: string;
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private cacheTtl: number;

  constructor() {
    this.fearGreedApi = process.env.FEAR_GREED_API || 'https://api.alternative.me/fng/';
    this.coinGeckoApi = process.env.COINGECKO_API || 'https://api.coingecko.com/api/v3';
    this.cacheTtl = parseInt(process.env.CACHE_TTL || '300') * 1000; // Convert to milliseconds
  }

  // ==================== CACHE MANAGEMENT ====================

  private getCached(key: string): any | null {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTtl) {
      return cached.data;
    }
    return null;
  }

  private setCache(key: string, data: any): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }

  // ==================== FEAR & GREED INDEX ====================

  async getFearGreedIndex(): Promise<number> {
    const cached = this.getCached('fear_greed');
    if (cached) return cached;

    try {
      const response: AxiosResponse = await axios.get(this.fearGreedApi, {
        params: { limit: 1 },
        timeout: 10000,
        headers: {
          'User-Agent': 'HTS-Trading-System/1.0.0'
        }
      });

      const value = parseInt(response.data.data[0].value);
      const normalizedValue = Math.max(0, Math.min(100, value));
      
      this.setCache('fear_greed', normalizedValue);
      return normalizedValue;
    } catch (error) {
      console.warn('⚠️ Fear & Greed Index fetch failed:', error);
      return 50; // Neutral fallback
    }
  }

  // ==================== REDDIT SENTIMENT ====================

  async getRedditSentiment(): Promise<number> {
    const cached = this.getCached('reddit_sentiment');
    if (cached) return cached;

    try {
      // In a real implementation, you would use Reddit API
      // For now, we'll simulate with some realistic patterns
      const baseSentiment = 45 + Math.sin(Date.now() / 1000000) * 10;
      const randomFactor = (Math.random() - 0.5) * 20;
      const sentiment = Math.max(0, Math.min(100, baseSentiment + randomFactor));
      
      this.setCache('reddit_sentiment', Math.round(sentiment));
      return Math.round(sentiment);
    } catch (error) {
      console.warn('⚠️ Reddit sentiment fetch failed:', error);
      return 50;
    }
  }

  // ==================== COINGECKO SENTIMENT ====================

  async getCoinGeckoSentiment(): Promise<number> {
    const cached = this.getCached('coingecko_sentiment');
    if (cached) return cached;

    try {
      // Simulate CoinGecko social sentiment
      const baseSentiment = 50 + Math.cos(Date.now() / 2000000) * 15;
      const randomFactor = (Math.random() - 0.5) * 15;
      const sentiment = Math.max(0, Math.min(100, baseSentiment + randomFactor));
      
      this.setCache('coingecko_sentiment', Math.round(sentiment));
      return Math.round(sentiment);
    } catch (error) {
      console.warn('⚠️ CoinGecko sentiment fetch failed:', error);
      return 50;
    }
  }

  // ==================== TWITTER SENTIMENT ====================

  async getTwitterSentiment(): Promise<number> {
    const cached = this.getCached('twitter_sentiment');
    if (cached) return cached;

    try {
      // Simulate Twitter sentiment analysis
      const baseSentiment = 48 + Math.sin(Date.now() / 1500000) * 12;
      const randomFactor = (Math.random() - 0.5) * 18;
      const sentiment = Math.max(0, Math.min(100, baseSentiment + randomFactor));
      
      this.setCache('twitter_sentiment', Math.round(sentiment));
      return Math.round(sentiment);
    } catch (error) {
      console.warn('⚠️ Twitter sentiment fetch failed:', error);
      return 50;
    }
  }

  // ==================== NEWS SENTIMENT ====================

  async getNewsSentiment(): Promise<number> {
    const cached = this.getCached('news_sentiment');
    if (cached) return cached;

    try {
      // Simulate news sentiment analysis
      const baseSentiment = 52 + Math.cos(Date.now() / 1800000) * 8;
      const randomFactor = (Math.random() - 0.5) * 12;
      const sentiment = Math.max(0, Math.min(100, baseSentiment + randomFactor));
      
      this.setCache('news_sentiment', Math.round(sentiment));
      return Math.round(sentiment);
    } catch (error) {
      console.warn('⚠️ News sentiment fetch failed:', error);
      return 50;
    }
  }

  // ==================== AGGREGATED SENTIMENT ====================

  async getAggregatedSentiment(): Promise<SentimentData> {
    try {
      const [fearGreed, reddit, coinGecko, twitter, news] = await Promise.allSettled([
        this.getFearGreedIndex(),
        this.getRedditSentiment(),
        this.getCoinGeckoSentiment(),
        this.getTwitterSentiment(),
        this.getNewsSentiment()
      ]);

      // Extract values with fallbacks
      const fearGreedValue = fearGreed.status === 'fulfilled' ? fearGreed.value : 50;
      const redditValue = reddit.status === 'fulfilled' ? reddit.value : 50;
      const coinGeckoValue = coinGecko.status === 'fulfilled' ? coinGecko.value : 50;
      const twitterValue = twitter.status === 'fulfilled' ? twitter.value : 50;
      const newsValue = news.status === 'fulfilled' ? news.value : 50;

      // Weighted average: Fear & Greed (40%), Social (35%), News (25%)
      const overallScore = Math.round(
        fearGreedValue * 0.4 +
        ((redditValue + coinGeckoValue + twitterValue) / 3) * 0.35 +
        newsValue * 0.25
      );

      // Determine trend
      let trend: 'extreme fear' | 'fear' | 'neutral' | 'greed' | 'extreme greed';
      if (overallScore < 20) trend = 'extreme fear';
      else if (overallScore < 40) trend = 'fear';
      else if (overallScore < 60) trend = 'neutral';
      else if (overallScore < 80) trend = 'greed';
      else trend = 'extreme greed';

      // Calculate confidence based on data consistency
      const values = [fearGreedValue, redditValue, coinGeckoValue, twitterValue, newsValue];
      const mean = values.reduce((a, b) => a + b, 0) / values.length;
      const variance = values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length;
      const confidence = Math.max(60, 100 - Math.sqrt(variance) * 2);

      const sentimentData: SentimentData = {
        fearGreed: fearGreedValue,
        redditSentiment: redditValue,
        coinGeckoSentiment: coinGeckoValue,
        twitterSentiment: twitterValue,
        overallScore,
        trend,
        confidence: Math.round(confidence),
        timestamp: Date.now()
      };

      console.log(`✅ Sentiment analysis complete: ${overallScore} (${trend})`);
      return sentimentData;
    } catch (error) {
      console.error('❌ Error getting aggregated sentiment:', error);
      throw new TradingSystemError(
        'Failed to get sentiment data',
        'SENTIMENT_ERROR',
        500,
        error
      );
    }
  }

  // ==================== SENTIMENT HISTORY ====================

  async getSentimentHistory(days: number = 7): Promise<SentimentData[]> {
    const cached = this.getCached(`sentiment_history_${days}`);
    if (cached) return cached;

    try {
      // Simulate historical sentiment data
      const history: SentimentData[] = [];
      const now = Date.now();
      const dayMs = 24 * 60 * 60 * 1000;

      for (let i = days; i >= 0; i--) {
        const timestamp = now - (i * dayMs);
        const baseScore = 50 + Math.sin(timestamp / 1000000) * 20;
        const randomFactor = (Math.random() - 0.5) * 15;
        const score = Math.max(0, Math.min(100, baseScore + randomFactor));

        let trend: 'extreme fear' | 'fear' | 'neutral' | 'greed' | 'extreme greed';
        if (score < 20) trend = 'extreme fear';
        else if (score < 40) trend = 'fear';
        else if (score < 60) trend = 'neutral';
        else if (score < 80) trend = 'greed';
        else trend = 'extreme greed';

        history.push({
          fearGreed: Math.round(score + (Math.random() - 0.5) * 10),
          redditSentiment: Math.round(score + (Math.random() - 0.5) * 15),
          coinGeckoSentiment: Math.round(score + (Math.random() - 0.5) * 12),
          twitterSentiment: Math.round(score + (Math.random() - 0.5) * 18),
          overallScore: Math.round(score),
          trend,
          confidence: Math.round(70 + Math.random() * 20),
          timestamp
        });
      }

      this.setCache(`sentiment_history_${days}`, history);
      return history;
    } catch (error) {
      console.error('❌ Error getting sentiment history:', error);
      return [];
    }
  }

  // ==================== SENTIMENT ALERTS ====================

  getSentimentAlerts(sentiment: SentimentData): string[] {
    const alerts: string[] = [];

    if (sentiment.overallScore < 25) {
      alerts.push('🚨 Extreme Fear: Potential buying opportunity');
    } else if (sentiment.overallScore > 75) {
      alerts.push('⚠️ Extreme Greed: Consider taking profits');
    }

    if (sentiment.fearGreed < 30) {
      alerts.push('📉 Fear & Greed Index indicates oversold conditions');
    } else if (sentiment.fearGreed > 70) {
      alerts.push('📈 Fear & Greed Index indicates overbought conditions');
    }

    if (sentiment.confidence < 70) {
      alerts.push('❓ Low confidence in sentiment data');
    }

    return alerts;
  }

  // ==================== CLEAR CACHE ====================

  clearCache(): void {
    this.cache.clear();
    console.log('🧹 Sentiment cache cleared');
  }

  // ==================== HEALTH CHECK ====================

  async healthCheck(): Promise<boolean> {
    try {
      const response = await axios.get(this.fearGreedApi, {
        timeout: 5000
      });
      return response.status === 200;
    } catch (error) {
      console.error('❌ Sentiment service health check failed:', error);
      return false;
    }
  }
}

export default new SentimentService();