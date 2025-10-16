import { RSIResult, MACDResult, TechnicalIndicators } from '../types/index';

class IndicatorService {

  // Calculate RSI
  calculateRSI(prices: number[], period: number = 14): RSIResult {
    if (prices.length < period + 1) {
      return { rsi: 50, trend: 'neutral' };
    }

    let gains = 0;
    let losses = 0;

    for (let i = prices.length - period; i < prices.length; i++) {
      const change = prices[i] - prices[i - 1];
      if (change > 0) gains += change;
      else losses += Math.abs(change);
    }

    const avgGain = gains / period;
    const avgLoss = losses / period;
    const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
    const rsi = 100 - (100 / (1 + rs));

    let trend: 'oversold' | 'neutral' | 'overbought';
    if (rsi < 30) trend = 'oversold';
    else if (rsi > 70) trend = 'overbought';
    else trend = 'neutral';

    return {
      rsi: Math.round(rsi * 100) / 100,
      trend
    };
  }

  // Calculate MACD
  calculateMACD(prices: number[]): MACDResult {
    if (prices.length < 26) {
      return {
        macd: 0,
        signal: 0,
        histogram: 0,
        trend: 'neutral'
      };
    }

    const ema12 = this.calculateEMA(prices, 12);
    const ema26 = this.calculateEMA(prices, 26);
    const macd = ema12 - ema26;

    // Calculate signal line
    const recentPrices = prices.slice(-35);
    const macdValues: number[] = [];

    for (let i = 0; i < recentPrices.length; i++) {
      const sliced = prices.slice(0, prices.length - recentPrices.length + i + 1);
      if (sliced.length >= 26) {
        const e12 = this.calculateEMA(sliced, 12);
        const e26 = this.calculateEMA(sliced, 26);
        macdValues.push(e12 - e26);
      }
    }

    const signal = macdValues.length > 0
      ? this.calculateEMA(macdValues, 9)
      : 0;

    const histogram = macd - signal;

    return {
      macd: Math.round(macd * 10000) / 10000,
      signal: Math.round(signal * 10000) / 10000,
      histogram: Math.round(histogram * 10000) / 10000,
      trend: histogram > 0 ? 'bullish' : 'bearish'
    };
  }

  // Calculate Exponential Moving Average
  private calculateEMA(prices: number[], period: number): number {
    if (prices.length < period) return prices[prices.length - 1];

    const multiplier = 2 / (period + 1);
    let ema = prices.slice(0, period).reduce((a, b) => a + b, 0) / period;

    for (let i = period; i < prices.length; i++) {
      ema = (prices[i] - ema) * multiplier + ema;
    }

    return ema;
  }

  // Calculate Simple Moving Average
  calculateSMA(prices: number[], period: number): number {
    if (prices.length < period) {
      return prices.reduce((a, b) => a + b, 0) / prices.length;
    }
    return prices.slice(-period).reduce((a, b) => a + b, 0) / period;
  }

  // Calculate Bollinger Bands
  calculateBollingerBands(
    prices: number[],
    period: number = 20,
    stdDeviation: number = 2
  ) {
    const middle = this.calculateSMA(prices, period);
    const recentPrices = prices.slice(-period);

    const variance =
      recentPrices.reduce((sum, price) => sum + Math.pow(price - middle, 2), 0) /
      period;
    const std = Math.sqrt(variance);

    return {
      upper: middle + std * stdDeviation,
      middle,
      lower: middle - std * stdDeviation
    };
  }

  // Calculate ATR
  calculateATR(
    highs: number[],
    lows: number[],
    closes: number[],
    period: number = 14
  ): number {
    const trueRanges: number[] = [];

    for (let i = 1; i < closes.length; i++) {
      const tr = Math.max(
        highs[i] - lows[i],
        Math.abs(highs[i] - closes[i - 1]),
        Math.abs(lows[i] - closes[i - 1])
      );
      trueRanges.push(tr);
    }

    if (trueRanges.length < period) {
      return trueRanges.reduce((a, b) => a + b, 0) / trueRanges.length;
    }

    const atr = trueRanges.slice(-period)
      .reduce((a, b) => a + b, 0) / period;

    return Math.round(atr * 100) / 100;
  }

  // Get all technical indicators
  getAllIndicators(
    candles: any[],
    prices: number[]
  ): TechnicalIndicators {
    const highs = candles.map(c => c.high);
    const lows = candles.map(c => c.low);
    const closes = candles.map(c => c.close);

    return {
      rsi: this.calculateRSI(prices),
      macd: this.calculateMACD(prices),
      atr: this.calculateATR(highs, lows, closes),
      sma20: this.calculateSMA(prices, 20),
      sma50: this.calculateSMA(prices, 50),
      bollingerBands: this.calculateBollingerBands(prices, 20, 2)
    };
  }
}

export default new IndicatorService();
