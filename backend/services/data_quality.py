"""
Data Quality Pipeline
Gap filling, outlier detection, normalization, and data validation
"""

import logging
import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import pytz
from scipy import stats
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

logger = logging.getLogger(__name__)


class DataQualityIssue(Enum):
    """Types of data quality issues."""

    MISSING_DATA = "missing_data"
    OUTLIER = "outlier"
    DUPLICATE = "duplicate"
    INVALID_VALUE = "invalid_value"
    TIMESTAMP_GAP = "timestamp_gap"
    TIMEZONE_INCONSISTENCY = "timezone_inconsistency"
    SYMBOL_MISMATCH = "symbol_mismatch"
    VOLUME_ANOMALY = "volume_anomaly"
    PRICE_SPIKE = "price_spike"


@dataclass
class QualityIssue:
    """Data quality issue record."""

    issue_type: DataQualityIssue
    timestamp: datetime
    symbol: str
    field: str
    value: Any
    expected_value: Optional[Any] = None
    severity: str = "medium"  # low, medium, high, critical
    description: str = ""
    fixed: bool = False


@dataclass
class DataQualityReport:
    """Data quality assessment report."""

    total_records: int
    valid_records: int
    issues: List[QualityIssue]
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    overall_score: float
    recommendations: List[str]


class GapFiller:
    """
    Gap filling algorithms for missing data.
    """

    def __init__(self):
        """Initialize gap filler."""
        self.methods = {
            "forward_fill": self._forward_fill,
            "backward_fill": self._backward_fill,
            "linear_interpolation": self._linear_interpolation,
            "cubic_spline": self._cubic_spline,
            "knn_imputation": self._knn_imputation,
            "seasonal_decomposition": self._seasonal_decomposition,
            "market_hours_aware": self._market_hours_aware_fill,
        }

        logger.info(
            "GapFiller initialized with methods: " + ", ".join(self.methods.keys())
        )

    def fill_gaps(
        self,
        data: pd.DataFrame,
        method: str = "linear_interpolation",
        max_gap_size: int = 10,
        **kwargs,
    ) -> Tuple[pd.DataFrame, List[QualityIssue]]:
        """
        Fill gaps in time series data.

        Args:
            data: DataFrame with timestamp index
            method: Gap filling method
            max_gap_size: Maximum gap size to fill
            **kwargs: Method-specific parameters

        Returns:
            Tuple of (filled_data, issues_found)
        """
        if method not in self.methods:
            raise ValueError(f"Unknown method: {method}")

        issues = []
        filled_data = data.copy()

        # Detect gaps
        gaps = self._detect_gaps(data)

        for gap_start, gap_end, gap_size in gaps:
            if gap_size <= max_gap_size:
                try:
                    filled_section = self.methods[method](
                        data, gap_start, gap_end, **kwargs
                    )
                    filled_data.loc[gap_start:gap_end] = filled_section

                    issues.append(
                        QualityIssue(
                            issue_type=DataQualityIssue.MISSING_DATA,
                            timestamp=gap_start,
                            symbol=kwargs.get("symbol", "unknown"),
                            field="multiple",
                            value=f"Gap of {gap_size} records",
                            severity="medium",
                            description=f"Filled gap using {method}",
                            fixed=True,
                        )
                    )

                except Exception as e:
                    logger.error(f"Failed to fill gap at {gap_start}: {e}")
                    issues.append(
                        QualityIssue(
                            issue_type=DataQualityIssue.MISSING_DATA,
                            timestamp=gap_start,
                            symbol=kwargs.get("symbol", "unknown"),
                            field="multiple",
                            value=f"Gap of {gap_size} records",
                            severity="high",
                            description=f"Failed to fill gap: {e}",
                            fixed=False,
                        )
                    )
            else:
                issues.append(
                    QualityIssue(
                        issue_type=DataQualityIssue.MISSING_DATA,
                        timestamp=gap_start,
                        symbol=kwargs.get("symbol", "unknown"),
                        field="multiple",
                        value=f"Gap of {gap_size} records",
                        severity="critical",
                        description=f"Gap too large to fill (max: {max_gap_size})",
                        fixed=False,
                    )
                )

        return filled_data, issues

    def _detect_gaps(self, data: pd.DataFrame) -> List[Tuple[datetime, datetime, int]]:
        """Detect gaps in time series data."""
        gaps = []

        if len(data) < 2:
            return gaps

        # Expected frequency (infer from first few intervals)
        time_diffs = pd.Series(data.index).diff().dropna()
        expected_freq = (
            time_diffs.mode().iloc[0]
            if len(time_diffs) > 0
            else pd.Timedelta(minutes=1)
        )

        # Find gaps larger than expected frequency
        for i in range(1, len(data)):
            current_diff = data.index[i] - data.index[i - 1]
            if current_diff > expected_freq * 1.5:  # Allow 50% tolerance
                gap_size = int(current_diff / expected_freq) - 1
                gaps.append((data.index[i - 1], data.index[i], gap_size))

        return gaps

    def _forward_fill(
        self, data: pd.DataFrame, start: datetime, end: datetime, **kwargs
    ) -> pd.DataFrame:
        """Forward fill method."""
        return data.fillna(method="ffill")

    def _backward_fill(
        self, data: pd.DataFrame, start: datetime, end: datetime, **kwargs
    ) -> pd.DataFrame:
        """Backward fill method."""
        return data.fillna(method="bfill")

    def _linear_interpolation(
        self, data: pd.DataFrame, start: datetime, end: datetime, **kwargs
    ) -> pd.DataFrame:
        """Linear interpolation method."""
        return data.interpolate(method="linear")

    def _cubic_spline(
        self, data: pd.DataFrame, start: datetime, end: datetime, **kwargs
    ) -> pd.DataFrame:
        """Cubic spline interpolation method."""
        return data.interpolate(method="cubic")

    def _knn_imputation(
        self, data: pd.DataFrame, start: datetime, end: datetime, **kwargs
    ) -> pd.DataFrame:
        """KNN imputation method."""
        n_neighbors = kwargs.get("n_neighbors", 5)

        # Only use numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) > 0:
            imputer = KNNImputer(n_neighbors=n_neighbors)
            data[numeric_cols] = imputer.fit_transform(data[numeric_cols])

        return data

    def _seasonal_decomposition(
        self, data: pd.DataFrame, start: datetime, end: datetime, **kwargs
    ) -> pd.DataFrame:
        """Seasonal decomposition-based filling."""
        # Simplified seasonal filling - use same time of day from previous days
        filled_data = data.copy()

        for col in data.select_dtypes(include=[np.number]).columns:
            if col in filled_data.columns:
                filled_data[col] = filled_data[col].fillna(
                    filled_data.groupby(filled_data.index.time)[col].transform("mean")
                )

        return filled_data

    def _market_hours_aware_fill(
        self, data: pd.DataFrame, start: datetime, end: datetime, **kwargs
    ) -> pd.DataFrame:
        """Market hours aware filling (crypto markets are 24/7, but can adapt)."""
        # For crypto, just use linear interpolation during gaps
        return self._linear_interpolation(data, start, end, **kwargs)


class OutlierDetector:
    """
    Outlier detection using multiple statistical methods.
    """

    def __init__(self):
        """Initialize outlier detector."""
        self.methods = {
            "iqr": self._iqr_method,
            "z_score": self._z_score_method,
            "modified_z_score": self._modified_z_score_method,
            "isolation_forest": self._isolation_forest_method,
            "price_spike": self._price_spike_method,
            "volume_anomaly": self._volume_anomaly_method,
        }

        logger.info("OutlierDetector initialized")

    def detect_outliers(
        self, data: pd.DataFrame, methods: List[str] = None, **kwargs
    ) -> Tuple[pd.DataFrame, List[QualityIssue]]:
        """
        Detect outliers using specified methods.

        Args:
            data: DataFrame to analyze
            methods: List of detection methods to use
            **kwargs: Method-specific parameters

        Returns:
            Tuple of (outlier_flags, issues_found)
        """
        if methods is None:
            methods = ["iqr", "z_score", "price_spike", "volume_anomaly"]

        issues = []
        outlier_flags = pd.DataFrame(index=data.index)

        for method in methods:
            if method in self.methods:
                try:
                    method_flags, method_issues = self.methods[method](data, **kwargs)
                    outlier_flags[f"{method}_outlier"] = method_flags
                    issues.extend(method_issues)

                except Exception as e:
                    logger.error(f"Outlier detection method {method} failed: {e}")

        # Combine outlier flags (majority vote or any method)
        combine_method = kwargs.get("combine_method", "any")
        if combine_method == "any":
            outlier_flags["is_outlier"] = outlier_flags.any(axis=1)
        elif combine_method == "majority":
            outlier_flags["is_outlier"] = outlier_flags.sum(axis=1) > len(methods) / 2
        else:
            outlier_flags["is_outlier"] = outlier_flags.all(axis=1)

        return outlier_flags, issues

    def _iqr_method(
        self, data: pd.DataFrame, **kwargs
    ) -> Tuple[pd.Series, List[QualityIssue]]:
        """Interquartile Range method."""
        multiplier = kwargs.get("iqr_multiplier", 1.5)
        issues = []
        outliers = pd.Series(False, index=data.index)

        for col in data.select_dtypes(include=[np.number]).columns:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - multiplier * IQR
            upper_bound = Q3 + multiplier * IQR

            col_outliers = (data[col] < lower_bound) | (data[col] > upper_bound)
            outliers |= col_outliers

            # Record issues
            for idx in data[col_outliers].index:
                issues.append(
                    QualityIssue(
                        issue_type=DataQualityIssue.OUTLIER,
                        timestamp=idx,
                        symbol=kwargs.get("symbol", "unknown"),
                        field=col,
                        value=data.loc[idx, col],
                        expected_value=f"[{lower_bound:.4f}, {upper_bound:.4f}]",
                        severity="medium",
                        description=f"IQR outlier in {col}",
                    )
                )

        return outliers, issues

    def _z_score_method(
        self, data: pd.DataFrame, **kwargs
    ) -> Tuple[pd.Series, List[QualityIssue]]:
        """Z-score method."""
        threshold = kwargs.get("z_threshold", 3.0)
        issues = []
        outliers = pd.Series(False, index=data.index)

        for col in data.select_dtypes(include=[np.number]).columns:
            z_scores = np.abs(stats.zscore(data[col].dropna()))
            col_outliers = pd.Series(False, index=data.index)
            col_outliers.loc[data[col].dropna().index] = z_scores > threshold
            outliers |= col_outliers

            # Record issues
            for idx in data[col_outliers].index:
                issues.append(
                    QualityIssue(
                        issue_type=DataQualityIssue.OUTLIER,
                        timestamp=idx,
                        symbol=kwargs.get("symbol", "unknown"),
                        field=col,
                        value=data.loc[idx, col],
                        severity="medium",
                        description=f"Z-score outlier in {col} (z={z_scores[data.index.get_loc(idx)]:.2f})",
                    )
                )

        return outliers, issues

    def _modified_z_score_method(
        self, data: pd.DataFrame, **kwargs
    ) -> Tuple[pd.Series, List[QualityIssue]]:
        """Modified Z-score method using median."""
        threshold = kwargs.get("modified_z_threshold", 3.5)
        issues = []
        outliers = pd.Series(False, index=data.index)

        for col in data.select_dtypes(include=[np.number]).columns:
            median = data[col].median()
            mad = np.median(np.abs(data[col] - median))

            if mad != 0:
                modified_z_scores = 0.6745 * (data[col] - median) / mad
                col_outliers = np.abs(modified_z_scores) > threshold
                outliers |= col_outliers

                # Record issues
                for idx in data[col_outliers].index:
                    issues.append(
                        QualityIssue(
                            issue_type=DataQualityIssue.OUTLIER,
                            timestamp=idx,
                            symbol=kwargs.get("symbol", "unknown"),
                            field=col,
                            value=data.loc[idx, col],
                            severity="medium",
                            description=f"Modified Z-score outlier in {col}",
                        )
                    )

        return outliers, issues

    def _isolation_forest_method(
        self, data: pd.DataFrame, **kwargs
    ) -> Tuple[pd.Series, List[QualityIssue]]:
        """Isolation Forest method."""
        try:
            from sklearn.ensemble import IsolationForest

            contamination = kwargs.get("contamination", 0.1)
            issues = []

            # Use only numeric columns
            numeric_data = data.select_dtypes(include=[np.number]).dropna()

            if len(numeric_data) > 0:
                iso_forest = IsolationForest(
                    contamination=contamination, random_state=42
                )
                outlier_labels = iso_forest.fit_predict(numeric_data)

                outliers = pd.Series(False, index=data.index)
                outliers.loc[numeric_data.index] = outlier_labels == -1

                # Record issues
                for idx in numeric_data[outlier_labels == -1].index:
                    issues.append(
                        QualityIssue(
                            issue_type=DataQualityIssue.OUTLIER,
                            timestamp=idx,
                            symbol=kwargs.get("symbol", "unknown"),
                            field="multiple",
                            value="anomalous pattern",
                            severity="medium",
                            description="Isolation Forest outlier",
                        )
                    )

                return outliers, issues

        except ImportError:
            logger.warning("sklearn not available for Isolation Forest")

        return pd.Series(False, index=data.index), []

    def _price_spike_method(
        self, data: pd.DataFrame, **kwargs
    ) -> Tuple[pd.Series, List[QualityIssue]]:
        """Price spike detection."""
        spike_threshold = kwargs.get("spike_threshold", 0.1)  # 10% change
        issues = []
        outliers = pd.Series(False, index=data.index)

        price_cols = ["open", "high", "low", "close"]
        available_price_cols = [col for col in price_cols if col in data.columns]

        if available_price_cols:
            # Use close price for spike detection
            price_col = (
                "close" if "close" in available_price_cols else available_price_cols[0]
            )

            # Calculate price changes
            price_changes = data[price_col].pct_change().abs()

            # Detect spikes
            spike_outliers = price_changes > spike_threshold
            outliers |= spike_outliers

            # Record issues
            for idx in data[spike_outliers].index:
                issues.append(
                    QualityIssue(
                        issue_type=DataQualityIssue.PRICE_SPIKE,
                        timestamp=idx,
                        symbol=kwargs.get("symbol", "unknown"),
                        field=price_col,
                        value=data.loc[idx, price_col],
                        severity="high",
                        description=f"Price spike: {price_changes.loc[idx]:.2%} change",
                    )
                )

        return outliers, issues

    def _volume_anomaly_method(
        self, data: pd.DataFrame, **kwargs
    ) -> Tuple[pd.Series, List[QualityIssue]]:
        """Volume anomaly detection."""
        volume_threshold = kwargs.get("volume_threshold", 5.0)  # 5x average
        issues = []
        outliers = pd.Series(False, index=data.index)

        if "volume" in data.columns:
            # Calculate rolling average volume
            window = kwargs.get("volume_window", 20)
            avg_volume = data["volume"].rolling(window=window).mean()

            # Detect volume anomalies
            volume_ratio = data["volume"] / avg_volume
            volume_outliers = volume_ratio > volume_threshold
            outliers |= volume_outliers

            # Record issues
            for idx in data[volume_outliers].index:
                issues.append(
                    QualityIssue(
                        issue_type=DataQualityIssue.VOLUME_ANOMALY,
                        timestamp=idx,
                        symbol=kwargs.get("symbol", "unknown"),
                        field="volume",
                        value=data.loc[idx, "volume"],
                        severity="medium",
                        description=f"Volume anomaly: {volume_ratio.loc[idx]:.1f}x average",
                    )
                )

        return outliers, issues


class DataNormalizer:
    """
    Data normalization and standardization.
    """

    def __init__(self):
        """Initialize data normalizer."""
        self.scalers = {}
        self.normalization_params = {}

        logger.info("DataNormalizer initialized")

    def normalize_data(
        self,
        data: pd.DataFrame,
        method: str = "standard",
        columns: List[str] = None,
        fit_params: bool = True,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Normalize data using specified method.

        Args:
            data: DataFrame to normalize
            method: Normalization method ('standard', 'robust', 'minmax')
            columns: Columns to normalize (None for all numeric)
            fit_params: Whether to fit normalization parameters

        Returns:
            Tuple of (normalized_data, normalization_params)
        """
        if columns is None:
            columns = data.select_dtypes(include=[np.number]).columns.tolist()

        normalized_data = data.copy()
        params = {}

        for col in columns:
            if col in data.columns:
                normalized_col, col_params = self._normalize_column(
                    data[col], method, col, fit_params
                )
                normalized_data[col] = normalized_col
                params[col] = col_params

        return normalized_data, params

    def _normalize_column(
        self, series: pd.Series, method: str, column_name: str, fit_params: bool
    ) -> Tuple[pd.Series, Dict[str, Any]]:
        """Normalize a single column."""
        if method == "standard":
            scaler = StandardScaler()
        elif method == "robust":
            scaler = RobustScaler()
        elif method == "minmax":
            scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown normalization method: {method}")

        # Reshape for sklearn
        values = series.values.reshape(-1, 1)

        if fit_params:
            normalized_values = scaler.fit_transform(values)
            self.scalers[column_name] = scaler
        else:
            if column_name in self.scalers:
                normalized_values = self.scalers[column_name].transform(values)
            else:
                # Fallback to fitting if no saved scaler
                normalized_values = scaler.fit_transform(values)
                self.scalers[column_name] = scaler

        normalized_series = pd.Series(
            normalized_values.flatten(), index=series.index, name=series.name
        )

        # Extract parameters
        if hasattr(scaler, "mean_"):
            params = {"mean": scaler.mean_[0], "scale": scaler.scale_[0]}
        elif hasattr(scaler, "center_"):
            params = {"center": scaler.center_[0], "scale": scaler.scale_[0]}
        elif hasattr(scaler, "data_min_"):
            params = {
                "data_min": scaler.data_min_[0],
                "data_max": scaler.data_max_[0],
                "data_range": scaler.data_range_[0],
            }
        else:
            params = {}

        return normalized_series, params

    def denormalize_data(
        self, data: pd.DataFrame, columns: List[str] = None
    ) -> pd.DataFrame:
        """Denormalize data using saved parameters."""
        if columns is None:
            columns = [col for col in data.columns if col in self.scalers]

        denormalized_data = data.copy()

        for col in columns:
            if col in self.scalers:
                values = data[col].values.reshape(-1, 1)
                denormalized_values = self.scalers[col].inverse_transform(values)
                denormalized_data[col] = denormalized_values.flatten()

        return denormalized_data


class DataQualityPipeline:
    """
    Comprehensive data quality pipeline.
    """

    def __init__(self):
        """Initialize data quality pipeline."""
        self.gap_filler = GapFiller()
        self.outlier_detector = OutlierDetector()
        self.normalizer = DataNormalizer()

        logger.info("DataQualityPipeline initialized")

    def process_data(
        self, data: pd.DataFrame, symbol: str = "unknown", config: Dict[str, Any] = None
    ) -> Tuple[pd.DataFrame, DataQualityReport]:
        """
        Process data through complete quality pipeline.

        Args:
            data: Raw data DataFrame
            symbol: Symbol identifier
            config: Processing configuration

        Returns:
            Tuple of (processed_data, quality_report)
        """
        if config is None:
            config = self._get_default_config()

        processed_data = data.copy()
        all_issues = []

        # Step 1: Basic validation
        validation_issues = self._validate_basic_structure(processed_data, symbol)
        all_issues.extend(validation_issues)

        # Step 2: Remove duplicates
        processed_data, duplicate_issues = self._remove_duplicates(
            processed_data, symbol
        )
        all_issues.extend(duplicate_issues)

        # Step 3: Timezone normalization
        processed_data, timezone_issues = self._normalize_timezone(
            processed_data, symbol, config
        )
        all_issues.extend(timezone_issues)

        # Step 4: Gap filling
        if config.get("fill_gaps", True):
            processed_data, gap_issues = self.gap_filler.fill_gaps(
                processed_data,
                method=config.get("gap_fill_method", "linear_interpolation"),
                max_gap_size=config.get("max_gap_size", 10),
                symbol=symbol,
            )
            all_issues.extend(gap_issues)

        # Step 5: Outlier detection
        if config.get("detect_outliers", True):
            outlier_flags, outlier_issues = self.outlier_detector.detect_outliers(
                processed_data,
                methods=config.get(
                    "outlier_methods", ["iqr", "price_spike", "volume_anomaly"]
                ),
                symbol=symbol,
            )
            all_issues.extend(outlier_issues)

            # Handle outliers
            if config.get("remove_outliers", False):
                processed_data = processed_data[~outlier_flags["is_outlier"]]
            elif config.get("winsorize_outliers", True):
                processed_data = self._winsorize_outliers(processed_data, outlier_flags)

        # Step 6: Data normalization
        if config.get("normalize_data", False):
            processed_data, norm_params = self.normalizer.normalize_data(
                processed_data,
                method=config.get("normalization_method", "standard"),
                columns=config.get("normalize_columns"),
            )

        # Generate quality report
        quality_report = self._generate_quality_report(data, processed_data, all_issues)

        return processed_data, quality_report

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default processing configuration."""
        return {
            "fill_gaps": True,
            "gap_fill_method": "linear_interpolation",
            "max_gap_size": 10,
            "detect_outliers": True,
            "outlier_methods": ["iqr", "price_spike", "volume_anomaly"],
            "remove_outliers": False,
            "winsorize_outliers": True,
            "normalize_data": False,
            "normalization_method": "standard",
            "target_timezone": "UTC",
        }

    def _validate_basic_structure(
        self, data: pd.DataFrame, symbol: str
    ) -> List[QualityIssue]:
        """Validate basic data structure."""
        issues = []

        # Check for required columns
        required_cols = ["open", "high", "low", "close", "volume"]
        missing_cols = [col for col in required_cols if col not in data.columns]

        for col in missing_cols:
            issues.append(
                QualityIssue(
                    issue_type=DataQualityIssue.INVALID_VALUE,
                    timestamp=datetime.now(),
                    symbol=symbol,
                    field=col,
                    value="missing",
                    severity="critical",
                    description=f"Required column {col} is missing",
                )
            )

        # Check for negative prices
        price_cols = ["open", "high", "low", "close"]
        for col in price_cols:
            if col in data.columns:
                negative_prices = data[data[col] < 0]
                for idx in negative_prices.index:
                    issues.append(
                        QualityIssue(
                            issue_type=DataQualityIssue.INVALID_VALUE,
                            timestamp=idx,
                            symbol=symbol,
                            field=col,
                            value=data.loc[idx, col],
                            severity="high",
                            description=f"Negative price in {col}",
                        )
                    )

        # Check OHLC relationships
        if all(col in data.columns for col in ["open", "high", "low", "close"]):
            invalid_ohlc = data[
                (data["high"] < data["low"])
                | (data["high"] < data["open"])
                | (data["high"] < data["close"])
                | (data["low"] > data["open"])
                | (data["low"] > data["close"])
            ]

            for idx in invalid_ohlc.index:
                issues.append(
                    QualityIssue(
                        issue_type=DataQualityIssue.INVALID_VALUE,
                        timestamp=idx,
                        symbol=symbol,
                        field="OHLC",
                        value="invalid relationship",
                        severity="high",
                        description="Invalid OHLC relationship",
                    )
                )

        return issues

    def _remove_duplicates(
        self, data: pd.DataFrame, symbol: str
    ) -> Tuple[pd.DataFrame, List[QualityIssue]]:
        """Remove duplicate records."""
        issues = []

        # Find duplicates
        duplicates = data.duplicated()
        duplicate_count = duplicates.sum()

        if duplicate_count > 0:
            duplicate_indices = data[duplicates].index
            for idx in duplicate_indices:
                issues.append(
                    QualityIssue(
                        issue_type=DataQualityIssue.DUPLICATE,
                        timestamp=idx,
                        symbol=symbol,
                        field="all",
                        value="duplicate record",
                        severity="medium",
                        description="Duplicate record removed",
                        fixed=True,
                    )
                )

            # Remove duplicates
            data = data[~duplicates]
            logger.info(f"Removed {duplicate_count} duplicate records for {symbol}")

        return data, issues

    def _normalize_timezone(
        self, data: pd.DataFrame, symbol: str, config: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, List[QualityIssue]]:
        """Normalize timezone information."""
        issues = []
        target_tz = config.get("target_timezone", "UTC")

        if hasattr(data.index, "tz"):
            if data.index.tz is None:
                # Assume UTC if no timezone
                data.index = data.index.tz_localize("UTC")
                issues.append(
                    QualityIssue(
                        issue_type=DataQualityIssue.TIMEZONE_INCONSISTENCY,
                        timestamp=datetime.now(),
                        symbol=symbol,
                        field="timestamp",
                        value="no timezone",
                        severity="medium",
                        description="Assumed UTC timezone",
                        fixed=True,
                    )
                )

            # Convert to target timezone
            if str(data.index.tz) != target_tz:
                data.index = data.index.tz_convert(target_tz)
                issues.append(
                    QualityIssue(
                        issue_type=DataQualityIssue.TIMEZONE_INCONSISTENCY,
                        timestamp=datetime.now(),
                        symbol=symbol,
                        field="timestamp",
                        value=f"converted to {target_tz}",
                        severity="low",
                        description=f"Converted timezone to {target_tz}",
                        fixed=True,
                    )
                )

        return data, issues

    def _winsorize_outliers(
        self, data: pd.DataFrame, outlier_flags: pd.DataFrame
    ) -> pd.DataFrame:
        """Winsorize outliers instead of removing them."""
        winsorized_data = data.copy()

        for col in data.select_dtypes(include=[np.number]).columns:
            if col in data.columns:
                # Calculate winsorization bounds (5th and 95th percentiles)
                lower_bound = data[col].quantile(0.05)
                upper_bound = data[col].quantile(0.95)

                # Apply winsorization
                winsorized_data[col] = np.clip(data[col], lower_bound, upper_bound)

        return winsorized_data

    def _generate_quality_report(
        self,
        original_data: pd.DataFrame,
        processed_data: pd.DataFrame,
        issues: List[QualityIssue],
    ) -> DataQualityReport:
        """Generate comprehensive quality report."""
        total_records = len(original_data)
        valid_records = len(processed_data)

        # Calculate scores
        completeness_score = valid_records / total_records if total_records > 0 else 0

        # Count issues by severity
        critical_issues = sum(1 for issue in issues if issue.severity == "critical")
        high_issues = sum(1 for issue in issues if issue.severity == "high")
        medium_issues = sum(1 for issue in issues if issue.severity == "medium")

        # Calculate accuracy score (based on issues)
        total_issues = len(issues)
        accuracy_score = (
            max(0, 1 - (total_issues / total_records)) if total_records > 0 else 1
        )

        # Calculate consistency score (based on critical issues)
        consistency_score = (
            max(0, 1 - (critical_issues / total_records)) if total_records > 0 else 1
        )

        # Overall score (weighted average)
        overall_score = (
            0.4 * completeness_score + 0.4 * accuracy_score + 0.2 * consistency_score
        )

        # Generate recommendations
        recommendations = []
        if completeness_score < 0.9:
            recommendations.append(
                "Consider improving data collection to reduce missing values"
            )
        if critical_issues > 0:
            recommendations.append("Address critical data quality issues immediately")
        if high_issues > total_records * 0.05:
            recommendations.append("Review data sources for high-severity issues")
        if overall_score < 0.8:
            recommendations.append("Implement additional data validation checks")

        return DataQualityReport(
            total_records=total_records,
            valid_records=valid_records,
            issues=issues,
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            consistency_score=consistency_score,
            overall_score=overall_score,
            recommendations=recommendations,
        )
