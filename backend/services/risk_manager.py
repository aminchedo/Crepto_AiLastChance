"""
Risk Management Service
Implements Kelly criterion, volatility gating, and dynamic position sizing
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class PositionSizingMethod(Enum):
    """Position sizing methods."""

    KELLY = "kelly"
    FIXED_FRACTION = "fixed_fraction"
    VOLATILITY_BASED = "volatility_based"
    RISK_PARITY = "risk_parity"
    ADAPTIVE = "adaptive"


@dataclass
class PositionSizingResult:
    """Result of position sizing calculation."""

    position_size: float
    method: PositionSizingMethod
    confidence: float
    risk_score: float
    volatility: float
    expected_return: float
    max_drawdown: float
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class RiskMetrics:
    """Risk metrics for portfolio."""

    var_95: float  # Value at Risk (95%)
    var_99: float  # Value at Risk (99%)
    cvar_95: float  # Conditional Value at Risk (95%)
    cvar_99: float  # Conditional Value at Risk (99%)
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    volatility: float
    beta: float
    alpha: float
    information_ratio: float


class KellyCriterionCalculator:
    """
    Kelly Criterion position sizing calculator.

    Features:
    - Kelly fraction calculation
    - Confidence interval estimation
    - Risk-adjusted Kelly
    - Multiple asset support
    """

    def __init__(
        self,
        max_fraction: float = 0.25,
        min_fraction: float = 0.01,
        confidence_factor: float = 0.5,
        risk_free_rate: float = 0.02,
    ):
        """
        Initialize Kelly criterion calculator.

        Args:
            max_fraction: Maximum position fraction
            min_fraction: Minimum position fraction
            confidence_factor: Factor to reduce Kelly fraction
            risk_free_rate: Risk-free rate for calculations
        """
        self.max_fraction = max_fraction
        self.min_fraction = min_fraction
        self.confidence_factor = confidence_factor
        self.risk_free_rate = risk_free_rate

        logger.info(
            f"KellyCriterionCalculator initialized: max_fraction={max_fraction}, "
            f"min_fraction={min_fraction}, confidence_factor={confidence_factor}"
        )

    def calculate_kelly_fraction(
        self, win_rate: float, avg_win: float, avg_loss: float, confidence: float = 1.0
    ) -> float:
        """
        Calculate Kelly fraction for single asset.

        Args:
            win_rate: Probability of winning
            avg_win: Average win amount
            avg_loss: Average loss amount
            confidence: Confidence in the estimate

        Returns:
            Kelly fraction
        """
        if win_rate <= 0 or win_rate >= 1:
            return 0.0

        if avg_loss <= 0:
            return 0.0

        # Kelly formula: f = (bp - q) / b
        # where b = avg_win/avg_loss, p = win_rate, q = 1 - win_rate
        b = avg_win / avg_loss
        p = win_rate
        q = 1 - win_rate

        kelly_fraction = (b * p - q) / b

        # Apply confidence factor
        kelly_fraction *= confidence * self.confidence_factor

        # Clamp to bounds
        kelly_fraction = max(min(kelly_fraction, self.max_fraction), self.min_fraction)

        return kelly_fraction

    def calculate_kelly_portfolio(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        confidence: float = 1.0,
    ) -> np.ndarray:
        """
        Calculate Kelly fractions for portfolio.

        Args:
            expected_returns: Expected returns for each asset
            covariance_matrix: Covariance matrix
            confidence: Confidence in the estimates

        Returns:
            Kelly fractions for each asset
        """
        try:
            # Kelly formula for portfolio: f = Σ^(-1) * μ
            # where Σ is covariance matrix, μ is expected returns
            inv_cov = np.linalg.inv(covariance_matrix)
            kelly_fractions = inv_cov @ expected_returns

            # Apply confidence factor
            kelly_fractions *= confidence * self.confidence_factor

            # Clamp to bounds
            kelly_fractions = np.clip(
                kelly_fractions, self.min_fraction, self.max_fraction
            )

            return kelly_fractions

        except np.linalg.LinAlgError:
            logger.warning("Covariance matrix is singular, using equal weights")
            n_assets = len(expected_returns)
            return np.full(n_assets, self.min_fraction)

    def calculate_risk_adjusted_kelly(
        self,
        expected_return: float,
        volatility: float,
        confidence: float = 1.0,
        risk_aversion: float = 2.0,
    ) -> float:
        """
        Calculate risk-adjusted Kelly fraction.

        Args:
            expected_return: Expected return
            volatility: Volatility
            confidence: Confidence in the estimate
            risk_aversion: Risk aversion parameter

        Returns:
            Risk-adjusted Kelly fraction
        """
        if volatility <= 0:
            return 0.0

        # Risk-adjusted Kelly: f = (μ - r) / (γ * σ²)
        # where μ is expected return, r is risk-free rate, γ is risk aversion, σ is volatility
        excess_return = expected_return - self.risk_free_rate
        risk_adjusted_fraction = excess_return / (risk_aversion * volatility**2)

        # Apply confidence factor
        risk_adjusted_fraction *= confidence * self.confidence_factor

        # Clamp to bounds
        risk_adjusted_fraction = max(
            min(risk_adjusted_fraction, self.max_fraction), self.min_fraction
        )

        return risk_adjusted_fraction


class VolatilityGating:
    """
    Volatility-based position sizing and gating.

    Features:
    - Dynamic volatility estimation
    - Volatility regime detection
    - Position size adjustment
    - Risk gate implementation
    """

    def __init__(
        self,
        volatility_window: int = 20,
        high_volatility_threshold: float = 2.0,
        low_volatility_threshold: float = 0.5,
        position_reduction_factor: float = 0.5,
        min_position_size: float = 0.01,
    ):
        """
        Initialize volatility gating.

        Args:
            volatility_window: Window for volatility calculation
            high_volatility_threshold: Threshold for high volatility
            low_volatility_threshold: Threshold for low volatility
            position_reduction_factor: Factor to reduce position size
            min_position_size: Minimum position size
        """
        self.volatility_window = volatility_window
        self.high_volatility_threshold = high_volatility_threshold
        self.low_volatility_threshold = low_volatility_threshold
        self.position_reduction_factor = position_reduction_factor
        self.min_position_size = min_position_size

        # State tracking
        self.volatility_history = {}
        self.regime_history = {}

        logger.info(
            f"VolatilityGating initialized: window={volatility_window}, "
            f"high_threshold={high_volatility_threshold}, low_threshold={low_volatility_threshold}"
        )

    def calculate_volatility(
        self, returns: np.ndarray, method: str = "standard"
    ) -> float:
        """
        Calculate volatility from returns.

        Args:
            returns: Return series
            method: Calculation method ("standard", "ewm", "garch")

        Returns:
            Volatility estimate
        """
        if len(returns) < 2:
            return 0.0

        if method == "standard":
            return np.std(returns)
        elif method == "ewm":
            # Exponential weighted moving average
            alpha = 2.0 / (self.volatility_window + 1)
            ewm_var = 0.0
            for i, ret in enumerate(returns):
                ewm_var = alpha * ret**2 + (1 - alpha) * ewm_var
            return np.sqrt(ewm_var)
        elif method == "garch":
            # Simplified GARCH(1,1) model
            if len(returns) < 10:
                return np.std(returns)

            # GARCH parameters (simplified)
            omega = 0.0001
            alpha = 0.1
            beta = 0.85

            # Initialize
            var = np.var(returns)
            for ret in returns:
                var = omega + alpha * ret**2 + beta * var

            return np.sqrt(var)
        else:
            raise ValueError(f"Unknown volatility method: {method}")

    def detect_volatility_regime(self, symbol: str, current_volatility: float) -> str:
        """
        Detect volatility regime.

        Args:
            symbol: Trading symbol
            current_volatility: Current volatility

        Returns:
            Volatility regime ("low", "normal", "high")
        """
        if current_volatility < self.low_volatility_threshold:
            regime = "low"
        elif current_volatility > self.high_volatility_threshold:
            regime = "high"
        else:
            regime = "normal"

        # Update regime history
        if symbol not in self.regime_history:
            self.regime_history[symbol] = []

        self.regime_history[symbol].append(regime)

        # Keep only recent history
        if len(self.regime_history[symbol]) > 100:
            self.regime_history[symbol] = self.regime_history[symbol][-100:]

        return regime

    def adjust_position_size(
        self,
        base_position_size: float,
        volatility: float,
        regime: str,
        confidence: float = 1.0,
    ) -> float:
        """
        Adjust position size based on volatility.

        Args:
            base_position_size: Base position size
            volatility: Current volatility
            regime: Volatility regime
            confidence: Confidence in the prediction

        Returns:
            Adjusted position size
        """
        adjusted_size = base_position_size

        # Adjust based on regime
        if regime == "high":
            # Reduce position size in high volatility
            adjusted_size *= self.position_reduction_factor
        elif regime == "low":
            # Increase position size in low volatility (with caution)
            adjusted_size *= min(
                1.5, 1.0 + (self.low_volatility_threshold - volatility)
            )

        # Adjust based on confidence
        adjusted_size *= confidence

        # Ensure minimum position size
        adjusted_size = max(adjusted_size, self.min_position_size)

        return adjusted_size

    def should_gate_trade(
        self,
        volatility: float,
        confidence: float,
        min_confidence_threshold: float = 0.6,
    ) -> bool:
        """
        Determine if trade should be gated.

        Args:
            volatility: Current volatility
            confidence: Prediction confidence
            min_confidence_threshold: Minimum confidence threshold

        Returns:
            True if trade should be gated
        """
        # Gate if volatility is too high
        if volatility > self.high_volatility_threshold * 2:
            return True

        # Gate if confidence is too low
        if confidence < min_confidence_threshold:
            return True

        return False


class RiskManager:
    """
    Comprehensive risk management system.

    Features:
    - Multiple position sizing methods
    - Risk metrics calculation
    - Drawdown monitoring
    - Portfolio risk assessment
    - Dynamic risk adjustment
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        max_position_size: float = 0.25,
        min_position_size: float = 0.01,
        max_drawdown_limit: float = 0.20,
        risk_free_rate: float = 0.02,
    ):
        """
        Initialize risk manager.

        Args:
            initial_capital: Initial capital
            max_position_size: Maximum position size
            min_position_size: Minimum position size
            max_drawdown_limit: Maximum drawdown limit
            risk_free_rate: Risk-free rate
        """
        self.initial_capital = initial_capital
        self.max_position_size = max_position_size
        self.min_position_size = min_position_size
        self.max_drawdown_limit = max_drawdown_limit
        self.risk_free_rate = risk_free_rate

        # Components
        self.kelly_calculator = KellyCriterionCalculator(
            max_fraction=max_position_size,
            min_fraction=min_position_size,
            risk_free_rate=risk_free_rate,
        )

        self.volatility_gating = VolatilityGating(min_position_size=min_position_size)

        # State tracking
        self.current_capital = initial_capital
        self.peak_capital = initial_capital
        self.positions = {}
        self.returns_history = []
        self.drawdown_history = []

        # Statistics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0

        logger.info(
            f"RiskManager initialized: capital={initial_capital}, "
            f"max_position={max_position_size}, max_drawdown={max_drawdown_limit}"
        )

    def calculate_position_size(
        self,
        symbol: str,
        expected_return: float,
        volatility: float,
        confidence: float,
        method: PositionSizingMethod = PositionSizingMethod.KELLY,
        win_rate: Optional[float] = None,
        avg_win: Optional[float] = None,
        avg_loss: Optional[float] = None,
    ) -> PositionSizingResult:
        """
        Calculate position size using specified method.

        Args:
            symbol: Trading symbol
            expected_return: Expected return
            volatility: Volatility
            confidence: Prediction confidence
            method: Position sizing method
            win_rate: Win rate (for Kelly)
            avg_win: Average win (for Kelly)
            avg_loss: Average loss (for Kelly)

        Returns:
            Position sizing result
        """
        # Detect volatility regime
        regime = self.volatility_gating.detect_volatility_regime(symbol, volatility)

        # Check if trade should be gated
        if self.volatility_gating.should_gate_trade(volatility, confidence):
            return PositionSizingResult(
                position_size=0.0,
                method=method,
                confidence=confidence,
                risk_score=1.0,
                volatility=volatility,
                expected_return=expected_return,
                max_drawdown=0.0,
                metadata={"gated": True, "reason": "volatility_or_confidence"},
                timestamp=datetime.now(),
            )

        # Calculate base position size
        if method == PositionSizingMethod.KELLY:
            if win_rate is not None and avg_win is not None and avg_loss is not None:
                base_size = self.kelly_calculator.calculate_kelly_fraction(
                    win_rate, avg_win, avg_loss, confidence
                )
            else:
                base_size = self.kelly_calculator.calculate_risk_adjusted_kelly(
                    expected_return, volatility, confidence
                )

        elif method == PositionSizingMethod.FIXED_FRACTION:
            base_size = self.max_position_size * confidence

        elif method == PositionSizingMethod.VOLATILITY_BASED:
            # Volatility-based sizing: size inversely proportional to volatility
            base_size = min(self.max_position_size, 0.1 / volatility) * confidence

        elif method == PositionSizingMethod.RISK_PARITY:
            # Risk parity: equal risk contribution
            base_size = self.max_position_size / volatility * confidence

        else:
            base_size = self.min_position_size

        # Adjust for volatility regime
        adjusted_size = self.volatility_gating.adjust_position_size(
            base_size, volatility, regime, confidence
        )

        # Calculate risk metrics
        risk_score = self._calculate_risk_score(volatility, confidence)
        max_drawdown = self._calculate_max_drawdown()

        # Create result
        result = PositionSizingResult(
            position_size=adjusted_size,
            method=method,
            confidence=confidence,
            risk_score=risk_score,
            volatility=volatility,
            expected_return=expected_return,
            max_drawdown=max_drawdown,
            metadata={
                "regime": regime,
                "base_size": base_size,
                "adjusted_size": adjusted_size,
                "gated": False,
            },
            timestamp=datetime.now(),
        )

        return result

    def _calculate_risk_score(self, volatility: float, confidence: float) -> float:
        """Calculate overall risk score."""
        # Risk score based on volatility and confidence
        volatility_risk = min(volatility / 2.0, 1.0)  # Normalize volatility
        confidence_risk = 1.0 - confidence

        # Combined risk score
        risk_score = (volatility_risk + confidence_risk) / 2.0

        return min(risk_score, 1.0)

    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown."""
        if not self.drawdown_history:
            return 0.0

        return max(self.drawdown_history)

    def update_position(
        self,
        symbol: str,
        position_size: float,
        entry_price: float,
        current_price: float,
    ) -> Dict[str, float]:
        """
        Update position and calculate P&L.

        Args:
            symbol: Trading symbol
            position_size: Position size
            entry_price: Entry price
            current_price: Current price

        Returns:
            Position update information
        """
        # Calculate P&L
        pnl = position_size * (current_price - entry_price)

        # Update position
        self.positions[symbol] = {
            "size": position_size,
            "entry_price": entry_price,
            "current_price": current_price,
            "pnl": pnl,
            "timestamp": datetime.now(),
        }

        # Update capital
        self.current_capital += pnl
        self.total_pnl += pnl

        # Update peak capital
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital

        # Calculate drawdown
        drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
        self.drawdown_history.append(drawdown)

        # Update returns
        if len(self.returns_history) > 0:
            period_return = (
                self.current_capital - self.returns_history[-1]
            ) / self.returns_history[-1]
            self.returns_history.append(self.current_capital)
        else:
            self.returns_history.append(self.current_capital)

        # Update trade statistics
        self.total_trades += 1
        if pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1

        return {
            "pnl": pnl,
            "current_capital": self.current_capital,
            "drawdown": drawdown,
            "total_pnl": self.total_pnl,
        }

    def calculate_risk_metrics(self) -> RiskMetrics:
        """Calculate comprehensive risk metrics."""
        if len(self.returns_history) < 2:
            return RiskMetrics(
                var_95=0.0,
                var_99=0.0,
                cvar_95=0.0,
                cvar_99=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0,
                sortino_ratio=0.0,
                calmar_ratio=0.0,
                volatility=0.0,
                beta=0.0,
                alpha=0.0,
                information_ratio=0.0,
            )

        # Calculate returns
        returns = np.diff(self.returns_history) / self.returns_history[:-1]

        # VaR and CVaR
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        cvar_95 = np.mean(returns[returns <= var_95])
        cvar_99 = np.mean(returns[returns <= var_99])

        # Drawdown
        max_drawdown = max(self.drawdown_history) if self.drawdown_history else 0.0

        # Sharpe ratio
        excess_returns = returns - self.risk_free_rate / 252  # Daily risk-free rate
        sharpe_ratio = np.mean(excess_returns) / np.std(returns) * np.sqrt(252)

        # Sortino ratio
        downside_returns = returns[returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0.0
        sortino_ratio = (
            np.mean(excess_returns) / downside_std * np.sqrt(252)
            if downside_std > 0
            else 0.0
        )

        # Calmar ratio
        annual_return = (self.current_capital / self.initial_capital) ** (
            252 / len(returns)
        ) - 1
        calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0.0

        # Volatility
        volatility = np.std(returns) * np.sqrt(252)

        # Beta and Alpha (simplified)
        beta = 1.0  # Placeholder
        alpha = 0.0  # Placeholder

        # Information ratio
        information_ratio = 0.0  # Placeholder

        return RiskMetrics(
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            cvar_99=cvar_99,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            volatility=volatility,
            beta=beta,
            alpha=alpha,
            information_ratio=information_ratio,
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get risk manager statistics."""
        risk_metrics = self.calculate_risk_metrics()

        return {
            "initial_capital": self.initial_capital,
            "current_capital": self.current_capital,
            "total_pnl": self.total_pnl,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.winning_trades / max(self.total_trades, 1),
            "max_drawdown": risk_metrics.max_drawdown,
            "sharpe_ratio": risk_metrics.sharpe_ratio,
            "volatility": risk_metrics.volatility,
            "positions": len(self.positions),
            "returns_history_length": len(self.returns_history),
        }
