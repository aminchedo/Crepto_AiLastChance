"""
Comprehensive Metrics Suite
MSE, MAE, R², Brier, ECE, precision/recall, Sharpe ratio and more
"""

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, f1_score, mean_absolute_error,
                             mean_squared_error, precision_score, r2_score,
                             recall_score)

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric types."""

    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    CALIBRATION = "calibration"
    FINANCIAL = "financial"
    CUSTOM = "custom"


@dataclass
class MetricResult:
    """Metric calculation result."""

    name: str
    value: float
    metric_type: MetricType
    metadata: Dict[str, Any] = None
    timestamp: str = None


class RegressionMetrics:
    """
    Regression metrics for continuous predictions.
    """

    @staticmethod
    def mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Mean Squared Error."""
        return mean_squared_error(y_true, y_pred)

    @staticmethod
    def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Root Mean Squared Error."""
        return math.sqrt(mean_squared_error(y_true, y_pred))

    @staticmethod
    def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Mean Absolute Error."""
        return mean_absolute_error(y_true, y_pred)

    @staticmethod
    def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """R-squared (coefficient of determination)."""
        return r2_score(y_true, y_pred)

    @staticmethod
    def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Mean Absolute Percentage Error."""
        return np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100

    @staticmethod
    def smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Symmetric Mean Absolute Percentage Error."""
        return (
            np.mean(
                2 * np.abs(y_true - y_pred) / (np.abs(y_true) + np.abs(y_pred) + 1e-8)
            )
            * 100
        )

    @staticmethod
    def directional_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Directional accuracy (percentage of correct direction predictions)."""
        if len(y_true) < 2:
            return 0.0

        true_direction = np.diff(y_true) > 0
        pred_direction = np.diff(y_pred) > 0

        return np.mean(true_direction == pred_direction) * 100

    @staticmethod
    def theil_u(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Theil's U statistic (relative to naive forecast)."""
        if len(y_true) < 2:
            return 0.0

        naive_pred = np.roll(y_true, 1)
        naive_pred[0] = y_true[0]

        mse_pred = np.mean((y_true - y_pred) ** 2)
        mse_naive = np.mean((y_true - naive_pred) ** 2)

        return math.sqrt(mse_pred / (mse_naive + 1e-8))


class ClassificationMetrics:
    """
    Classification metrics for categorical predictions.
    """

    @staticmethod
    def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Accuracy score."""
        return accuracy_score(y_true, y_pred)

    @staticmethod
    def precision(
        y_true: np.ndarray, y_pred: np.ndarray, average: str = "weighted"
    ) -> float:
        """Precision score."""
        return precision_score(y_true, y_pred, average=average, zero_division=0)

    @staticmethod
    def recall(
        y_true: np.ndarray, y_pred: np.ndarray, average: str = "weighted"
    ) -> float:
        """Recall score."""
        return recall_score(y_true, y_pred, average=average, zero_division=0)

    @staticmethod
    def f1_score(
        y_true: np.ndarray, y_pred: np.ndarray, average: str = "weighted"
    ) -> float:
        """F1 score."""
        return f1_score(y_true, y_pred, average=average, zero_division=0)

    @staticmethod
    def confusion_matrix_metrics(
        y_true: np.ndarray, y_pred: np.ndarray
    ) -> Dict[str, Any]:
        """Detailed confusion matrix metrics."""
        cm = confusion_matrix(y_true, y_pred)

        # Calculate metrics for each class
        metrics = {}
        for i in range(cm.shape[0]):
            tp = cm[i, i]
            fp = cm.sum(axis=0)[i] - tp
            fn = cm.sum(axis=1)[i] - tp
            tn = cm.sum() - tp - fp - fn

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = (
                2 * precision * recall / (precision + recall)
                if (precision + recall) > 0
                else 0
            )

            metrics[f"class_{i}"] = {
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "support": tp + fn,
            }

        return metrics

    @staticmethod
    def classification_report_dict(
        y_true: np.ndarray, y_pred: np.ndarray
    ) -> Dict[str, Any]:
        """Classification report as dictionary."""
        return classification_report(y_true, y_pred, output_dict=True, zero_division=0)


class CalibrationMetrics:
    """
    Calibration metrics for probability predictions.
    """

    @staticmethod
    def brier_score(y_true: np.ndarray, y_prob: np.ndarray) -> float:
        """Brier score for probability calibration."""
        return np.mean((y_true - y_prob) ** 2)

    @staticmethod
    def expected_calibration_error(
        self, y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
    ) -> float:
        """Expected Calibration Error (ECE)."""
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]

        ece = 0
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            in_bin = (y_prob > bin_lower) & (y_prob <= bin_upper)
            prop_in_bin = in_bin.mean()

            if prop_in_bin > 0:
                accuracy_in_bin = y_true[in_bin].mean()
                avg_confidence_in_bin = y_prob[in_bin].mean()
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

        return ece

    @staticmethod
    def reliability_diagram(
        y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
    ) -> Dict[str, np.ndarray]:
        """Reliability diagram data."""
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]

        bin_centers = []
        bin_accuracies = []
        bin_confidences = []
        bin_counts = []

        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            in_bin = (y_prob > bin_lower) & (y_prob <= bin_upper)
            prop_in_bin = in_bin.sum()

            if prop_in_bin > 0:
                bin_centers.append((bin_lower + bin_upper) / 2)
                bin_accuracies.append(y_true[in_bin].mean())
                bin_confidences.append(y_prob[in_bin].mean())
                bin_counts.append(prop_in_bin)
            else:
                bin_centers.append((bin_lower + bin_upper) / 2)
                bin_accuracies.append(0)
                bin_confidences.append((bin_lower + bin_upper) / 2)
                bin_counts.append(0)

        return {
            "bin_centers": np.array(bin_centers),
            "bin_accuracies": np.array(bin_accuracies),
            "bin_confidences": np.array(bin_confidences),
            "bin_counts": np.array(bin_counts),
        }

    @staticmethod
    def log_loss(y_true: np.ndarray, y_prob: np.ndarray) -> float:
        """Log loss (cross-entropy) for probability predictions."""
        # Clip probabilities to avoid log(0)
        y_prob = np.clip(y_prob, 1e-15, 1 - 1e-15)
        return -np.mean(y_true * np.log(y_prob) + (1 - y_true) * np.log(1 - y_prob))


class FinancialMetrics:
    """
    Financial performance metrics for trading strategies.
    """

    @staticmethod
    def sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.0) -> float:
        """Sharpe ratio."""
        if len(returns) == 0 or np.std(returns) == 0:
            return 0.0

        excess_returns = returns - risk_free_rate
        return np.mean(excess_returns) / np.std(returns) * np.sqrt(252)  # Annualized

    @staticmethod
    def sortino_ratio(returns: np.ndarray, risk_free_rate: float = 0.0) -> float:
        """Sortino ratio (downside deviation)."""
        if len(returns) == 0:
            return 0.0

        excess_returns = returns - risk_free_rate
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0:
            return np.inf if np.mean(excess_returns) > 0 else 0.0

        downside_std = np.std(downside_returns)
        if downside_std == 0:
            return 0.0

        return np.mean(excess_returns) / downside_std * np.sqrt(252)  # Annualized

    @staticmethod
    def calmar_ratio(returns: np.ndarray) -> float:
        """Calmar ratio (annual return / max drawdown)."""
        if len(returns) == 0:
            return 0.0

        annual_return = np.mean(returns) * 252
        max_drawdown = FinancialMetrics.max_drawdown(returns)

        if max_drawdown == 0:
            return np.inf if annual_return > 0 else 0.0

        return annual_return / abs(max_drawdown)

    @staticmethod
    def max_drawdown(returns: np.ndarray) -> float:
        """Maximum drawdown."""
        if len(returns) == 0:
            return 0.0

        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max

        return np.min(drawdown)

    @staticmethod
    def max_drawdown_duration(returns: np.ndarray) -> int:
        """Maximum drawdown duration in periods."""
        if len(returns) == 0:
            return 0

        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max

        in_drawdown = drawdown < 0
        drawdown_periods = []
        current_period = 0

        for is_dd in in_drawdown:
            if is_dd:
                current_period += 1
            else:
                if current_period > 0:
                    drawdown_periods.append(current_period)
                current_period = 0

        if current_period > 0:
            drawdown_periods.append(current_period)

        return max(drawdown_periods) if drawdown_periods else 0

    @staticmethod
    def var(returns: np.ndarray, confidence_level: float = 0.05) -> float:
        """Value at Risk (VaR)."""
        if len(returns) == 0:
            return 0.0

        return np.percentile(returns, confidence_level * 100)

    @staticmethod
    def cvar(returns: np.ndarray, confidence_level: float = 0.05) -> float:
        """Conditional Value at Risk (CVaR) / Expected Shortfall."""
        if len(returns) == 0:
            return 0.0

        var = FinancialMetrics.var(returns, confidence_level)
        return np.mean(returns[returns <= var])

    @staticmethod
    def profit_factor(returns: np.ndarray) -> float:
        """Profit factor (gross profit / gross loss)."""
        if len(returns) == 0:
            return 0.0

        gross_profit = np.sum(returns[returns > 0])
        gross_loss = abs(np.sum(returns[returns < 0]))

        if gross_loss == 0:
            return np.inf if gross_profit > 0 else 0.0

        return gross_profit / gross_loss

    @staticmethod
    def win_rate(returns: np.ndarray) -> float:
        """Win rate (percentage of profitable trades)."""
        if len(returns) == 0:
            return 0.0

        return np.mean(returns > 0) * 100

    @staticmethod
    def average_win(returns: np.ndarray) -> float:
        """Average winning trade."""
        winning_trades = returns[returns > 0]
        return np.mean(winning_trades) if len(winning_trades) > 0 else 0.0

    @staticmethod
    def average_loss(returns: np.ndarray) -> float:
        """Average losing trade."""
        losing_trades = returns[returns < 0]
        return np.mean(losing_trades) if len(losing_trades) > 0 else 0.0

    @staticmethod
    def expectancy(returns: np.ndarray) -> float:
        """Expectancy (expected value per trade)."""
        if len(returns) == 0:
            return 0.0

        win_rate = FinancialMetrics.win_rate(returns) / 100
        avg_win = FinancialMetrics.average_win(returns)
        avg_loss = FinancialMetrics.average_loss(returns)

        return win_rate * avg_win + (1 - win_rate) * avg_loss


class MetricsCalculator:
    """
    Comprehensive metrics calculator for all types of predictions.
    """

    def __init__(self):
        """Initialize metrics calculator."""
        self.regression_metrics = RegressionMetrics()
        self.classification_metrics = ClassificationMetrics()
        self.calibration_metrics = CalibrationMetrics()
        self.financial_metrics = FinancialMetrics()

        logger.info("MetricsCalculator initialized")

    def calculate_regression_metrics(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ) -> Dict[str, MetricResult]:
        """Calculate regression metrics."""
        metrics = {}

        metrics["mse"] = MetricResult(
            name="MSE",
            value=self.regression_metrics.mse(y_true, y_pred),
            metric_type=MetricType.REGRESSION,
        )

        metrics["rmse"] = MetricResult(
            name="RMSE",
            value=self.regression_metrics.rmse(y_true, y_pred),
            metric_type=MetricType.REGRESSION,
        )

        metrics["mae"] = MetricResult(
            name="MAE",
            value=self.regression_metrics.mae(y_true, y_pred),
            metric_type=MetricType.REGRESSION,
        )

        metrics["r2_score"] = MetricResult(
            name="R²",
            value=self.regression_metrics.r2_score(y_true, y_pred),
            metric_type=MetricType.REGRESSION,
        )

        metrics["mape"] = MetricResult(
            name="MAPE",
            value=self.regression_metrics.mape(y_true, y_pred),
            metric_type=MetricType.REGRESSION,
        )

        metrics["smape"] = MetricResult(
            name="SMAPE",
            value=self.regression_metrics.smape(y_true, y_pred),
            metric_type=MetricType.REGRESSION,
        )

        metrics["directional_accuracy"] = MetricResult(
            name="Directional Accuracy",
            value=self.regression_metrics.directional_accuracy(y_true, y_pred),
            metric_type=MetricType.REGRESSION,
        )

        metrics["theil_u"] = MetricResult(
            name="Theil's U",
            value=self.regression_metrics.theil_u(y_true, y_pred),
            metric_type=MetricType.REGRESSION,
        )

        return metrics

    def calculate_classification_metrics(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ) -> Dict[str, MetricResult]:
        """Calculate classification metrics."""
        metrics = {}

        metrics["accuracy"] = MetricResult(
            name="Accuracy",
            value=self.classification_metrics.accuracy(y_true, y_pred),
            metric_type=MetricType.CLASSIFICATION,
        )

        metrics["precision"] = MetricResult(
            name="Precision",
            value=self.classification_metrics.precision(y_true, y_pred),
            metric_type=MetricType.CLASSIFICATION,
        )

        metrics["recall"] = MetricResult(
            name="Recall",
            value=self.classification_metrics.recall(y_true, y_pred),
            metric_type=MetricType.CLASSIFICATION,
        )

        metrics["f1_score"] = MetricResult(
            name="F1 Score",
            value=self.classification_metrics.f1_score(y_true, y_pred),
            metric_type=MetricType.CLASSIFICATION,
        )

        # Detailed confusion matrix metrics
        cm_metrics = self.classification_metrics.confusion_matrix_metrics(
            y_true, y_pred
        )
        metrics["confusion_matrix"] = MetricResult(
            name="Confusion Matrix",
            value=0.0,  # Placeholder
            metric_type=MetricType.CLASSIFICATION,
            metadata=cm_metrics,
        )

        return metrics

    def calculate_calibration_metrics(
        self, y_true: np.ndarray, y_prob: np.ndarray
    ) -> Dict[str, MetricResult]:
        """Calculate calibration metrics."""
        metrics = {}

        metrics["brier_score"] = MetricResult(
            name="Brier Score",
            value=self.calibration_metrics.brier_score(y_true, y_prob),
            metric_type=MetricType.CALIBRATION,
        )

        metrics["ece"] = MetricResult(
            name="Expected Calibration Error",
            value=self.calibration_metrics.expected_calibration_error(y_true, y_prob),
            metric_type=MetricType.CALIBRATION,
        )

        metrics["log_loss"] = MetricResult(
            name="Log Loss",
            value=self.calibration_metrics.log_loss(y_true, y_prob),
            metric_type=MetricType.CALIBRATION,
        )

        # Reliability diagram data
        reliability_data = self.calibration_metrics.reliability_diagram(y_true, y_prob)
        metrics["reliability_diagram"] = MetricResult(
            name="Reliability Diagram",
            value=0.0,  # Placeholder
            metric_type=MetricType.CALIBRATION,
            metadata=reliability_data,
        )

        return metrics

    def calculate_financial_metrics(
        self, returns: np.ndarray, risk_free_rate: float = 0.0
    ) -> Dict[str, MetricResult]:
        """Calculate financial metrics."""
        metrics = {}

        metrics["sharpe_ratio"] = MetricResult(
            name="Sharpe Ratio",
            value=self.financial_metrics.sharpe_ratio(returns, risk_free_rate),
            metric_type=MetricType.FINANCIAL,
        )

        metrics["sortino_ratio"] = MetricResult(
            name="Sortino Ratio",
            value=self.financial_metrics.sortino_ratio(returns, risk_free_rate),
            metric_type=MetricType.FINANCIAL,
        )

        metrics["calmar_ratio"] = MetricResult(
            name="Calmar Ratio",
            value=self.financial_metrics.calmar_ratio(returns),
            metric_type=MetricType.FINANCIAL,
        )

        metrics["max_drawdown"] = MetricResult(
            name="Max Drawdown",
            value=self.financial_metrics.max_drawdown(returns),
            metric_type=MetricType.FINANCIAL,
        )

        metrics["max_drawdown_duration"] = MetricResult(
            name="Max Drawdown Duration",
            value=self.financial_metrics.max_drawdown_duration(returns),
            metric_type=MetricType.FINANCIAL,
        )

        metrics["var_5"] = MetricResult(
            name="VaR (5%)",
            value=self.financial_metrics.var(returns, 0.05),
            metric_type=MetricType.FINANCIAL,
        )

        metrics["cvar_5"] = MetricResult(
            name="CVaR (5%)",
            value=self.financial_metrics.cvar(returns, 0.05),
            metric_type=MetricType.FINANCIAL,
        )

        metrics["profit_factor"] = MetricResult(
            name="Profit Factor",
            value=self.financial_metrics.profit_factor(returns),
            metric_type=MetricType.FINANCIAL,
        )

        metrics["win_rate"] = MetricResult(
            name="Win Rate",
            value=self.financial_metrics.win_rate(returns),
            metric_type=MetricType.FINANCIAL,
        )

        metrics["expectancy"] = MetricResult(
            name="Expectancy",
            value=self.financial_metrics.expectancy(returns),
            metric_type=MetricType.FINANCIAL,
        )

        return metrics

    def calculate_all_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: Optional[np.ndarray] = None,
        returns: Optional[np.ndarray] = None,
        risk_free_rate: float = 0.0,
    ) -> Dict[str, Dict[str, MetricResult]]:
        """
        Calculate all applicable metrics.

        Args:
            y_true: True values
            y_pred: Predicted values
            y_prob: Predicted probabilities (for calibration)
            returns: Returns for financial metrics
            risk_free_rate: Risk-free rate

        Returns:
            Dictionary of metric categories
        """
        all_metrics = {}

        # Regression metrics
        all_metrics["regression"] = self.calculate_regression_metrics(y_true, y_pred)

        # Classification metrics (if predictions are categorical)
        if len(np.unique(y_pred)) < len(y_pred) * 0.1:  # Heuristic for categorical
            all_metrics["classification"] = self.calculate_classification_metrics(
                y_true, y_pred
            )

        # Calibration metrics (if probabilities provided)
        if y_prob is not None:
            all_metrics["calibration"] = self.calculate_calibration_metrics(
                y_true, y_prob
            )

        # Financial metrics (if returns provided)
        if returns is not None:
            all_metrics["financial"] = self.calculate_financial_metrics(
                returns, risk_free_rate
            )

        return all_metrics

    def get_metric_summary(
        self, metrics: Dict[str, Dict[str, MetricResult]]
    ) -> pd.DataFrame:
        """
        Get metrics summary as DataFrame.

        Args:
            metrics: Metrics dictionary

        Returns:
            DataFrame with metrics summary
        """
        rows = []

        for category, category_metrics in metrics.items():
            for metric_name, metric_result in category_metrics.items():
                rows.append(
                    {
                        "Category": category,
                        "Metric": metric_result.name,
                        "Value": metric_result.value,
                        "Type": metric_result.metric_type.value,
                    }
                )

        return pd.DataFrame(rows)

    def compare_models(
        self, model_results: Dict[str, Dict[str, np.ndarray]]
    ) -> pd.DataFrame:
        """
        Compare multiple models using metrics.

        Args:
            model_results: Dictionary of {model_name: {y_true, y_pred, y_prob, returns}}

        Returns:
            DataFrame with model comparison
        """
        comparison_data = []

        for model_name, results in model_results.items():
            y_true = results["y_true"]
            y_pred = results["y_pred"]
            y_prob = results.get("y_prob")
            returns = results.get("returns")

            metrics = self.calculate_all_metrics(y_true, y_pred, y_prob, returns)

            for category, category_metrics in metrics.items():
                for metric_name, metric_result in category_metrics.items():
                    comparison_data.append(
                        {
                            "Model": model_name,
                            "Category": category,
                            "Metric": metric_result.name,
                            "Value": metric_result.value,
                        }
                    )

        return pd.DataFrame(comparison_data)
