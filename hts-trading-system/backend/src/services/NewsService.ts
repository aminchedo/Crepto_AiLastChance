import axios, { AxiosResponse } from 'axios';
import { NewsArticle } from '../types/index.js';
import { TradingSystemError } from '../types/index.js';

class NewsService {
  private newsApiKey: string;
  private coinGeckoApi: string;
  private cache: Map<string, { data: NewsArticle[]; timestamp: number }> = new Map();
  private cacheTtl: number;

  // Sentiment analysis keywords
  private positiveKeywords = [
    'surge', 'gains', 'bullish', 'rally', 'increase', 'boost', 'pump', 'moon',
    'soar', 'jump', 'breakthrough', 'milestone', 'adoption', 'partnership',
    'upgrade', 'launch', 'success', 'profit', 'growth', 'positive', 'optimistic',
    'breakout', 'resistance', 'support', 'buy', 'long', 'hodl', 'diamond hands'
  ];

  private negativeKeywords = [
    'crash', 'drop', 'bearish', 'decline', 'loss', 'dump', 'risk', 'fear',
    'plunge', 'collapse', 'sell', 'short', 'bear', 'panic', 'fud', 'scam',
    'hack', 'exploit', 'regulation', 'ban', 'warning', 'bubble', 'correction',
    'volatility', 'uncertainty', 'concern', 'doubt', 'skeptical', 'negative'
  ];

  private neutralKeywords = [
    'analysis', 'report', 'update', 'news', 'announcement', 'development',
    'technology', 'blockchain', 'cryptocurrency', 'digital', 'asset', 'token',
    'exchange', 'market', 'trading', 'investment', 'finance', 'economy'
  ];

  constructor() {
    this.newsApiKey = process.env.NEWS_API_KEY || 'demo';
    this.coinGeckoApi = process.env.COINGECKO_API || 'https://api.coingecko.com/api/v3';
    this.cacheTtl = parseInt(process.env.CACHE_TTL || '300') * 1000; // Convert to milliseconds
  }

  // ==================== CACHE MANAGEMENT ====================

  private getCached(key: string): NewsArticle[] | null {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTtl) {
      return cached.data;
    }
    return null;
  }

  private setCache(key: string, data: NewsArticle[]): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }

  // ==================== NEWS API INTEGRATION ====================

  async getLatestNews(limit: number = 20): Promise<NewsArticle[]> {
    const cacheKey = `news_${limit}`;
    const cached = this.getCached(cacheKey);
    if (cached) return cached;

    try {
      let articles: NewsArticle[] = [];

      // Try NewsAPI first
      if (this.newsApiKey !== 'demo') {
        try {
          articles = await this.fetchFromNewsAPI(limit);
        } catch (error) {
          console.warn('⚠️ NewsAPI failed, trying fallback:', error);
        }
      }

      // Fallback to CoinGecko if NewsAPI fails or is not available
      if (articles.length === 0) {
        articles = await this.fetchFromCoinGecko(limit);
      }

      // Analyze sentiment for each article
      articles = articles.map(article => ({
        ...article,
        sentiment: this.analyzeSentiment(article.title + ' ' + article.description),
        impact: this.assessImpact(article),
        tags: this.extractTags(article)
      }));

      this.setCache(cacheKey, articles);
      console.log(`✅ Fetched ${articles.length} news articles`);
      return articles;
    } catch (error) {
      console.error('❌ Error fetching news:', error);
      throw new TradingSystemError(
        'Failed to fetch news articles',
        'NEWS_FETCH_ERROR',
        500,
        error
      );
    }
  }

  // ==================== NEWSAPI FETCH ====================

  private async fetchFromNewsAPI(limit: number): Promise<NewsArticle[]> {
    const response: AxiosResponse = await axios.get(
      'https://newsapi.org/v2/everything',
      {
        params: {
          q: 'cryptocurrency OR bitcoin OR ethereum OR blockchain',
          sortBy: 'publishedAt',
          language: 'en',
          pageSize: Math.min(limit, 100),
          apiKey: this.newsApiKey
        },
        timeout: 10000,
        headers: {
          'User-Agent': 'HTS-Trading-System/1.0.0'
        }
      }
    );

    return response.data.articles.map((article: any, index: number) => ({
      id: `newsapi_${index}_${Date.now()}`,
      title: article.title || 'No title',
      description: article.description || '',
      url: article.url || '',
      source: article.source?.name || 'NewsAPI',
      image: article.urlToImage || '',
      published: article.publishedAt || new Date().toISOString(),
      sentiment: 'neutral' as const,
      impact: 'medium' as const,
      tags: [],
      author: article.author
    }));
  }

  // ==================== COINGECKO FETCH ====================

  private async fetchFromCoinGecko(limit: number): Promise<NewsArticle[]> {
    try {
      const response: AxiosResponse = await axios.get(
        `${this.coinGeckoApi}/coins/bitcoin/status_updates`,
        {
          params: {
            per_page: Math.min(limit, 100)
          },
          timeout: 10000,
          headers: {
            'User-Agent': 'HTS-Trading-System/1.0.0'
          }
        }
      );

      return response.data.status_updates.map((update: any, index: number) => ({
        id: `coingecko_${index}_${Date.now()}`,
        title: update.description?.substring(0, 100) || 'Status Update',
        description: update.description || '',
        url: update.user?.twitter || '',
        source: 'CoinGecko',
        image: '',
        published: update.created_at || new Date().toISOString(),
        sentiment: 'neutral' as const,
        impact: 'low' as const,
        tags: [],
        author: update.user?.username
      }));
    } catch (error) {
      console.warn('⚠️ CoinGecko news fetch failed:', error);
      return this.getMockNews(limit);
    }
  }

  // ==================== MOCK NEWS (FALLBACK) ====================

  private getMockNews(limit: number): NewsArticle[] {
    const mockArticles: NewsArticle[] = [
      {
        id: 'mock_1',
        title: 'Bitcoin Reaches New Milestone in Institutional Adoption',
        description: 'Major corporations continue to add Bitcoin to their balance sheets, signaling growing mainstream acceptance.',
        url: 'https://example.com/bitcoin-adoption',
        source: 'CryptoNews',
        image: '',
        published: new Date(Date.now() - 3600000).toISOString(),
        sentiment: 'positive',
        impact: 'high',
        tags: ['bitcoin', 'institutional', 'adoption'],
        author: 'Crypto Analyst'
      },
      {
        id: 'mock_2',
        title: 'Ethereum Network Upgrade Shows Promising Results',
        description: 'The latest Ethereum upgrade has improved transaction speeds and reduced gas fees significantly.',
        url: 'https://example.com/ethereum-upgrade',
        source: 'Blockchain Weekly',
        image: '',
        published: new Date(Date.now() - 7200000).toISOString(),
        sentiment: 'positive',
        impact: 'medium',
        tags: ['ethereum', 'upgrade', 'scalability'],
        author: 'Tech Reporter'
      },
      {
        id: 'mock_3',
        title: 'Regulatory Uncertainty Continues to Impact Crypto Markets',
        description: 'Investors remain cautious as regulatory frameworks continue to evolve in major markets.',
        url: 'https://example.com/regulation',
        source: 'Finance Today',
        image: '',
        published: new Date(Date.now() - 10800000).toISOString(),
        sentiment: 'negative',
        impact: 'medium',
        tags: ['regulation', 'uncertainty', 'markets'],
        author: 'Financial Analyst'
      }
    ];

    return mockArticles.slice(0, limit);
  }

  // ==================== SENTIMENT ANALYSIS ====================

  private analyzeSentiment(text: string): 'positive' | 'negative' | 'neutral' {
    const lowerText = text.toLowerCase();
    
    const positiveCount = this.positiveKeywords.filter(keyword =>
      lowerText.includes(keyword)
    ).length;

    const negativeCount = this.negativeKeywords.filter(keyword =>
      lowerText.includes(keyword)
    ).length;

    const neutralCount = this.neutralKeywords.filter(keyword =>
      lowerText.includes(keyword)
    ).length;

    const totalKeywords = positiveCount + negativeCount + neutralCount;

    if (totalKeywords === 0) return 'neutral';

    const positiveRatio = positiveCount / totalKeywords;
    const negativeRatio = negativeCount / totalKeywords;

    if (positiveRatio > 0.6) return 'positive';
    if (negativeRatio > 0.6) return 'negative';
    return 'neutral';
  }

  // ==================== IMPACT ASSESSMENT ====================

  private assessImpact(article: NewsArticle): 'high' | 'medium' | 'low' {
    const highImpactKeywords = [
      'bitcoin', 'ethereum', 'regulation', 'adoption', 'partnership',
      'upgrade', 'launch', 'crash', 'rally', 'milestone', 'breakthrough'
    ];

    const mediumImpactKeywords = [
      'market', 'trading', 'price', 'volume', 'analysis', 'report',
      'update', 'announcement', 'development', 'technology'
    ];

    const text = (article.title + ' ' + article.description).toLowerCase();
    
    const highImpactCount = highImpactKeywords.filter(keyword =>
      text.includes(keyword)
    ).length;

    const mediumImpactCount = mediumImpactKeywords.filter(keyword =>
      text.includes(keyword)
    ).length;

    if (highImpactCount >= 2) return 'high';
    if (highImpactCount >= 1 || mediumImpactCount >= 3) return 'medium';
    return 'low';
  }

  // ==================== TAG EXTRACTION ====================

  private extractTags(article: NewsArticle): string[] {
    const text = (article.title + ' ' + article.description).toLowerCase();
    const allKeywords = [
      ...this.positiveKeywords,
      ...this.negativeKeywords,
      ...this.neutralKeywords,
      'bitcoin', 'ethereum', 'crypto', 'blockchain', 'defi', 'nft',
      'trading', 'investment', 'market', 'price', 'volume'
    ];

    return allKeywords.filter(keyword => text.includes(keyword)).slice(0, 5);
  }

  // ==================== FILTERED NEWS ====================

  async getNewsBySentiment(
    sentiment: 'positive' | 'negative' | 'neutral',
    limit: number = 10
  ): Promise<NewsArticle[]> {
    const allNews = await this.getLatestNews(limit * 2);
    return allNews
      .filter(article => article.sentiment === sentiment)
      .slice(0, limit);
  }

  async getNewsByImpact(
    impact: 'high' | 'medium' | 'low',
    limit: number = 10
  ): Promise<NewsArticle[]> {
    const allNews = await this.getLatestNews(limit * 2);
    return allNews
      .filter(article => article.impact === impact)
      .slice(0, limit);
  }

  async getNewsBySource(
    source: string,
    limit: number = 10
  ): Promise<NewsArticle[]> {
    const allNews = await this.getLatestNews(limit * 2);
    return allNews
      .filter(article => article.source.toLowerCase().includes(source.toLowerCase()))
      .slice(0, limit);
  }

  // ==================== NEWS STATISTICS ====================

  getNewsStatistics(news: NewsArticle[]): {
    total: number;
    positive: number;
    negative: number;
    neutral: number;
    highImpact: number;
    mediumImpact: number;
    lowImpact: number;
    sources: { [key: string]: number };
  } {
    const stats = {
      total: news.length,
      positive: news.filter(n => n.sentiment === 'positive').length,
      negative: news.filter(n => n.sentiment === 'negative').length,
      neutral: news.filter(n => n.sentiment === 'neutral').length,
      highImpact: news.filter(n => n.impact === 'high').length,
      mediumImpact: news.filter(n => n.impact === 'medium').length,
      lowImpact: news.filter(n => n.impact === 'low').length,
      sources: {} as { [key: string]: number }
    };

    news.forEach(article => {
      stats.sources[article.source] = (stats.sources[article.source] || 0) + 1;
    });

    return stats;
  }

  // ==================== CLEAR CACHE ====================

  clearCache(): void {
    this.cache.clear();
    console.log('🧹 News cache cleared');
  }

  // ==================== HEALTH CHECK ====================

  async healthCheck(): Promise<boolean> {
    try {
      // Test with a simple request
      const response = await axios.get(this.coinGeckoApi + '/ping', {
        timeout: 5000
      });
      return response.status === 200;
    } catch (error) {
      console.error('❌ News service health check failed:', error);
      return false;
    }
  }
}

export default new NewsService();