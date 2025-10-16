import { WhaleTransaction } from '../types/index';

class WhaleTrackingService {
  private transactions: WhaleTransaction[] = [];
  private minAmount = 1000000; // $1M minimum

  async getTransactions(limit: number = 20): Promise<WhaleTransaction[]> {
    try {
      // Simplified mock - in production use actual blockchain APIs
      const mockTransactions: WhaleTransaction[] = [];

      for (let i = 0; i < limit; i++) {
        mockTransactions.push({
          id: `tx_${i}_${Date.now()}`,
          blockchain: (['ethereum', 'bitcoin', 'bsc', 'tron'] as const)[
            Math.floor(Math.random() * 4)
          ],
          amount: this.minAmount + Math.random() * 10000000,
          from: `0x${Math.random().toString(16).slice(2, 42)}`,
          to: `0x${Math.random().toString(16).slice(2, 42)}`,
          type: Math.random() > 0.5 ? 'buy' : 'sell',
          timestamp: Date.now() - Math.random() * 3600000,
          txHash: `0x${Math.random().toString(16).slice(2)}`
        });
      }

      return mockTransactions;
    } catch (error) {
      console.error('❌ Error fetching whale transactions:', error);
      return [];
    }
  }

  async filterLargeTransfers(minAmount: number = 1000000): Promise<WhaleTransaction[]> {
    const transactions = await this.getTransactions(100);
    return transactions.filter(tx => tx.amount >= minAmount);
  }
}

export default new WhaleTrackingService();
