interface RSIResult {
  rsi: number;
  trend: 'oversold' | 'neutral' | 'overbought';
}

interface MACDResult {
  macd: number;
  signal: number;
  histogram: number;
  trend: 'bullish' | 'bearish' | 'neutral';
}

class IndicatorService {
  
  // Calculate RSI (Relative Strength Index)
  calculateRSI(prices: number[], period: number = 14): RSIResult {
    if (prices.length < period + 1) {
      return { rsi: 50, trend: 'neutral' };
    }

    let gains = 0;
    let losses = 0;

    // Calculate average gain and loss
    for (let i = prices.length - period; i < prices.length; i++) {
      const currentPrice = prices[i];
      const previousPrice = prices[i - 1];
      if (currentPrice !== undefined && previousPrice !== undefined) {
        const change = currentPrice - previousPrice;
        if (change > 0) {
          gains += change;
        } else {
          losses += Math.abs(change);
        }
      }
    }

    const avgGain = gains / period;
    const avgLoss = losses / period;

    const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
    const rsi = 100 - (100 / (1 + rs));

    // Determine trend
    let trend: 'oversold' | 'neutral' | 'overbought';
    if (rsi < 30) trend = 'oversold';
    else if (rsi > 70) trend = 'overbought';
    else trend = 'neutral';

    return {
      rsi: Math.round(rsi * 100) / 100,
      trend
    };
  }

  // Calculate MACD (Moving Average Convergence Divergence)
  calculateMACD(prices: number[]): MACDResult {
    if (prices.length < 26) {
      return {
        macd: 0,
        signal: 0,
        histogram: 0,
        trend: 'neutral'
      };
    }

    // Calculate EMAs
    const ema12 = this.calculateEMA(prices, 12);
    const ema26 = this.calculateEMA(prices, 26);

    const macd = ema12 - ema26;

    // Calculate signal line
    const recentPrices = prices.slice(-35);
    const macdValues = [];
    
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
    if (prices.length < period) {
      const lastPrice = prices[prices.length - 1];
      return lastPrice !== undefined ? lastPrice : 0;
    }

    const multiplier = 2 / (period + 1);
    let ema = prices.slice(0, period).reduce((a, b) => a + b, 0) / period;

    for (let i = period; i < prices.length; i++) {
      const currentPrice = prices[i];
      if (currentPrice !== undefined) {
        ema = (currentPrice - ema) * multiplier + ema;
      }
    }

    return ema;
  }

  // Calculate ATR (Average True Range)
  calculateATR(
    highs: number[],
    lows: number[],
    closes: number[],
    period: number = 14
  ): number {
    const trueRanges: number[] = [];

    for (let i = 1; i < closes.length; i++) {
      const currentHigh = highs[i];
      const currentLow = lows[i];
      const currentClose = closes[i];
      const previousClose = closes[i - 1];
      
      if (currentHigh !== undefined && currentLow !== undefined && 
          currentClose !== undefined && previousClose !== undefined) {
        const tr = Math.max(
          currentHigh - currentLow,
          Math.abs(currentHigh - previousClose),
          Math.abs(currentLow - previousClose)
        );
        trueRanges.push(tr);
      }
    }

    if (trueRanges.length < period) {
      return trueRanges.reduce((a, b) => a + b, 0) / trueRanges.length;
    }

    const atr = trueRanges.slice(-period)
      .reduce((a, b) => a + b, 0) / period;

    return Math.round(atr * 100) / 100;
  }
}

export default new IndicatorService();