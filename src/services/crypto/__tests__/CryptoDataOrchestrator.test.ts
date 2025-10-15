import { describe, it, expect, beforeEach, vi } from 'vitest';
import CryptoDataOrchestrator from '../CryptoDataOrchestrator';
import { FEATURE_FLAGS } from '../../../config/cryptoApiConfig';

// Mock the feature flags
vi.mock('../../../config/cryptoApiConfig', () => ({
    FEATURE_FLAGS: {
        USE_REAL_APIS: false // Start with mock data for testing
    }
}));

describe('CryptoDataOrchestrator', () => {
    beforeEach(() => {
        // Reset metrics before each test
        CryptoDataOrchestrator.resetMetrics();
    });

    describe('getDashboardData', () => {
        it('should return mock data when real APIs are disabled', async () => {
            const data = await CryptoDataOrchestrator.getDashboardData();

            expect(data).toHaveProperty('prices');
            expect(data).toHaveProperty('news');
            expect(data).toHaveProperty('whaleAlerts');
            expect(data).toHaveProperty('sentiment');
            expect(data).toHaveProperty('marketOverview');
            expect(data).toHaveProperty('systemHealth');

            expect(Array.isArray(data.prices)).toBe(true);
            expect(Array.isArray(data.news)).toBe(true);
            expect(Array.isArray(data.whaleAlerts)).toBe(true);
            expect(data.sentiment).toHaveProperty('fear_greed_index');
            expect(data.marketOverview).toHaveProperty('total_market_cap');
        });

        it('should return data with correct structure', async () => {
            const data = await CryptoDataOrchestrator.getDashboardData();

            // Check prices structure
            if (data.prices.length > 0) {
                const price = data.prices[0];
                expect(price).toHaveProperty('id');
                expect(price).toHaveProperty('symbol');
                expect(price).toHaveProperty('name');
                expect(price).toHaveProperty('current_price');
                expect(price).toHaveProperty('market_cap');
            }

            // Check news structure
            if (data.news.length > 0) {
                const news = data.news[0];
                expect(news).toHaveProperty('id');
                expect(news).toHaveProperty('title');
                expect(news).toHaveProperty('description');
                expect(news).toHaveProperty('url');
            }
        });
    });

    describe('getMarketData', () => {
        it('should return market data for specific symbols', async () => {
            const symbols = ['BTC', 'ETH'];
            const data = await CryptoDataOrchestrator.getMarketData(symbols);

            expect(data).toHaveProperty('prices');
            expect(data).toHaveProperty('sentiment');
            expect(data).toHaveProperty('news');

            expect(typeof data.prices).toBe('object');
            expect(Array.isArray(data.news)).toBe(true);
        });

        it('should handle empty symbols array', async () => {
            const data = await CryptoDataOrchestrator.getMarketData([]);

            expect(data.prices).toEqual({});
            expect(data.sentiment).toEqual({});
            expect(Array.isArray(data.news)).toBe(true);
        });
    });

    describe('getNewsAndSentiment', () => {
        it('should return news and sentiment data', async () => {
            const data = await CryptoDataOrchestrator.getNewsAndSentiment();

            expect(data).toHaveProperty('news');
            expect(data).toHaveProperty('sentiment');
            expect(data).toHaveProperty('socialSentiment');

            expect(Array.isArray(data.news)).toBe(true);
            expect(data.sentiment).toHaveProperty('fear_greed_index');
        });
    });

    describe('getWhaleData', () => {
        it('should return whale tracking data', async () => {
            const data = await CryptoDataOrchestrator.getWhaleData();

            expect(data).toHaveProperty('recentTransactions');
            expect(data).toHaveProperty('summary');
            expect(data).toHaveProperty('statistics');

            expect(Array.isArray(data.recentTransactions)).toBe(true);
            expect(typeof data.summary).toBe('object');
            expect(typeof data.statistics).toBe('object');
        });
    });

    describe('getBlockchainData', () => {
        it('should return blockchain data for an address', async () => {
            const address = '0x1234567890123456789012345678901234567890';
            const data = await CryptoDataOrchestrator.getBlockchainData(address, 'ethereum');

            expect(data).toHaveProperty('balance');
            expect(data).toHaveProperty('transactions');
            expect(data).toHaveProperty('tokenBalances');

            expect(Array.isArray(data.transactions)).toBe(true);
            expect(Array.isArray(data.tokenBalances)).toBe(true);
        });
    });

    describe('getSystemHealth', () => {
        it('should return system health information', () => {
            const health = CryptoDataOrchestrator.getSystemHealth();

            expect(health).toHaveProperty('overall');
            expect(health).toHaveProperty('services');
            expect(health).toHaveProperty('metrics');

            expect(health.overall).toHaveProperty('status');
            expect(health.overall).toHaveProperty('healthyServices');
            expect(health.overall).toHaveProperty('totalServices');
        });
    });

    describe('getServiceHealth', () => {
        it('should return health for specific service', () => {
            const health = CryptoDataOrchestrator.getServiceHealth('MarketDataService');

            expect(health).toHaveProperty('service');
            expect(health).toHaveProperty('status');
            expect(health).toHaveProperty('lastCheck');
            expect(health).toHaveProperty('responseTime');
        });

        it('should return null for non-existent service', () => {
            const health = CryptoDataOrchestrator.getServiceHealth('NonExistentService');
            expect(health).toBeNull();
        });
    });

    describe('resetMetrics', () => {
        it('should reset all metrics', () => {
            // This should not throw an error
            expect(() => CryptoDataOrchestrator.resetMetrics()).not.toThrow();
        });
    });
});
