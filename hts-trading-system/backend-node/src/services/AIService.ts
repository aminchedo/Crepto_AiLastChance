import { PredictionData, TrainingMetrics } from '../types/index';

class AIService {
  private predictions: Map<string, PredictionData> = new Map();
  private trainingMetrics: TrainingMetrics[] = [];
  private isTraining = false;

  generatePrediction(
    symbol: string,
    rsi: number,
    macd: number,
    sentiment: number
  ): PredictionData {
    // Simplified neural network simulation
    const rsiWeight = (100 - Math.abs(rsi - 50)) / 100;
    const macdWeight = Math.max(0, macd);
    const sentimentWeight = sentiment / 100;

    // Calculate probabilities
    const bullishScore = (rsiWeight * 0.4 + sentimentWeight * 0.3 + (macdWeight > 0 ? 1 : 0) * 0.3) * 100;
    const bearishScore = 100 - bullishScore;
    const neutralScore = 30;

    const totalScore = bullishScore + bearishScore + neutralScore;
    const bullishProb = (bullishScore / totalScore) * 100;
    const bearishProb = (bearishScore / totalScore) * 100;
    const neutralProb = (neutralScore / totalScore) * 100;

    // Determine signal
    let signal: 'BUY' | 'SELL' | 'HOLD';
    if (bullishProb > 70 && rsi < 30) signal = 'BUY';
    else if (bearishProb > 70 && rsi > 70) signal = 'SELL';
    else signal = 'HOLD';

    // Calculate confidence
    const confidence = Math.max(bullishProb, bearishProb, neutralProb);

    // Risk score (inverse of confidence)
    const riskScore = 100 - confidence;

    const prediction: PredictionData = {
      symbol,
      bullishProbability: Math.round(bullishProb),
      bearishProbability: Math.round(bearishProb),
      neutralProbability: Math.round(neutralProb),
      confidence: Math.round(confidence),
      signal,
      riskScore: Math.round(riskScore),
      timestamp: Date.now()
    };

    this.predictions.set(symbol, prediction);
    return prediction;
  }

  simulateTraining(epoch: number): TrainingMetrics {
    // Simulate training with realistic metrics
    const baseMetrics = {
      epoch,
      loss: Math.max(0.01, 0.5 * Math.exp(-epoch / 100)),
      mse: Math.max(0.001, 0.1 * Math.exp(-epoch / 50)),
      mae: Math.max(0.0005, 0.05 * Math.exp(-epoch / 50)),
      r2Score: Math.min(0.99, 0.5 + epoch / 200),
      learningRate: 0.001 * Math.exp(-epoch / 50),
      gradientNorm: Math.max(0.01, 10 * Math.exp(-epoch / 100)),
      timestamp: Date.now()
    };

    this.trainingMetrics.push(baseMetrics);

    // Keep last 100 metrics
    if (this.trainingMetrics.length > 100) {
      this.trainingMetrics.shift();
    }

    return baseMetrics;
  }

  startTraining(): void {
    this.isTraining = true;
    console.log('🤖 Training started');
  }

  stopTraining(): void {
    this.isTraining = false;
    console.log('🛑 Training stopped');
  }

  getTrainingMetrics(): TrainingMetrics[] {
    return this.trainingMetrics;
  }

  getPrediction(symbol: string): PredictionData | null {
    return this.predictions.get(symbol) || null;
  }
}

export default new AIService();
