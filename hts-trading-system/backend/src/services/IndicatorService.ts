import { 
  RSIResult, 
  MACDResult, 
  BollingerBands, 
  TechnicalIndicators,
  Candle 
} from '../types/index.js';

class IndicatorService {

  // ==================== RSI CALCULATION ====================

  calculateRSI(prices: number[], period: number = 14): RSIResult {
    if (prices.length < period + 1) {
      return { rsi: 50, trend: 'neutral' };
    }

    let gains = 0;
    let losses = 0;

    // Calculate initial average gains and losses
    for (let i = prices.length - period; i < prices.length; i++) {
      const change = prices[i] - prices[i - 1];
      if (change > 0) gains += change;
      else losses += Math.abs(change);
    }

    const avgGain = gains / period;
    const avgLoss = losses / period;

    if (avgLoss === 0) {
      return { rsi: 100, trend: 'overbought' };
    }

    const rs = avgGain / avgLoss;
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

  // ==================== MACD CALCULATION ====================

  calculateMACD(prices: number[], fastPeriod: number = 12, slowPeriod: number = 26, signalPeriod: number = 9): MACDResult {
    if (prices.length < slowPeriod) {
      return {
        macd: 0,
        signal: 0,
        histogram: 0,
        trend: 'neutral'
      };
    }

    const ema12 = this.calculateEMA(prices, fastPeriod);
    const ema26 = this.calculateEMA(prices, slowPeriod);
    const macd = ema12 - ema26;

    // Calculate MACD line for signal calculation
    const macdValues: number[] = [];
    for (let i = slowPeriod; i < prices.length; i++) {
      const sliced = prices.slice(0, i + 1);
      if (sliced.length >= slowPeriod) {
        const e12 = this.calculateEMA(sliced, fastPeriod);
        const e26 = this.calculateEMA(sliced, slowPeriod);
        macdValues.push(e12 - e26);
      }
    }

    const signal = macdValues.length >= signalPeriod
      ? this.calculateEMA(macdValues.slice(-signalPeriod), signalPeriod)
      : 0;

    const histogram = macd - signal;

    return {
      macd: Math.round(macd * 10000) / 10000,
      signal: Math.round(signal * 10000) / 10000,
      histogram: Math.round(histogram * 10000) / 10000,
      trend: histogram > 0 ? 'bullish' : histogram < 0 ? 'bearish' : 'neutral'
    };
  }

  // ==================== EXPONENTIAL MOVING AVERAGE ====================

  private calculateEMA(prices: number[], period: number): number {
    if (prices.length < period) {
      return prices.reduce((a, b) => a + b, 0) / prices.length;
    }

    const multiplier = 2 / (period + 1);
    let ema = prices.slice(0, period).reduce((a, b) => a + b, 0) / period;

    for (let i = period; i < prices.length; i++) {
      ema = (prices[i] - ema) * multiplier + ema;
    }

    return ema;
  }

  // ==================== SIMPLE MOVING AVERAGE ====================

  calculateSMA(prices: number[], period: number): number {
    if (prices.length < period) {
      return prices.reduce((a, b) => a + b, 0) / prices.length;
    }
    return prices.slice(-period).reduce((a, b) => a + b, 0) / period;
  }

  // ==================== BOLLINGER BANDS ====================

  calculateBollingerBands(
    prices: number[],
    period: number = 20,
    stdDeviation: number = 2
  ): BollingerBands {
    const middle = this.calculateSMA(prices, period);
    const recentPrices = prices.slice(-period);

    const variance = recentPrices.reduce(
      (sum, price) => sum + Math.pow(price - middle, 2), 
      0
    ) / period;
    const std = Math.sqrt(variance);

    const upper = middle + std * stdDeviation;
    const lower = middle - std * stdDeviation;
    const width = (upper - lower) / middle;
    const percentB = (prices[prices.length - 1] - lower) / (upper - lower);

    return {
      upper: Math.round(upper * 100) / 100,
      middle: Math.round(middle * 100) / 100,
      lower: Math.round(lower * 100) / 100,
      width: Math.round(width * 10000) / 10000,
      percentB: Math.round(percentB * 100) / 100
    };
  }

  // ==================== AVERAGE TRUE RANGE ====================

  calculateATR(
    highs: number[],
    lows: number[],
    closes: number[],
    period: number = 14
  ): number {
    if (highs.length < 2 || lows.length < 2 || closes.length < 2) {
      return 0;
    }

    const trueRanges: number[] = [];

    for (let i = 1; i < Math.min(highs.length, lows.length, closes.length); i++) {
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

  // ==================== STOCHASTIC OSCILLATOR ====================

  calculateStochastic(
    highs: number[],
    lows: number[],
    closes: number[],
    kPeriod: number = 14,
    dPeriod: number = 3
  ): { k: number; d: number; trend: 'oversold' | 'neutral' | 'overbought' } {
    if (highs.length < kPeriod || lows.length < kPeriod || closes.length < kPeriod) {
      return { k: 50, d: 50, trend: 'neutral' };
    }

    const recentHighs = highs.slice(-kPeriod);
    const recentLows = lows.slice(-kPeriod);
    const currentClose = closes[closes.length - 1];

    const highestHigh = Math.max(...recentHighs);
    const lowestLow = Math.min(...recentLows);

    const k = ((currentClose - lowestLow) / (highestHigh - lowestLow)) * 100;

    // Calculate %D (smoothed %K)
    const kValues: number[] = [];
    for (let i = kPeriod; i < closes.length; i++) {
      const periodHighs = highs.slice(i - kPeriod, i);
      const periodLows = lows.slice(i - kPeriod, i);
      const periodClose = closes[i];

      const hh = Math.max(...periodHighs);
      const ll = Math.min(...periodLows);
      const kValue = ((periodClose - ll) / (hh - ll)) * 100;
      kValues.push(kValue);
    }

    const d = kValues.length >= dPeriod
      ? kValues.slice(-dPeriod).reduce((a, b) => a + b, 0) / dPeriod
      : k;

    let trend: 'oversold' | 'neutral' | 'overbought';
    if (k < 20) trend = 'oversold';
    else if (k > 80) trend = 'overbought';
    else trend = 'neutral';

    return {
      k: Math.round(k * 100) / 100,
      d: Math.round(d * 100) / 100,
      trend
    };
  }

  // ==================== WILLIAMS %R ====================

  calculateWilliamsR(
    highs: number[],
    lows: number[],
    closes: number[],
    period: number = 14
  ): { value: number; trend: 'oversold' | 'neutral' | 'overbought' } {
    if (highs.length < period || lows.length < period || closes.length < period) {
      return { value: -50, trend: 'neutral' };
    }

    const recentHighs = highs.slice(-period);
    const recentLows = lows.slice(-period);
    const currentClose = closes[closes.length - 1];

    const highestHigh = Math.max(...recentHighs);
    const lowestLow = Math.min(...recentLows);

    const williamsR = ((highestHigh - currentClose) / (highestHigh - lowestLow)) * -100;

    let trend: 'oversold' | 'neutral' | 'overbought';
    if (williamsR < -80) trend = 'oversold';
    else if (williamsR > -20) trend = 'overbought';
    else trend = 'neutral';

    return {
      value: Math.round(williamsR * 100) / 100,
      trend
    };
  }

  // ==================== COMPREHENSIVE INDICATORS ====================

  getAllIndicators(candles: Candle[], prices: number[]): TechnicalIndicators {
    const highs = candles.map(c => c.high);
    const lows = candles.map(c => c.low);
    const closes = candles.map(c => c.close);

    return {
      rsi: this.calculateRSI(prices),
      macd: this.calculateMACD(prices),
      atr: this.calculateATR(highs, lows, closes),
      sma20: this.calculateSMA(prices, 20),
      sma50: this.calculateSMA(prices, 50),
      sma200: this.calculateSMA(prices, 200),
      bollingerBands: this.calculateBollingerBands(prices, 20, 2),
      ema12: this.calculateEMA(prices, 12),
      ema26: this.calculateEMA(prices, 26),
      stochastic: this.calculateStochastic(highs, lows, closes),
      williamsR: this.calculateWilliamsR(highs, lows, closes)
    };
  }

  // ==================== TREND ANALYSIS ====================

  analyzeTrend(indicators: TechnicalIndicators): {
    shortTerm: 'bullish' | 'bearish' | 'neutral';
    mediumTerm: 'bullish' | 'bearish' | 'neutral';
    longTerm: 'bullish' | 'bearish' | 'neutral';
    overall: 'bullish' | 'bearish' | 'neutral';
  } {
    const { rsi, macd, sma20, sma50, sma200, bollingerBands } = indicators;

    // Short-term trend (RSI + MACD)
    const shortTermScore = 
      (rsi.trend === 'oversold' ? 1 : rsi.trend === 'overbought' ? -1 : 0) +
      (macd.trend === 'bullish' ? 1 : macd.trend === 'bearish' ? -1 : 0);

    // Medium-term trend (Moving averages)
    const mediumTermScore = 
      (sma20 > sma50 ? 1 : -1) +
      (macd.trend === 'bullish' ? 1 : macd.trend === 'bearish' ? -1 : 0);

    // Long-term trend (SMA200)
    const longTermScore = sma50 > sma200 ? 1 : -1;

    // Overall trend
    const overallScore = shortTermScore + mediumTermScore + longTermScore;

    return {
      shortTerm: shortTermScore > 0 ? 'bullish' : shortTermScore < 0 ? 'bearish' : 'neutral',
      mediumTerm: mediumTermScore > 0 ? 'bullish' : mediumTermScore < 0 ? 'bearish' : 'neutral',
      longTerm: longTermScore > 0 ? 'bullish' : 'bearish',
      overall: overallScore > 1 ? 'bullish' : overallScore < -1 ? 'bearish' : 'neutral'
    };
  }

  // ==================== VOLATILITY ANALYSIS ====================

  calculateVolatility(prices: number[], period: number = 20): {
    current: number;
    average: number;
    level: 'low' | 'medium' | 'high';
  } {
    if (prices.length < period) {
      return { current: 0, average: 0, level: 'low' };
    }

    const returns: number[] = [];
    for (let i = 1; i < prices.length; i++) {
      returns.push((prices[i] - prices[i - 1]) / prices[i - 1]);
    }

    const recentReturns = returns.slice(-period);
    const currentVolatility = Math.sqrt(
      recentReturns.reduce((sum, ret) => sum + ret * ret, 0) / period
    ) * Math.sqrt(252); // Annualized

    const allReturns = returns.slice(-period * 2, -period);
    const averageVolatility = allReturns.length > 0
      ? Math.sqrt(
          allReturns.reduce((sum, ret) => sum + ret * ret, 0) / allReturns.length
        ) * Math.sqrt(252)
      : currentVolatility;

    let level: 'low' | 'medium' | 'high';
    if (currentVolatility < 0.2) level = 'low';
    else if (currentVolatility < 0.5) level = 'medium';
    else level = 'high';

    return {
      current: Math.round(currentVolatility * 10000) / 10000,
      average: Math.round(averageVolatility * 10000) / 10000,
      level
    };
  }
}

export default new IndicatorService();