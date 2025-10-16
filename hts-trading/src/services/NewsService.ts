import axios from 'axios';

interface NewsArticle {
  id: string;
  title: string;
  description: string;
  url: string;
  source: string;
  image: string;
  published: string;
  sentiment: 'positive' | 'negative' | 'neutral';
}

class NewsService {
  private newsCache: NewsArticle[] = [];
  private lastFetch = 0;
  private cacheDuration = 300000; // 5 minutes

  async getLatestNews(limit: number = 20): Promise<NewsArticle[]> {
    // Check cache
    if (this.newsCache.length > 0 && Date.now() - this.lastFetch < this.cacheDuration) {
      return this.newsCache.slice(0, limit);
    }

    try {
      // For demo purposes, we'll create mock news data
      // In production, use NewsAPI or similar service
      const mockNews: NewsArticle[] = [
        {
          id: '1',
          title: 'Bitcoin Reaches New All-Time High Amid Institutional Adoption',
          description: 'Major corporations continue to add Bitcoin to their balance sheets, driving price momentum.',
          url: 'https://example.com/bitcoin-news-1',
          source: 'CryptoNews',
          image: 'https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=400',
          published: new Date().toISOString(),
          sentiment: 'positive'
        },
        {
          id: '2',
          title: 'Ethereum 2.0 Staking Rewards Hit Record Highs',
          description: 'Network upgrade continues to show strong performance metrics and user adoption.',
          url: 'https://example.com/ethereum-news-1',
          source: 'EthereumDaily',
          image: 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=400',
          published: new Date(Date.now() - 3600000).toISOString(),
          sentiment: 'positive'
        },
        {
          id: '3',
          title: 'Regulatory Concerns Weigh on Crypto Markets',
          description: 'Government officials express concerns about cryptocurrency regulation and oversight.',
          url: 'https://example.com/regulation-news-1',
          source: 'CryptoRegulation',
          image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400',
          published: new Date(Date.now() - 7200000).toISOString(),
          sentiment: 'negative'
        },
        {
          id: '4',
          title: 'DeFi Protocol Launches Revolutionary Yield Farming',
          description: 'New decentralized finance platform offers innovative staking mechanisms.',
          url: 'https://example.com/defi-news-1',
          source: 'DeFiToday',
          image: 'https://images.unsplash.com/photo-1639322537504-6427a16b0a28?w=400',
          published: new Date(Date.now() - 10800000).toISOString(),
          sentiment: 'positive'
        },
        {
          id: '5',
          title: 'Market Analysis: Technical Indicators Show Mixed Signals',
          description: 'Trading experts provide insights on current market conditions and future outlook.',
          url: 'https://example.com/analysis-news-1',
          source: 'TradingInsights',
          image: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400',
          published: new Date(Date.now() - 14400000).toISOString(),
          sentiment: 'neutral'
        }
      ];

      this.newsCache = mockNews;
      this.lastFetch = Date.now();

      return mockNews.slice(0, limit);
    } catch (error) {
      console.warn('⚠️ Error fetching news:', error);
      return this.newsCache.slice(0, limit);
    }
  }

  // Simple sentiment analysis
  private analyzeSentiment(text: string): 'positive' | 'negative' | 'neutral' {
    const positiveWords = ['surge', 'gains', 'bullish', 'rally', 'increase', 'boost', 'pump', 'moon', 'adoption', 'record', 'high'];
    const negativeWords = ['crash', 'drop', 'bearish', 'decline', 'loss', 'dump', 'risk', 'fear', 'concern', 'regulation', 'weigh'];

    const lowerText = text.toLowerCase();
    
    const positiveCount = positiveWords.filter(word => lowerText.includes(word)).length;
    const negativeCount = negativeWords.filter(word => lowerText.includes(word)).length;

    if (positiveCount > negativeCount) return 'positive';
    if (negativeCount > positiveCount) return 'negative';
    return 'neutral';
  }
}

export default new NewsService();