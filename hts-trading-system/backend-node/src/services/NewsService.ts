import axios from 'axios';
import { NewsArticle } from '../types/index';

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
      // Note: For demo, using mock data. In production, use NewsAPI with valid API key
      const mockNews: NewsArticle[] = this.generateMockNews();
      
      this.newsCache = mockNews;
      this.lastFetch = Date.now();

      return mockNews.slice(0, limit);
    } catch (error) {
      console.warn('⚠️ Error fetching news:', error);
      return this.newsCache.slice(0, limit);
    }
  }

  private generateMockNews(): NewsArticle[] {
    const titles = [
      'Bitcoin Surges Past $45,000 as Institutional Interest Grows',
      'Ethereum 2.0 Upgrade Shows Promising Results',
      'Major Bank Announces Crypto Trading Services',
      'Regulatory Clarity Boosts Market Sentiment',
      'DeFi Protocols See Record Trading Volume',
      'NFT Market Shows Signs of Recovery',
      'Cryptocurrency Adoption Increases in Emerging Markets',
      'Blockchain Technology Revolutionizes Supply Chain',
      'Central Banks Explore Digital Currency Options',
      'Crypto Hedge Funds Report Strong Q1 Performance'
    ];

    return titles.map((title, index) => ({
      id: `news_${index}_${Date.now()}`,
      title,
      description: `${title}. Market analysts suggest this could be a significant development for the cryptocurrency ecosystem.`,
      url: `https://example.com/news/${index}`,
      source: ['CoinDesk', 'CoinTelegraph', 'Bloomberg', 'Reuters'][index % 4],
      image: `https://via.placeholder.com/400x200?text=Crypto+News+${index + 1}`,
      published: new Date(Date.now() - Math.random() * 86400000).toISOString(),
      sentiment: this.analyzeSentiment(title)
    }));
  }

  private analyzeSentiment(text: string): 'positive' | 'negative' | 'neutral' {
    const positiveWords = [
      'surge', 'gains', 'bullish', 'rally', 'increase',
      'boost', 'pump', 'moon', 'soar', 'jump', 'grow', 'promising'
    ];
    const negativeWords = [
      'crash', 'drop', 'bearish', 'decline', 'loss',
      'dump', 'risk', 'fear', 'plunge', 'collapse', 'fall'
    ];

    const lowerText = text.toLowerCase();

    const positiveCount = positiveWords.filter(word =>
      lowerText.includes(word)
    ).length;

    const negativeCount = negativeWords.filter(word =>
      lowerText.includes(word)
    ).length;

    if (positiveCount > negativeCount) return 'positive';
    if (negativeCount > positiveCount) return 'negative';
    return 'neutral';
  }
}

export default new NewsService();
