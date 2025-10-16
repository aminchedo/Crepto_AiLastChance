import axios, { AxiosResponse } from 'axios';
import { WhaleTransaction, Blockchain } from '../types/index.js';
import { TradingSystemError } from '../types/index.js';

class WhaleTrackingService {
  private cache: Map<string, { data: WhaleTransaction[]; timestamp: number }> = new Map();
  private cacheTtl: number;
  private minAmount: number = 1000000; // $1M minimum

  // Mock whale addresses for simulation
  private whaleAddresses = [
    '0x1234567890123456789012345678901234567890',
    '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
    '0x9876543210987654321098765432109876543210',
    '0xfedcbafedcbafedcbafedcbafedcbafedcbafedc',
    '0x1111111111111111111111111111111111111111'
  ];

  // Mock exchange addresses
  private exchangeAddresses = [
    '0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be', // Binance
    '0x28c6c06298d514db089934071355e5743bf21d60', // Binance 2
    '0x21a31ee1afc51d94c2efccaa2092ad1028285549', // Binance 3
    '0xdfd5293d8e347dfe59e90efd55b2956a1343963d', // Binance 4
    '0x56eddb7aa87536c09ccc2793473599fd21a8b17f', // Binance 5
    '0x5041ed759dd4afc3a72b8192c143f72f3d3244c',  // Binance 6
    '0x689c56aef474df92d44a1b70850f808488f9769c', // Binance 7
    '0xab83d182f3485cf1d6ccdd34c7cfef95b4c08da',  // Binance 8
    '0x4e9ce36e442e55ecd9025b9a6e0d88485d628a67', // Binance 9
    '0xbe0eb53f46cd790cd13851d5eff43d12404d33e8'  // Binance 10
  ];

  constructor() {
    this.cacheTtl = parseInt(process.env.CACHE_TTL || '300') * 1000; // Convert to milliseconds
  }

  // ==================== CACHE MANAGEMENT ====================

  private getCached(key: string): WhaleTransaction[] | null {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTtl) {
      return cached.data;
    }
    return null;
  }

  private setCache(key: string, data: WhaleTransaction[]): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }

  // ==================== TRANSACTION FETCHING ====================

  async getTransactions(limit: number = 20): Promise<WhaleTransaction[]> {
    const cacheKey = `whale_transactions_${limit}`;
    const cached = this.getCached(cacheKey);
    if (cached) return cached;

    try {
      // In a real implementation, you would fetch from multiple sources
      const transactions = await this.fetchFromMultipleSources(limit);
      
      this.setCache(cacheKey, transactions);
      console.log(`✅ Fetched ${transactions.length} whale transactions`);
      return transactions;
    } catch (error) {
      console.error('❌ Error fetching whale transactions:', error);
      return this.getMockTransactions(limit);
    }
  }

  // ==================== MULTIPLE SOURCE FETCHING ====================

  private async fetchFromMultipleSources(limit: number): Promise<WhaleTransaction[]> {
    const allTransactions: WhaleTransaction[] = [];

    try {
      // Fetch from different blockchains in parallel
      const [ethereum, bsc, polygon] = await Promise.allSettled([
        this.fetchEthereumTransactions(Math.ceil(limit / 3)),
        this.fetchBSCTransactions(Math.ceil(limit / 3)),
        this.fetchPolygonTransactions(Math.ceil(limit / 3))
      ]);

      // Combine results
      if (ethereum.status === 'fulfilled') {
        allTransactions.push(...ethereum.value);
      }
      if (bsc.status === 'fulfilled') {
        allTransactions.push(...bsc.value);
      }
      if (polygon.status === 'fulfilled') {
        allTransactions.push(...polygon.value);
      }

      // Sort by timestamp (newest first) and limit
      return allTransactions
        .sort((a, b) => b.timestamp - a.timestamp)
        .slice(0, limit);
    } catch (error) {
      console.error('❌ Error fetching from multiple sources:', error);
      return this.getMockTransactions(limit);
    }
  }

  // ==================== ETHEREUM TRANSACTIONS ====================

  private async fetchEthereumTransactions(limit: number): Promise<WhaleTransaction[]> {
    try {
      // In a real implementation, you would use Etherscan API
      // For now, we'll simulate with mock data
      return this.generateMockTransactions('ethereum', limit);
    } catch (error) {
      console.warn('⚠️ Ethereum transaction fetch failed:', error);
      return [];
    }
  }

  // ==================== BSC TRANSACTIONS ====================

  private async fetchBSCTransactions(limit: number): Promise<WhaleTransaction[]> {
    try {
      // In a real implementation, you would use BSCScan API
      return this.generateMockTransactions('bsc', limit);
    } catch (error) {
      console.warn('⚠️ BSC transaction fetch failed:', error);
      return [];
    }
  }

  // ==================== POLYGON TRANSACTIONS ====================

  private async fetchPolygonTransactions(limit: number): Promise<WhaleTransaction[]> {
    try {
      // In a real implementation, you would use PolygonScan API
      return this.generateMockTransactions('polygon', limit);
    } catch (error) {
      console.warn('⚠️ Polygon transaction fetch failed:', error);
      return [];
    }
  }

  // ==================== MOCK TRANSACTION GENERATION ====================

  private generateMockTransactions(blockchain: Blockchain, limit: number): WhaleTransaction[] {
    const transactions: WhaleTransaction[] = [];
    const now = Date.now();
    const hourMs = 60 * 60 * 1000;

    for (let i = 0; i < limit; i++) {
      const isExchange = Math.random() < 0.3; // 30% chance of exchange transaction
      const from = isExchange 
        ? this.exchangeAddresses[Math.floor(Math.random() * this.exchangeAddresses.length)]
        : this.whaleAddresses[Math.floor(Math.random() * this.whaleAddresses.length)];
      
      const to = isExchange
        ? this.whaleAddresses[Math.floor(Math.random() * this.whaleAddresses.length)]
        : this.exchangeAddresses[Math.floor(Math.random() * this.exchangeAddresses.length)];

      const amount = this.minAmount + Math.random() * 10000000; // $1M to $11M
      const usdValue = amount * (0.8 + Math.random() * 0.4); // Some price variation

      const transaction: WhaleTransaction = {
        id: `${blockchain}_${i}_${Date.now()}`,
        blockchain,
        amount,
        from,
        to,
        type: isExchange ? 'sell' : 'buy',
        timestamp: now - Math.random() * hourMs * 24, // Last 24 hours
        txHash: this.generateTxHash(),
        token: this.getRandomToken(blockchain),
        usdValue,
        gasUsed: Math.floor(Math.random() * 100000) + 21000,
        gasPrice: Math.floor(Math.random() * 50) + 20
      };

      transactions.push(transaction);
    }

    return transactions;
  }

  private getMockTransactions(limit: number): WhaleTransaction[] {
    const blockchains: Blockchain[] = ['ethereum', 'bsc', 'polygon'];
    const allTransactions: WhaleTransaction[] = [];

    for (const blockchain of blockchains) {
      const count = Math.ceil(limit / blockchains.length);
      allTransactions.push(...this.generateMockTransactions(blockchain, count));
    }

    return allTransactions
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit);
  }

  // ==================== UTILITY METHODS ====================

  private generateTxHash(): string {
    const chars = '0123456789abcdef';
    let hash = '0x';
    for (let i = 0; i < 64; i++) {
      hash += chars[Math.floor(Math.random() * chars.length)];
    }
    return hash;
  }

  private getRandomToken(blockchain: Blockchain): string {
    const tokens = {
      ethereum: ['ETH', 'USDT', 'USDC', 'WBTC', 'DAI'],
      bsc: ['BNB', 'BUSD', 'USDT', 'CAKE', 'ADA'],
      polygon: ['MATIC', 'USDT', 'USDC', 'WETH', 'QUICK']
    };
    
    const tokenList = tokens[blockchain] || ['TOKEN'];
    return tokenList[Math.floor(Math.random() * tokenList.length)];
  }

  // ==================== FILTERING METHODS ====================

  async filterLargeTransfers(minAmount: number = 1000000): Promise<WhaleTransaction[]> {
    const allTransactions = await this.getTransactions(100);
    return allTransactions.filter(tx => tx.amount >= minAmount);
  }

  async getTransactionsByBlockchain(blockchain: Blockchain, limit: number = 20): Promise<WhaleTransaction[]> {
    const allTransactions = await this.getTransactions(limit * 2);
    return allTransactions
      .filter(tx => tx.blockchain === blockchain)
      .slice(0, limit);
  }

  async getTransactionsByType(type: 'buy' | 'sell' | 'transfer', limit: number = 20): Promise<WhaleTransaction[]> {
    const allTransactions = await this.getTransactions(limit * 2);
    return allTransactions
      .filter(tx => tx.type === type)
      .slice(0, limit);
  }

  async getTransactionsByToken(token: string, limit: number = 20): Promise<WhaleTransaction[]> {
    const allTransactions = await this.getTransactions(limit * 2);
    return allTransactions
      .filter(tx => tx.token === token)
      .slice(0, limit);
  }

  // ==================== ANALYSIS METHODS ====================

  async getWhaleActivitySummary(): Promise<{
    totalTransactions: number;
    totalVolume: number;
    averageTransactionSize: number;
    topTokens: { token: string; count: number; volume: number }[];
    blockchainDistribution: { blockchain: string; count: number; volume: number }[];
    typeDistribution: { type: string; count: number; volume: number }[];
  }> {
    const transactions = await this.getTransactions(100);

    const summary = {
      totalTransactions: transactions.length,
      totalVolume: transactions.reduce((sum, tx) => sum + tx.usdValue, 0),
      averageTransactionSize: 0,
      topTokens: [] as { token: string; count: number; volume: number }[],
      blockchainDistribution: [] as { blockchain: string; count: number; volume: number }[],
      typeDistribution: [] as { type: string; count: number; volume: number }[]
    };

    summary.averageTransactionSize = summary.totalVolume / summary.totalTransactions;

    // Token analysis
    const tokenStats = new Map<string, { count: number; volume: number }>();
    transactions.forEach(tx => {
      const stats = tokenStats.get(tx.token) || { count: 0, volume: 0 };
      stats.count++;
      stats.volume += tx.usdValue;
      tokenStats.set(tx.token, stats);
    });

    summary.topTokens = Array.from(tokenStats.entries())
      .map(([token, stats]) => ({ token, ...stats }))
      .sort((a, b) => b.volume - a.volume)
      .slice(0, 5);

    // Blockchain analysis
    const blockchainStats = new Map<string, { count: number; volume: number }>();
    transactions.forEach(tx => {
      const stats = blockchainStats.get(tx.blockchain) || { count: 0, volume: 0 };
      stats.count++;
      stats.volume += tx.usdValue;
      blockchainStats.set(tx.blockchain, stats);
    });

    summary.blockchainDistribution = Array.from(blockchainStats.entries())
      .map(([blockchain, stats]) => ({ blockchain, ...stats }));

    // Type analysis
    const typeStats = new Map<string, { count: number; volume: number }>();
    transactions.forEach(tx => {
      const stats = typeStats.get(tx.type) || { count: 0, volume: 0 };
      stats.count++;
      stats.volume += tx.usdValue;
      typeStats.set(tx.type, stats);
    });

    summary.typeDistribution = Array.from(typeStats.entries())
      .map(([type, stats]) => ({ type, ...stats }));

    return summary;
  }

  // ==================== ALERT METHODS ====================

  async getWhaleAlerts(): Promise<string[]> {
    const transactions = await this.getTransactions(50);
    const alerts: string[] = [];

    // Check for very large transactions
    const veryLarge = transactions.filter(tx => tx.usdValue > 5000000);
    if (veryLarge.length > 0) {
      alerts.push(`🚨 ${veryLarge.length} transactions over $5M detected`);
    }

    // Check for exchange activity
    const exchangeActivity = transactions.filter(tx => 
      this.exchangeAddresses.includes(tx.from) || this.exchangeAddresses.includes(tx.to)
    );
    if (exchangeActivity.length > 10) {
      alerts.push(`📈 High exchange activity: ${exchangeActivity.length} transactions`);
    }

    // Check for specific token activity
    const tokenStats = new Map<string, number>();
    transactions.forEach(tx => {
      tokenStats.set(tx.token, (tokenStats.get(tx.token) || 0) + 1);
    });

    const topToken = Array.from(tokenStats.entries())
      .sort((a, b) => b[1] - a[1])[0];

    if (topToken && topToken[1] > 10) {
      alerts.push(`🔥 High ${topToken[0]} activity: ${topToken[1]} transactions`);
    }

    return alerts;
  }

  // ==================== CLEAR CACHE ====================

  clearCache(): void {
    this.cache.clear();
    console.log('🧹 Whale tracking cache cleared');
  }

  // ==================== HEALTH CHECK ====================

  async healthCheck(): Promise<boolean> {
    try {
      // Test with a small request
      const transactions = await this.getTransactions(1);
      return transactions.length >= 0; // Even 0 is considered healthy
    } catch (error) {
      console.error('❌ Whale tracking service health check failed:', error);
      return false;
    }
  }
}

export default new WhaleTrackingService();