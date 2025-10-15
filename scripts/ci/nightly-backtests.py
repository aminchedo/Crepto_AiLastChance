#!/usr/bin/env python3
"""
Nightly backtests for BOLT AI Neural Agent System
"""
import os
import sys
import asyncio
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

from backend.ml.trainer import ModelTrainer
from backend.ml.model import CryptoLSTMModel
from backend.services.market_service import MarketService
from backend.ml.backtester import Backtester
from backend.ml.metrics import MetricsCalculator
from backend.db.sqlite_manager import SQLiteManager
from backend.config import Settings


class NightlyBacktester:
    """Nightly backtesting system"""
    
    def __init__(self):
        self.setup_logging()
        self.settings = self.load_settings()
        self.db_manager = SQLiteManager(
            self.settings.SQLITE_DB_PATH,
            self.settings.SQLITE_ENCRYPTION_KEY
        )
        self.market_service = MarketService()
        self.trainer = ModelTrainer()
        self.backtester = Backtester()
        self.metrics_calculator = MetricsCalculator()
        
        # Backtest configuration
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']
        self.timeframes = ['1h', '4h', '1d']
        self.backtest_periods = {
            'short': 30,   # 30 days
            'medium': 90,  # 90 days
            'long': 180    # 180 days
        }
        
        # Results storage
        self.results = {}
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('nightly_backtests.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_settings(self) -> Settings:
        """Load application settings"""
        return Settings(
            DATABASE_URL="sqlite:///backtest.db",
            SQLITE_DB_PATH="backtest.db",
            SQLITE_ENCRYPTION_KEY="backtest_key_32_chars_long_12345",
            REDIS_URL="redis://localhost:6379/1",
            SECRET_KEY="backtest_secret_key",
            ENVIRONMENT="backtest"
        )
    
    async def fetch_market_data(self, symbol: str, timeframe: str, days: int) -> pd.DataFrame:
        """Fetch market data for backtesting"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            self.logger.info(f"Fetching {symbol} data for {timeframe} from {start_date} to {end_date}")
            
            # Fetch data from market service
            data = await self.market_service.get_historical_data(
                symbols=[symbol],
                interval=timeframe,
                start_time=start_date,
                end_time=end_date
            )
            
            if not data:
                self.logger.warning(f"No data received for {symbol} {timeframe}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame([d.model_dump() for d in data])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp').sort_index()
            
            self.logger.info(f"Fetched {len(df)} records for {symbol} {timeframe}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol} {timeframe}: {e}")
            return pd.DataFrame()
    
    async def train_model(self, symbol: str, timeframe: str, training_data: pd.DataFrame) -> Optional[CryptoLSTMModel]:
        """Train model on historical data"""
        try:
            self.logger.info(f"Training model for {symbol} {timeframe}")
            
            # Prepare training data
            if len(training_data) < 1000:
                self.logger.warning(f"Insufficient data for training {symbol} {timeframe}: {len(training_data)} records")
                return None
            
            # Split data for training (80%) and validation (20%)
            split_idx = int(len(training_data) * 0.8)
            train_data = training_data.iloc[:split_idx]
            val_data = training_data.iloc[split_idx:]
            
            # Train model
            model_config = {
                'learning_rate': 0.001,
                'sequence_length': 60,
                'lstm_units': [64, 32],
                'dropout_rate': 0.2,
                'dense_units': [16, 8],
                'activation': 'relu',
                'initializer': 'xavier_uniform',
                'gradient_clip_norm': 1.0,
                'early_stopping_patience': 10,
                'batch_size': 32,
                'epochs': 50
            }
            
            # Mock database session for training
            class MockDB:
                pass
            
            mock_db = MockDB()
            
            result = await self.trainer.train_model(
                db=mock_db,
                epochs=model_config['epochs'],
                symbols=[symbol],
                model_config=model_config,
                seed=42
            )
            
            if result['status'] == 'completed':
                self.logger.info(f"Model training completed for {symbol} {timeframe}")
                return self.trainer.prediction_engine.model
            else:
                self.logger.error(f"Model training failed for {symbol} {timeframe}: {result['message']}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error training model for {symbol} {timeframe}: {e}")
            return None
    
    async def run_backtest(self, symbol: str, timeframe: str, model: CryptoLSTMModel, 
                          test_data: pd.DataFrame) -> Dict:
        """Run backtest on test data"""
        try:
            self.logger.info(f"Running backtest for {symbol} {timeframe}")
            
            if len(test_data) < 100:
                self.logger.warning(f"Insufficient test data for {symbol} {timeframe}: {len(test_data)} records")
                return {}
            
            # Prepare test data
            test_data = test_data.copy()
            test_data['returns'] = test_data['close'].pct_change()
            test_data = test_data.dropna()
            
            # Generate predictions
            predictions = []
            confidence_scores = []
            
            sequence_length = 60
            for i in range(sequence_length, len(test_data)):
                # Prepare input sequence
                input_data = test_data.iloc[i-sequence_length:i][['open', 'high', 'low', 'close', 'volume']].values
                
                # Normalize input data
                input_data = (input_data - input_data.mean(axis=0)) / (input_data.std(axis=0) + 1e-8)
                
                # Reshape for model input
                X = input_data.reshape(1, sequence_length, -1)
                
                # Generate prediction
                try:
                    prediction = model.predict(X)
                    predictions.append(prediction)
                    confidence_scores.append(np.max(prediction))
                except Exception as e:
                    self.logger.warning(f"Prediction failed at index {i}: {e}")
                    predictions.append([0.33, 0.33, 0.34])  # Neutral prediction
                    confidence_scores.append(0.5)
            
            # Align predictions with test data
            test_data = test_data.iloc[sequence_length:].copy()
            test_data['prediction'] = predictions
            test_data['confidence'] = confidence_scores
            
            # Convert predictions to actions
            test_data['action'] = test_data['prediction'].apply(
                lambda x: 'BUY' if x[0] > 0.6 else 'SELL' if x[1] > 0.6 else 'HOLD'
            )
            
            # Calculate returns
            test_data['strategy_returns'] = 0.0
            test_data['position'] = 0
            
            for i in range(1, len(test_data)):
                if test_data.iloc[i]['action'] == 'BUY' and test_data.iloc[i-1]['action'] != 'BUY':
                    test_data.iloc[i, test_data.columns.get_loc('position')] = 1
                elif test_data.iloc[i]['action'] == 'SELL' and test_data.iloc[i-1]['action'] != 'SELL':
                    test_data.iloc[i, test_data.columns.get_loc('position')] = -1
                else:
                    test_data.iloc[i, test_data.columns.get_loc('position')] = test_data.iloc[i-1]['position']
                
                # Calculate strategy returns
                if test_data.iloc[i]['position'] != 0:
                    test_data.iloc[i, test_data.columns.get_loc('strategy_returns')] = \
                        test_data.iloc[i]['position'] * test_data.iloc[i]['returns']
            
            # Calculate metrics
            strategy_returns = test_data['strategy_returns'].dropna()
            market_returns = test_data['returns'].dropna()
            
            if len(strategy_returns) == 0:
                self.logger.warning(f"No strategy returns calculated for {symbol} {timeframe}")
                return {}
            
            # Calculate performance metrics
            total_return = (1 + strategy_returns).prod() - 1
            annualized_return = (1 + total_return) ** (365 / len(strategy_returns)) - 1
            volatility = strategy_returns.std() * np.sqrt(365)
            sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
            
            # Calculate drawdown
            cumulative_returns = (1 + strategy_returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # Calculate directional accuracy
            actual_direction = (market_returns > 0).astype(int)
            predicted_direction = (test_data['prediction'].apply(lambda x: x[0] > x[1])).astype(int)
            directional_accuracy = (actual_direction == predicted_direction).mean()
            
            # Calculate win rate
            winning_trades = (strategy_returns > 0).sum()
            total_trades = (strategy_returns != 0).sum()
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            # Calculate profit factor
            gross_profit = strategy_returns[strategy_returns > 0].sum()
            gross_loss = abs(strategy_returns[strategy_returns < 0].sum())
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            
            results = {
                'symbol': symbol,
                'timeframe': timeframe,
                'total_return': float(total_return),
                'annualized_return': float(annualized_return),
                'volatility': float(volatility),
                'sharpe_ratio': float(sharpe_ratio),
                'max_drawdown': float(max_drawdown),
                'directional_accuracy': float(directional_accuracy),
                'win_rate': float(win_rate),
                'profit_factor': float(profit_factor),
                'total_trades': int(total_trades),
                'winning_trades': int(winning_trades),
                'losing_trades': int(total_trades - winning_trades),
                'avg_confidence': float(test_data['confidence'].mean()),
                'test_period_days': len(test_data),
                'backtest_date': datetime.now().isoformat()
            }
            
            self.logger.info(f"Backtest completed for {symbol} {timeframe}: "
                           f"Return={total_return:.2%}, Sharpe={sharpe_ratio:.2f}, "
                           f"Accuracy={directional_accuracy:.2%}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error running backtest for {symbol} {timeframe}: {e}")
            return {}
    
    async def run_all_backtests(self):
        """Run backtests for all symbols and timeframes"""
        self.logger.info("Starting nightly backtests")
        
        for period_name, days in self.backtest_periods.items():
            self.logger.info(f"Running {period_name} period backtests ({days} days)")
            
            period_results = {}
            
            for symbol in self.symbols:
                symbol_results = {}
                
                for timeframe in self.timeframes:
                    try:
                        # Fetch data
                        all_data = await self.fetch_market_data(symbol, timeframe, days)
                        
                        if all_data.empty:
                            self.logger.warning(f"No data available for {symbol} {timeframe}")
                            continue
                        
                        # Split data for training and testing
                        split_idx = int(len(all_data) * 0.7)  # 70% for training
                        training_data = all_data.iloc[:split_idx]
                        test_data = all_data.iloc[split_idx:]
                        
                        # Train model
                        model = await self.train_model(symbol, timeframe, training_data)
                        
                        if model is None:
                            self.logger.warning(f"Model training failed for {symbol} {timeframe}")
                            continue
                        
                        # Run backtest
                        backtest_results = await self.run_backtest(symbol, timeframe, model, test_data)
                        
                        if backtest_results:
                            symbol_results[timeframe] = backtest_results
                            
                    except Exception as e:
                        self.logger.error(f"Error processing {symbol} {timeframe}: {e}")
                        continue
                
                if symbol_results:
                    period_results[symbol] = symbol_results
            
            if period_results:
                self.results[period_name] = period_results
        
        self.logger.info("Nightly backtests completed")
    
    def generate_summary_report(self) -> Dict:
        """Generate summary report from all backtest results"""
        summary = {
            'backtest_date': datetime.now().isoformat(),
            'total_symbols': len(self.symbols),
            'total_timeframes': len(self.timeframes),
            'periods_tested': list(self.backtest_periods.keys()),
            'overall_metrics': {},
            'best_performers': {},
            'worst_performers': {},
            'period_summaries': {}
        }
        
        all_results = []
        
        # Collect all results
        for period_name, period_results in self.results.items():
            period_summary = {
                'period': period_name,
                'symbols_tested': len(period_results),
                'avg_return': 0,
                'avg_sharpe': 0,
                'avg_accuracy': 0,
                'total_trades': 0
            }
            
            period_returns = []
            period_sharpes = []
            period_accuracies = []
            period_trades = 0
            
            for symbol, symbol_results in period_results.items():
                for timeframe, results in symbol_results.items():
                    all_results.append({
                        'period': period_name,
                        'symbol': symbol,
                        'timeframe': timeframe,
                        **results
                    })
                    
                    period_returns.append(results['total_return'])
                    period_sharpes.append(results['sharpe_ratio'])
                    period_accuracies.append(results['directional_accuracy'])
                    period_trades += results['total_trades']
            
            if period_returns:
                period_summary['avg_return'] = np.mean(period_returns)
                period_summary['avg_sharpe'] = np.mean(period_sharpes)
                period_summary['avg_accuracy'] = np.mean(period_accuracies)
                period_summary['total_trades'] = period_trades
            
            summary['period_summaries'][period_name] = period_summary
        
        # Calculate overall metrics
        if all_results:
            summary['overall_metrics'] = {
                'avg_return': np.mean([r['total_return'] for r in all_results]),
                'avg_sharpe': np.mean([r['sharpe_ratio'] for r in all_results]),
                'avg_accuracy': np.mean([r['directional_accuracy'] for r in all_results]),
                'total_trades': sum([r['total_trades'] for r in all_results]),
                'best_return': max([r['total_return'] for r in all_results]),
                'worst_return': min([r['total_return'] for r in all_results]),
                'best_sharpe': max([r['sharpe_ratio'] for r in all_results]),
                'worst_sharpe': min([r['sharpe_ratio'] for r in all_results])
            }
            
            # Find best and worst performers
            best_result = max(all_results, key=lambda x: x['sharpe_ratio'])
            worst_result = min(all_results, key=lambda x: x['sharpe_ratio'])
            
            summary['best_performers'] = {
                'symbol': best_result['symbol'],
                'timeframe': best_result['timeframe'],
                'period': best_result['period'],
                'return': best_result['total_return'],
                'sharpe': best_result['sharpe_ratio'],
                'accuracy': best_result['directional_accuracy']
            }
            
            summary['worst_performers'] = {
                'symbol': worst_result['symbol'],
                'timeframe': worst_result['timeframe'],
                'period': worst_result['period'],
                'return': worst_result['total_return'],
                'sharpe': worst_result['sharpe_ratio'],
                'accuracy': worst_result['directional_accuracy']
            }
        
        return summary
    
    def save_results(self):
        """Save backtest results to files"""
        # Create reports directory
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = reports_dir / f"backtest-detailed-{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Save summary report
        summary = self.generate_summary_report()
        summary_file = reports_dir / f"backtest-summary-{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Save summary for CI/CD
        summary_file_ci = reports_dir / "backtest-summary.json"
        with open(summary_file_ci, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.logger.info(f"Results saved to {reports_dir}")
        
        return summary


async def main():
    """Main function"""
    backtester = NightlyBacktester()
    
    try:
        # Run all backtests
        await backtester.run_all_backtests()
        
        # Generate and save summary
        summary = backtester.save_results()
        
        # Print summary
        print("\n" + "="*60)
        print("NIGHTLY BACKTEST SUMMARY")
        print("="*60)
        print(f"Date: {summary['backtest_date']}")
        print(f"Symbols Tested: {summary['total_symbols']}")
        print(f"Timeframes Tested: {summary['total_timeframes']}")
        print(f"Periods Tested: {', '.join(summary['periods_tested'])}")
        
        if summary['overall_metrics']:
            metrics = summary['overall_metrics']
            print(f"\nOverall Performance:")
            print(f"  Average Return: {metrics['avg_return']:.2%}")
            print(f"  Average Sharpe: {metrics['avg_sharpe']:.2f}")
            print(f"  Average Accuracy: {metrics['avg_accuracy']:.2%}")
            print(f"  Total Trades: {metrics['total_trades']}")
            
            print(f"\nBest Performer:")
            best = summary['best_performers']
            print(f"  {best['symbol']} ({best['timeframe']}) - Return: {best['return']:.2%}, Sharpe: {best['sharpe']:.2f}")
            
            print(f"\nWorst Performer:")
            worst = summary['worst_performers']
            print(f"  {worst['symbol']} ({worst['timeframe']}) - Return: {worst['return']:.2%}, Sharpe: {worst['sharpe']:.2f}")
        
        print("="*60)
        
    except Exception as e:
        backtester.logger.error(f"Nightly backtests failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
