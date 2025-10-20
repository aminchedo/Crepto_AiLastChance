import axios from 'axios';

interface SentimentData {
  fearGreed: number;
  redditSentiment: number;
  coinGeckoSentiment: number;
  overallScore: number;
  trend: string;
}

class SentimentService {
  
  // Get Fear & Greed Index
  async getFearGreedIndex(): Promise<number> {
    try {
      const response = await axios.get(
        'https://api.alternative.me/fng/?limit=1',
        { timeout: 5000 }
      );

      const value = parseInt(response.data.data[0].value);
      return Math.max(0, Math.min(100, value)); // Clamp 0-100
    } catch (error) {
      console.warn('⚠️ Fear & Greed Index fetch failed, using 50:', error);
      return 50; // Default neutral
    }
  }

  // Analyze Reddit sentiment (simplified)
  async getRedditSentiment(): Promise<number> {
    try {
      // This is a simplified example
      // In production, use Reddit API or sentiment analysis service
      const randomFactor = Math.random();
      return Math.round(40 + randomFactor * 20); // 40-60 range
    } catch (error) {
      console.warn('⚠️ Reddit sentiment fetch failed:', error);
      return 50;
    }
  }

  // Get CoinGecko community sentiment
  async getCoinGeckoSentiment(): Promise<number> {
    try {
      // Simplified - in production use CoinGecko API
      const randomFactor = Math.random();
      return Math.round(40 + randomFactor * 20); // 40-60 range
    } catch (error) {
      console.warn('⚠️ CoinGecko sentiment fetch failed:', error);
      return 50;
    }
  }

  // Get combined sentiment score
  async getAggregatedSentiment(): Promise<SentimentData> {
    try {
      const [fearGreed, reddit, coinGecko] = await Promise.all([
        this.getFearGreedIndex(),
        this.getRedditSentiment(),
        this.getCoinGeckoSentiment()
      ]);

      // Weighted average: Fear & Greed 40%, Reddit 30%, CoinGecko 30%
      const overallScore = (fearGreed * 0.4) + (reddit * 0.3) + (coinGecko * 0.3);

      let trend = 'neutral';
      if (overallScore < 35) trend = 'extreme fear';
      else if (overallScore < 50) trend = 'fear';
      else if (overallScore < 65) trend = 'neutral';
      else if (overallScore < 80) trend = 'greed';
      else trend = 'extreme greed';

      return {
        fearGreed,
        redditSentiment: reddit,
        coinGeckoSentiment: coinGecko,
        overallScore: Math.round(overallScore),
        trend
      };
    } catch (error) {
      console.error('❌ Error getting aggregated sentiment:', error);
      return {
        fearGreed: 50,
        redditSentiment: 50,
        coinGeckoSentiment: 50,
        overallScore: 50,
        trend: 'neutral'
      };
    }
  }
}

export default new SentimentService();