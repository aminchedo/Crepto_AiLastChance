import { PredictionData, TrainingMetrics, TechnicalIndicators, SentimentData } from '../types/index.js';

class AIService {
  private predictions: Map<string, PredictionData> = new Map();
  private trainingMetrics: TrainingMetrics[] = [];
  private isTraining: boolean = false;
  private modelVersion: string = '1.0.0';
  private trainingStartTime: number = 0;

  // ==================== PREDICTION GENERATION ====================

  generatePrediction(
    symbol: string,
    indicators: TechnicalIndicators,
    sentiment: SentimentData,
    priceHistory: number[]
  ): PredictionData {
    try {
      // Calculate technical score (0-100)
      const technicalScore = this.calculateTechnicalScore(indicators);

      // Calculate sentiment score (0-100)
      const sentimentScore = sentiment.overallScore;

      // Calculate momentum score
      const momentumScore = this.calculateMomentumScore(priceHistory);

      // Calculate volatility score
      const volatilityScore = this.calculateVolatilityScore(priceHistory);

      // Weighted combination
      const finalScore = (
        technicalScore * 0.4 +
        sentimentScore * 0.25 +
        momentumScore * 0.2 +
        volatilityScore * 0.15
      );

      // Calculate probabilities
      const bullishProb = this.calculateBullishProbability(finalScore, indicators);
      const bearishProb = this.calculateBearishProbability(finalScore, indicators);
      const neutralProb = 100 - bullishProb - bearishProb;

      // Determine signal
      const signal = this.determineSignal(bullishProb, bearishProb, neutralProb, indicators);

      // Calculate confidence
      const confidence = this.calculateConfidence(indicators, sentiment, priceHistory);

      // Calculate risk score
      const riskScore = this.calculateRiskScore(indicators, volatilityScore);

      // Generate price targets
      const priceTargets = this.generatePriceTargets(
        priceHistory[priceHistory.length - 1],
        signal,
        confidence
      );

      const prediction: PredictionData = {
        symbol,
        bullishProbability: Math.round(bullishProb),
        bearishProbability: Math.round(bearishProb),
        neutralProbability: Math.round(neutralProb),
        confidence: Math.round(confidence),
        signal,
        riskScore: Math.round(riskScore),
        priceTarget: priceTargets,
        timeframe: '4h',
        timestamp: Date.now(),
        modelVersion: this.modelVersion
      };

      this.predictions.set(symbol, prediction);
      return prediction;
    } catch (error) {
      console.error(`❌ Error generating prediction for ${symbol}:`, error);
      return this.getDefaultPrediction(symbol);
    }
  }

  // ==================== TECHNICAL SCORE CALCULATION ====================

  private calculateTechnicalScore(indicators: TechnicalIndicators): number {
    let score = 50; // Base neutral score

    // RSI contribution
    const rsi = indicators.rsi.rsi;
    if (rsi < 30) score += 20; // Oversold - bullish
    else if (rsi > 70) score -= 20; // Overbought - bearish
    else if (rsi > 40 && rsi < 60) score += 5; // Neutral range

    // MACD contribution
    if (indicators.macd.trend === 'bullish') score += 15;
    else if (indicators.macd.trend === 'bearish') score -= 15;

    // Moving averages
    if (indicators.sma20 > indicators.sma50) score += 10;
    else if (indicators.sma20 < indicators.sma50) score -= 10;

    if (indicators.sma50 > indicators.sma200) score += 5;
    else if (indicators.sma50 < indicators.sma200) score -= 5;

    // Bollinger Bands
    const bbPercent = indicators.bollingerBands.percentB;
    if (bbPercent < 0.2) score += 10; // Near lower band
    else if (bbPercent > 0.8) score -= 10; // Near upper band

    // Stochastic
    if (indicators.stochastic.trend === 'oversold') score += 10;
    else if (indicators.stochastic.trend === 'overbought') score -= 10;

    return Math.max(0, Math.min(100, score));
  }

  // ==================== MOMENTUM SCORE CALCULATION ====================

  private calculateMomentumScore(priceHistory: number[]): number {
    if (priceHistory.length < 20) return 50;

    const recent = priceHistory.slice(-20);
    const older = priceHistory.slice(-40, -20);

    if (older.length === 0) return 50;

    const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;
    const olderAvg = older.reduce((a, b) => a + b, 0) / older.length;

    const momentum = ((recentAvg - olderAvg) / olderAvg) * 100;
    return Math.max(0, Math.min(100, 50 + momentum * 2));
  }

  // ==================== VOLATILITY SCORE CALCULATION ====================

  private calculateVolatilityScore(priceHistory: number[]): number {
    if (priceHistory.length < 20) return 50;

    const returns: number[] = [];
    for (let i = 1; i < priceHistory.length; i++) {
      returns.push((priceHistory[i] - priceHistory[i - 1]) / priceHistory[i - 1]);
    }

    const recentReturns = returns.slice(-20);
    const volatility = Math.sqrt(
      recentReturns.reduce((sum, ret) => sum + ret * ret, 0) / recentReturns.length
    ) * Math.sqrt(252); // Annualized

    // Higher volatility = higher risk = lower score
    if (volatility < 0.2) return 70; // Low volatility - good
    else if (volatility < 0.5) return 50; // Medium volatility
    else return 30; // High volatility - risky
  }

  // ==================== PROBABILITY CALCULATIONS ====================

  private calculateBullishProbability(score: number, indicators: TechnicalIndicators): number {
    let prob = score;

    // RSI oversold condition
    if (indicators.rsi.rsi < 30) prob += 15;

    // MACD bullish crossover
    if (indicators.macd.histogram > 0 && indicators.macd.macd > indicators.macd.signal) {
      prob += 10;
    }

    // Price above key moving averages
    const currentPrice = indicators.sma20; // Approximate current price
    if (currentPrice > indicators.sma50 && currentPrice > indicators.sma200) {
      prob += 10;
    }

    return Math.min(95, prob);
  }

  private calculateBearishProbability(score: number, indicators: TechnicalIndicators): number {
    let prob = 100 - score;

    // RSI overbought condition
    if (indicators.rsi.rsi > 70) prob += 15;

    // MACD bearish crossover
    if (indicators.macd.histogram < 0 && indicators.macd.macd < indicators.macd.signal) {
      prob += 10;
    }

    // Price below key moving averages
    const currentPrice = indicators.sma20; // Approximate current price
    if (currentPrice < indicators.sma50 && currentPrice < indicators.sma200) {
      prob += 10;
    }

    return Math.min(95, prob);
  }

  // ==================== SIGNAL DETERMINATION ====================

  private determineSignal(
    bullishProb: number,
    bearishProb: number,
    neutralProb: number,
    indicators: TechnicalIndicators
  ): 'BUY' | 'SELL' | 'HOLD' {
    // Strong signals require high confidence
    if (bullishProb > 75 && indicators.rsi.rsi < 40) return 'BUY';
    if (bearishProb > 75 && indicators.rsi.rsi > 60) return 'SELL';

    // Medium signals with additional conditions
    if (bullishProb > 65 && indicators.macd.trend === 'bullish') return 'BUY';
    if (bearishProb > 65 && indicators.macd.trend === 'bearish') return 'SELL';

    // Default to HOLD
    return 'HOLD';
  }

  // ==================== CONFIDENCE CALCULATION ====================

  private calculateConfidence(
    indicators: TechnicalIndicators,
    sentiment: SentimentData,
    priceHistory: number[]
  ): number {
    let confidence = 50; // Base confidence

    // Technical indicators agreement
    const technicalAgreement = this.calculateTechnicalAgreement(indicators);
    confidence += technicalAgreement * 0.3;

    // Sentiment confidence
    confidence += sentiment.confidence * 0.2;

    // Price trend consistency
    const trendConsistency = this.calculateTrendConsistency(priceHistory);
    confidence += trendConsistency * 0.2;

    // Volatility factor (lower volatility = higher confidence)
    const volatility = this.calculateVolatilityScore(priceHistory);
    confidence += (100 - volatility) * 0.1;

    return Math.max(30, Math.min(95, confidence));
  }

  private calculateTechnicalAgreement(indicators: TechnicalIndicators): number {
    let agreement = 0;
    let total = 0;

    // RSI and MACD agreement
    if ((indicators.rsi.trend === 'oversold' && indicators.macd.trend === 'bullish') ||
        (indicators.rsi.trend === 'overbought' && indicators.macd.trend === 'bearish')) {
      agreement += 1;
    }
    total += 1;

    // Moving average alignment
    if (indicators.sma20 > indicators.sma50 && indicators.sma50 > indicators.sma200) {
      agreement += 1;
    } else if (indicators.sma20 < indicators.sma50 && indicators.sma50 < indicators.sma200) {
      agreement += 1;
    }
    total += 1;

    // Bollinger Bands and price position
    const bbPercent = indicators.bollingerBands.percentB;
    if ((bbPercent < 0.2 && indicators.rsi.trend === 'oversold') ||
        (bbPercent > 0.8 && indicators.rsi.trend === 'overbought')) {
      agreement += 1;
    }
    total += 1;

    return (agreement / total) * 100;
  }

  private calculateTrendConsistency(priceHistory: number[]): number {
    if (priceHistory.length < 10) return 50;

    const recent = priceHistory.slice(-10);
    const trend = recent[recent.length - 1] - recent[0];
    const volatility = Math.sqrt(
      recent.reduce((sum, price, i) => {
        if (i === 0) return sum;
        const change = (price - recent[i - 1]) / recent[i - 1];
        return sum + change * change;
      }, 0) / (recent.length - 1)
    );

    // Higher trend consistency with lower volatility
    const consistency = Math.abs(trend) / (volatility * recent[0]);
    return Math.min(100, consistency * 1000);
  }

  // ==================== RISK SCORE CALCULATION ====================

  private calculateRiskScore(indicators: TechnicalIndicators, volatilityScore: number): number {
    let risk = 50; // Base risk

    // High volatility increases risk
    risk += (100 - volatilityScore) * 0.3;

    // Extreme RSI values increase risk
    if (indicators.rsi.rsi < 20 || indicators.rsi.rsi > 80) {
      risk += 20;
    }

    // High ATR increases risk
    if (indicators.atr > indicators.sma20 * 0.05) { // 5% of price
      risk += 15;
    }

    // Divergence between indicators increases risk
    if (indicators.rsi.trend !== indicators.macd.trend) {
      risk += 10;
    }

    return Math.max(10, Math.min(90, risk));
  }

  // ==================== PRICE TARGETS ====================

  private generatePriceTargets(
    currentPrice: number,
    signal: 'BUY' | 'SELL' | 'HOLD',
    confidence: number
  ): { short: number; medium: number; long: number } {
    const confidenceFactor = confidence / 100;
    const baseMultiplier = signal === 'BUY' ? 1.1 : signal === 'SELL' ? 0.9 : 1.0;

    return {
      short: currentPrice * (baseMultiplier + (confidenceFactor - 0.5) * 0.1),
      medium: currentPrice * (baseMultiplier + (confidenceFactor - 0.5) * 0.2),
      long: currentPrice * (baseMultiplier + (confidenceFactor - 0.5) * 0.3)
    };
  }

  // ==================== TRAINING SIMULATION ====================

  startTraining(): void {
    this.isTraining = true;
    this.trainingStartTime = Date.now();
    console.log('🤖 AI training started');
  }

  stopTraining(): void {
    this.isTraining = false;
    console.log('🛑 AI training stopped');
  }

  simulateTraining(epoch: number): TrainingMetrics {
    if (!this.isTraining) {
      throw new Error('Training not started');
    }

    // Simulate realistic training metrics
    const baseLoss = 0.5 * Math.exp(-epoch / 100);
    const noise = (Math.random() - 0.5) * 0.1;
    const loss = Math.max(0.001, baseLoss + noise);

    const mse = loss * 1.2;
    const mae = loss * 0.8;
    const r2Score = Math.min(0.99, 0.5 + epoch / 200 + Math.random() * 0.1);
    const learningRate = 0.001 * Math.exp(-epoch / 50);
    const gradientNorm = Math.max(0.01, 10 * Math.exp(-epoch / 100) + Math.random() * 2);
    const validationLoss = loss * 1.1;
    const accuracy = Math.min(0.95, 0.6 + epoch / 300 + Math.random() * 0.1);
    const precision = accuracy * 0.9;
    const recall = accuracy * 0.85;
    const f1Score = 2 * (precision * recall) / (precision + recall);

    const metrics: TrainingMetrics = {
      epoch,
      loss: Math.round(loss * 10000) / 10000,
      mse: Math.round(mse * 10000) / 10000,
      mae: Math.round(mae * 10000) / 10000,
      r2Score: Math.round(r2Score * 10000) / 10000,
      learningRate: Math.round(learningRate * 1000000) / 1000000,
      gradientNorm: Math.round(gradientNorm * 10000) / 10000,
      validationLoss: Math.round(validationLoss * 10000) / 10000,
      accuracy: Math.round(accuracy * 10000) / 10000,
      precision: Math.round(precision * 10000) / 10000,
      recall: Math.round(recall * 10000) / 10000,
      f1Score: Math.round(f1Score * 10000) / 10000,
      timestamp: Date.now()
    };

    this.trainingMetrics.push(metrics);

    // Keep only last 100 metrics
    if (this.trainingMetrics.length > 100) {
      this.trainingMetrics.shift();
    }

    return metrics;
  }

  // ==================== GETTERS ====================

  getPrediction(symbol: string): PredictionData | null {
    return this.predictions.get(symbol) || null;
  }

  getAllPredictions(): Map<string, PredictionData> {
    return new Map(this.predictions);
  }

  getTrainingMetrics(): TrainingMetrics[] {
    return [...this.trainingMetrics];
  }

  getIsTraining(): boolean {
    return this.isTraining;
  }

  getTrainingDuration(): number {
    return this.isTraining ? Date.now() - this.trainingStartTime : 0;
  }

  // ==================== UTILITY METHODS ====================

  private getDefaultPrediction(symbol: string): PredictionData {
    return {
      symbol,
      bullishProbability: 33,
      bearishProbability: 33,
      neutralProbability: 34,
      confidence: 50,
      signal: 'HOLD',
      riskScore: 50,
      timeframe: '4h',
      timestamp: Date.now(),
      modelVersion: this.modelVersion
    };
  }

  clearPredictions(): void {
    this.predictions.clear();
    console.log('🧹 AI predictions cleared');
  }

  clearTrainingMetrics(): void {
    this.trainingMetrics = [];
    console.log('🧹 Training metrics cleared');
  }

  // ==================== MODEL MANAGEMENT ====================

  updateModelVersion(version: string): void {
    this.modelVersion = version;
    console.log(`🔄 Model version updated to ${version}`);
  }

  getModelVersion(): string {
    return this.modelVersion;
  }

  // ==================== HEALTH CHECK ====================

  healthCheck(): boolean {
    return true; // AI service is always healthy
  }
}

export default new AIService();