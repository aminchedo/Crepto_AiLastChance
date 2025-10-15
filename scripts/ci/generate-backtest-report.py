#!/usr/bin/env python3
"""
Generate backtest report for BOLT AI Neural Agent System
"""
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import base64
from io import BytesIO


class BacktestReportGenerator:
    """Generate HTML and PDF reports from backtest results"""
    
    def __init__(self):
        self.reports_dir = Path("reports")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def load_results(self) -> Dict:
        """Load backtest results"""
        summary_file = self.reports_dir / "backtest-summary.json"
        
        if not summary_file.exists():
            raise FileNotFoundError(f"Summary file not found: {summary_file}")
        
        with open(summary_file, 'r') as f:
            return json.load(f)
    
    def create_performance_chart(self, results: Dict) -> str:
        """Create performance comparison chart"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('BOLT AI Neural Agent System - Performance Overview', fontsize=16, fontweight='bold')
        
        # Prepare data for plotting
        all_results = []
        for period_name, period_results in results.get('results', {}).items():
            for symbol, symbol_results in period_results.items():
                for timeframe, result in symbol_results.items():
                    all_results.append({
                        'Symbol': symbol,
                        'Timeframe': timeframe,
                        'Period': period_name,
                        'Return': result['total_return'],
                        'Sharpe': result['sharpe_ratio'],
                        'Accuracy': result['directional_accuracy'],
                        'Max Drawdown': result['max_drawdown']
                    })
        
        if not all_results:
            return ""
        
        df = pd.DataFrame(all_results)
        
        # 1. Returns by Symbol
        ax1 = axes[0, 0]
        symbol_returns = df.groupby('Symbol')['Return'].mean().sort_values(ascending=True)
        symbol_returns.plot(kind='barh', ax=ax1, color='skyblue')
        ax1.set_title('Average Returns by Symbol')
        ax1.set_xlabel('Return')
        ax1.grid(True, alpha=0.3)
        
        # 2. Sharpe Ratio by Timeframe
        ax2 = axes[0, 1]
        timeframe_sharpe = df.groupby('Timeframe')['Sharpe'].mean().sort_values(ascending=True)
        timeframe_sharpe.plot(kind='bar', ax=ax2, color='lightcoral')
        ax2.set_title('Average Sharpe Ratio by Timeframe')
        ax2.set_ylabel('Sharpe Ratio')
        ax2.grid(True, alpha=0.3)
        
        # 3. Accuracy Distribution
        ax3 = axes[1, 0]
        ax3.hist(df['Accuracy'], bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
        ax3.axvline(df['Accuracy'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {df["Accuracy"].mean():.2%}')
        ax3.set_title('Directional Accuracy Distribution')
        ax3.set_xlabel('Accuracy')
        ax3.set_ylabel('Frequency')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Return vs Risk Scatter
        ax4 = axes[1, 1]
        scatter = ax4.scatter(df['Max Drawdown'], df['Return'], c=df['Sharpe'], cmap='viridis', alpha=0.7)
        ax4.set_title('Return vs Risk (Max Drawdown)')
        ax4.set_xlabel('Max Drawdown')
        ax4.set_ylabel('Return')
        ax4.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax4)
        cbar.set_label('Sharpe Ratio')
        
        plt.tight_layout()
        
        # Convert to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def create_period_comparison_chart(self, results: Dict) -> str:
        """Create period comparison chart"""
        if 'period_summaries' not in results:
            return ""
        
        periods = list(results['period_summaries'].keys())
        metrics = ['avg_return', 'avg_sharpe', 'avg_accuracy']
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Performance by Backtest Period', fontsize=16, fontweight='bold')
        
        for i, metric in enumerate(metrics):
            ax = axes[i]
            values = [results['period_summaries'][period][metric] for period in periods]
            
            bars = ax.bar(periods, values, color=['skyblue', 'lightcoral', 'lightgreen'][i])
            ax.set_title(f'Average {metric.replace("_", " ").title()}')
            ax.set_ylabel(metric.replace('_', ' ').title())
            ax.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value:.3f}' if metric == 'avg_sharpe' else f'{value:.2%}',
                       ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Convert to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def generate_html_report(self, results: Dict) -> str:
        """Generate HTML report"""
        performance_chart = self.create_performance_chart(results)
        period_chart = self.create_period_comparison_chart(results)
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>BOLT AI Neural Agent System - Backtest Report</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 3px solid #007acc;
                }}
                .header h1 {{
                    color: #007acc;
                    margin: 0;
                    font-size: 2.5em;
                }}
                .header p {{
                    color: #666;
                    margin: 10px 0 0 0;
                    font-size: 1.1em;
                }}
                .summary {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .summary-card {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                }}
                .summary-card h3 {{
                    margin: 0 0 10px 0;
                    font-size: 1.2em;
                }}
                .summary-card .value {{
                    font-size: 2em;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .charts {{
                    margin: 30px 0;
                }}
                .chart-container {{
                    text-align: center;
                    margin: 20px 0;
                }}
                .chart-container img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .details {{
                    margin-top: 30px;
                }}
                .details h2 {{
                    color: #007acc;
                    border-bottom: 2px solid #007acc;
                    padding-bottom: 10px;
                }}
                .details table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                .details th, .details td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                .details th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                }}
                .details tr:hover {{
                    background-color: #f5f5f5;
                }}
                .positive {{
                    color: #28a745;
                    font-weight: bold;
                }}
                .negative {{
                    color: #dc3545;
                    font-weight: bold;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>BOLT AI Neural Agent System</h1>
                    <p>Backtest Report - {results.get('backtest_date', 'Unknown Date')}</p>
                </div>
                
                <div class="summary">
                    <div class="summary-card">
                        <h3>Symbols Tested</h3>
                        <div class="value">{results.get('total_symbols', 0)}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Timeframes Tested</h3>
                        <div class="value">{results.get('total_timeframes', 0)}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Total Trades</h3>
                        <div class="value">{results.get('overall_metrics', {}).get('total_trades', 0)}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Average Accuracy</h3>
                        <div class="value">{results.get('overall_metrics', {}).get('avg_accuracy', 0):.1%}</div>
                    </div>
                </div>
                
                <div class="charts">
                    <div class="chart-container">
                        <h2>Performance Overview</h2>
                        <img src="data:image/png;base64,{performance_chart}" alt="Performance Charts">
                    </div>
                    
                    <div class="chart-container">
                        <h2>Period Comparison</h2>
                        <img src="data:image/png;base64,{period_chart}" alt="Period Comparison">
                    </div>
                </div>
                
                <div class="details">
                    <h2>Overall Performance Metrics</h2>
                    <table>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                            <th>Best</th>
                            <th>Worst</th>
                        </tr>
                        <tr>
                            <td>Average Return</td>
                            <td class="{'positive' if results.get('overall_metrics', {}).get('avg_return', 0) > 0 else 'negative'}">
                                {results.get('overall_metrics', {}).get('avg_return', 0):.2%}
                            </td>
                            <td class="positive">{results.get('overall_metrics', {}).get('best_return', 0):.2%}</td>
                            <td class="negative">{results.get('overall_metrics', {}).get('worst_return', 0):.2%}</td>
                        </tr>
                        <tr>
                            <td>Average Sharpe Ratio</td>
                            <td class="{'positive' if results.get('overall_metrics', {}).get('avg_sharpe', 0) > 0 else 'negative'}">
                                {results.get('overall_metrics', {}).get('avg_sharpe', 0):.2f}
                            </td>
                            <td class="positive">{results.get('overall_metrics', {}).get('best_sharpe', 0):.2f}</td>
                            <td class="negative">{results.get('overall_metrics', {}).get('worst_sharpe', 0):.2f}</td>
                        </tr>
                        <tr>
                            <td>Average Accuracy</td>
                            <td class="{'positive' if results.get('overall_metrics', {}).get('avg_accuracy', 0) > 0.5 else 'negative'}">
                                {results.get('overall_metrics', {}).get('avg_accuracy', 0):.2%}
                            </td>
                            <td>-</td>
                            <td>-</td>
                        </tr>
                    </table>
                    
                    <h2>Best Performer</h2>
                    <table>
                        <tr>
                            <th>Symbol</th>
                            <th>Timeframe</th>
                            <th>Period</th>
                            <th>Return</th>
                            <th>Sharpe Ratio</th>
                            <th>Accuracy</th>
                        </tr>
                        <tr>
                            <td>{results.get('best_performers', {}).get('symbol', 'N/A')}</td>
                            <td>{results.get('best_performers', {}).get('timeframe', 'N/A')}</td>
                            <td>{results.get('best_performers', {}).get('period', 'N/A')}</td>
                            <td class="positive">{results.get('best_performers', {}).get('return', 0):.2%}</td>
                            <td class="positive">{results.get('best_performers', {}).get('sharpe', 0):.2f}</td>
                            <td class="positive">{results.get('best_performers', {}).get('accuracy', 0):.2%}</td>
                        </tr>
                    </table>
                    
                    <h2>Period Summaries</h2>
                    <table>
                        <tr>
                            <th>Period</th>
                            <th>Symbols Tested</th>
                            <th>Avg Return</th>
                            <th>Avg Sharpe</th>
                            <th>Avg Accuracy</th>
                            <th>Total Trades</th>
                        </tr>
        """
        
        # Add period summaries
        for period_name, period_data in results.get('period_summaries', {}).items():
            html_template += f"""
                        <tr>
                            <td>{period_name.title()}</td>
                            <td>{period_data.get('symbols_tested', 0)}</td>
                            <td class="{'positive' if period_data.get('avg_return', 0) > 0 else 'negative'}">
                                {period_data.get('avg_return', 0):.2%}
                            </td>
                            <td class="{'positive' if period_data.get('avg_sharpe', 0) > 0 else 'negative'}">
                                {period_data.get('avg_sharpe', 0):.2f}
                            </td>
                            <td class="{'positive' if period_data.get('avg_accuracy', 0) > 0.5 else 'negative'}">
                                {period_data.get('avg_accuracy', 0):.2%}
                            </td>
                            <td>{period_data.get('total_trades', 0)}</td>
                        </tr>
            """
        
        html_template += """
                    </table>
                </div>
                
                <div class="footer">
                    <p>Generated by BOLT AI Neural Agent System - Automated Backtesting</p>
                    <p>Report generated on """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC") + """</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def save_html_report(self, html_content: str):
        """Save HTML report to file"""
        html_file = self.reports_dir / f"backtest-report-{self.timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML report saved to: {html_file}")
    
    def generate_pdf_report(self, html_content: str):
        """Generate PDF report from HTML"""
        try:
            import weasyprint
            
            pdf_file = self.reports_dir / f"backtest-report-{self.timestamp}.pdf"
            weasyprint.HTML(string=html_content).write_pdf(pdf_file)
            print(f"PDF report saved to: {pdf_file}")
            
        except ImportError:
            print("WeasyPrint not available. Install with: pip install weasyprint")
        except Exception as e:
            print(f"Error generating PDF: {e}")
    
    def generate_csv_report(self, results: Dict):
        """Generate CSV report with detailed results"""
        # Flatten results for CSV
        csv_data = []
        
        for period_name, period_results in results.get('results', {}).items():
            for symbol, symbol_results in period_results.items():
                for timeframe, result in symbol_results.items():
                    csv_data.append({
                        'Period': period_name,
                        'Symbol': symbol,
                        'Timeframe': timeframe,
                        'Total Return': result['total_return'],
                        'Annualized Return': result['annualized_return'],
                        'Volatility': result['volatility'],
                        'Sharpe Ratio': result['sharpe_ratio'],
                        'Max Drawdown': result['max_drawdown'],
                        'Directional Accuracy': result['directional_accuracy'],
                        'Win Rate': result['win_rate'],
                        'Profit Factor': result['profit_factor'],
                        'Total Trades': result['total_trades'],
                        'Winning Trades': result['winning_trades'],
                        'Losing Trades': result['losing_trades'],
                        'Avg Confidence': result['avg_confidence'],
                        'Test Period Days': result['test_period_days'],
                        'Backtest Date': result['backtest_date']
                    })
        
        if csv_data:
            df = pd.DataFrame(csv_data)
            csv_file = self.reports_dir / f"backtest-results-{self.timestamp}.csv"
            df.to_csv(csv_file, index=False)
            print(f"CSV report saved to: {csv_file}")
    
    def generate_all_reports(self):
        """Generate all report formats"""
        try:
            # Load results
            results = self.load_results()
            
            # Generate HTML report
            html_content = self.generate_html_report(results)
            self.save_html_report(html_content)
            
            # Generate PDF report
            self.generate_pdf_report(html_content)
            
            # Generate CSV report
            self.generate_csv_report(results)
            
            print("All reports generated successfully!")
            
        except Exception as e:
            print(f"Error generating reports: {e}")
            raise


def main():
    """Main function"""
    generator = BacktestReportGenerator()
    generator.generate_all_reports()


if __name__ == "__main__":
    main()
