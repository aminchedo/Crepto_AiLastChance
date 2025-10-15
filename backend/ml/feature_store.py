"""
Feature Store & Registry
Comprehensive feature management with versioning, normalization, and importance tracking
"""

import hashlib
import json
import logging
import pickle
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class FeatureType(Enum):
    """Feature types."""

    TECHNICAL_INDICATOR = "technical_indicator"
    PRICE_ACTION = "price_action"
    VOLUME = "volume"
    VOLATILITY = "volatility"
    MOMENTUM = "momentum"
    TREND = "trend"
    PATTERN = "pattern"
    SMC = "smc"
    CUSTOM = "custom"


class NormalizationMethod(Enum):
    """Normalization methods."""

    Z_SCORE = "z_score"
    MIN_MAX = "min_max"
    ROBUST_SCALER = "robust_scaler"
    QUANTILE = "quantile"
    LOG_TRANSFORM = "log_transform"
    NONE = "none"


@dataclass
class FeatureDefinition:
    """Feature definition with metadata."""

    name: str
    feature_type: FeatureType
    description: str
    version: str
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    normalization_method: NormalizationMethod = NormalizationMethod.Z_SCORE
    importance_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True


@dataclass
class FeatureStats:
    """Feature statistics for normalization."""

    mean: float
    std: float
    min: float
    max: float
    median: float
    q25: float
    q75: float
    count: int
    null_count: int


class FeatureRegistry:
    """
    Feature Registry for managing feature definitions and metadata.
    """

    def __init__(self, db_path: str = "features.db"):
        """
        Initialize feature registry.

        Args:
            db_path: Path to SQLite database for feature metadata
        """
        self.db_path = db_path
        self.features: Dict[str, FeatureDefinition] = {}
        self.feature_stats: Dict[str, FeatureStats] = {}
        self.normalization_params: Dict[str, Dict[str, Any]] = {}

        self._init_database()
        self._load_features()

        logger.info(f"FeatureRegistry initialized with {len(self.features)} features")

    def _init_database(self):
        """Initialize SQLite database for feature metadata."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create features table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS features (
                name TEXT PRIMARY KEY,
                feature_type TEXT NOT NULL,
                description TEXT,
                version TEXT NOT NULL,
                dependencies TEXT,
                parameters TEXT,
                normalization_method TEXT,
                importance_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """
        )

        # Create feature_stats table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS feature_stats (
                feature_name TEXT PRIMARY KEY,
                mean REAL,
                std REAL,
                min REAL,
                max REAL,
                median REAL,
                q25 REAL,
                q75 REAL,
                count INTEGER,
                null_count INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feature_name) REFERENCES features (name)
            )
        """
        )

        # Create normalization_params table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS normalization_params (
                feature_name TEXT PRIMARY KEY,
                method TEXT,
                params TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feature_name) REFERENCES features (name)
            )
        """
        )

        conn.commit()
        conn.close()

    def register_feature(self, feature_def: FeatureDefinition) -> bool:
        """
        Register a new feature definition.

        Args:
            feature_def: Feature definition

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO features 
                (name, feature_type, description, version, dependencies, parameters, 
                 normalization_method, importance_score, created_at, updated_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    feature_def.name,
                    feature_def.feature_type.value,
                    feature_def.description,
                    feature_def.version,
                    json.dumps(feature_def.dependencies),
                    json.dumps(feature_def.parameters),
                    feature_def.normalization_method.value,
                    feature_def.importance_score,
                    feature_def.created_at.isoformat(),
                    datetime.now().isoformat(),
                    feature_def.is_active,
                ),
            )

            conn.commit()
            conn.close()

            self.features[feature_def.name] = feature_def
            logger.info(f"Registered feature: {feature_def.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to register feature {feature_def.name}: {e}")
            return False

    def get_feature(self, name: str) -> Optional[FeatureDefinition]:
        """
        Get feature definition by name.

        Args:
            name: Feature name

        Returns:
            Feature definition or None
        """
        return self.features.get(name)

    def list_features(
        self, feature_type: Optional[FeatureType] = None, is_active: bool = True
    ) -> List[FeatureDefinition]:
        """
        List features with optional filtering.

        Args:
            feature_type: Filter by feature type
            is_active: Filter by active status

        Returns:
            List of feature definitions
        """
        features = list(self.features.values())

        if feature_type:
            features = [f for f in features if f.feature_type == feature_type]

        if is_active:
            features = [f for f in features if f.is_active]

        return features

    def update_feature_importance(self, name: str, importance_score: float) -> bool:
        """
        Update feature importance score.

        Args:
            name: Feature name
            importance_score: New importance score

        Returns:
            True if successful, False otherwise
        """
        try:
            if name in self.features:
                self.features[name].importance_score = importance_score
                self.features[name].updated_at = datetime.now()

                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE features 
                    SET importance_score = ?, updated_at = ?
                    WHERE name = ?
                """,
                    (importance_score, datetime.now().isoformat(), name),
                )

                conn.commit()
                conn.close()

                logger.info(
                    f"Updated importance for feature {name}: {importance_score}"
                )
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to update importance for {name}: {e}")
            return False

    def _load_features(self):
        """Load features from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM features")
            rows = cursor.fetchall()

            for row in rows:
                feature_def = FeatureDefinition(
                    name=row[0],
                    feature_type=FeatureType(row[1]),
                    description=row[2],
                    version=row[3],
                    dependencies=json.loads(row[4]) if row[4] else [],
                    parameters=json.loads(row[5]) if row[5] else {},
                    normalization_method=NormalizationMethod(row[6]),
                    importance_score=row[7],
                    created_at=datetime.fromisoformat(row[8]),
                    updated_at=datetime.fromisoformat(row[9]),
                    is_active=bool(row[10]),
                )

                self.features[feature_def.name] = feature_def

            conn.close()

        except Exception as e:
            logger.error(f"Failed to load features: {e}")


class FeatureNormalizer:
    """
    Feature normalization with multiple methods and parameter persistence.
    """

    def __init__(self, registry: FeatureRegistry):
        """
        Initialize feature normalizer.

        Args:
            registry: Feature registry instance
        """
        self.registry = registry
        self.normalization_params: Dict[str, Dict[str, Any]] = {}

        logger.info("FeatureNormalizer initialized")

    def fit_normalization_params(
        self, feature_name: str, data: np.ndarray, method: NormalizationMethod
    ) -> Dict[str, Any]:
        """
        Fit normalization parameters for a feature.

        Args:
            feature_name: Feature name
            data: Training data
            method: Normalization method

        Returns:
            Normalization parameters
        """
        params = {}

        if method == NormalizationMethod.Z_SCORE:
            params = {"mean": np.mean(data), "std": np.std(data)}

        elif method == NormalizationMethod.MIN_MAX:
            params = {"min": np.min(data), "max": np.max(data)}

        elif method == NormalizationMethod.ROBUST_SCALER:
            params = {
                "median": np.median(data),
                "q25": np.percentile(data, 25),
                "q75": np.percentile(data, 75),
            }

        elif method == NormalizationMethod.QUANTILE:
            params = {"q25": np.percentile(data, 25), "q75": np.percentile(data, 75)}

        elif method == NormalizationMethod.LOG_TRANSFORM:
            params = {"offset": 1.0}  # Add offset to handle zeros

        self.normalization_params[feature_name] = params
        self._save_normalization_params(feature_name, method, params)

        return params

    def normalize_feature(
        self,
        feature_name: str,
        data: np.ndarray,
        method: Optional[NormalizationMethod] = None,
    ) -> np.ndarray:
        """
        Normalize feature data.

        Args:
            feature_name: Feature name
            data: Data to normalize
            method: Normalization method (uses feature definition if None)

        Returns:
            Normalized data
        """
        if method is None:
            feature_def = self.registry.get_feature(feature_name)
            if feature_def:
                method = feature_def.normalization_method
            else:
                method = NormalizationMethod.Z_SCORE

        if method == NormalizationMethod.NONE:
            return data

        # Load parameters if not available
        if feature_name not in self.normalization_params:
            self._load_normalization_params(feature_name)

        params = self.normalization_params.get(feature_name, {})

        if method == NormalizationMethod.Z_SCORE:
            if "mean" in params and "std" in params:
                return (data - params["mean"]) / (params["std"] + 1e-8)
            else:
                return (data - np.mean(data)) / (np.std(data) + 1e-8)

        elif method == NormalizationMethod.MIN_MAX:
            if "min" in params and "max" in params:
                return (data - params["min"]) / (params["max"] - params["min"] + 1e-8)
            else:
                return (data - np.min(data)) / (np.max(data) - np.min(data) + 1e-8)

        elif method == NormalizationMethod.ROBUST_SCALER:
            if "median" in params and "q25" in params and "q75" in params:
                return (data - params["median"]) / (
                    params["q75"] - params["q25"] + 1e-8
                )
            else:
                median = np.median(data)
                q25 = np.percentile(data, 25)
                q75 = np.percentile(data, 75)
                return (data - median) / (q75 - q25 + 1e-8)

        elif method == NormalizationMethod.QUANTILE:
            if "q25" in params and "q75" in params:
                return (data - params["q25"]) / (params["q75"] - params["q25"] + 1e-8)
            else:
                q25 = np.percentile(data, 25)
                q75 = np.percentile(data, 75)
                return (data - q25) / (q75 - q25 + 1e-8)

        elif method == NormalizationMethod.LOG_TRANSFORM:
            offset = params.get("offset", 1.0)
            return np.log(data + offset)

        return data

    def inverse_normalize_feature(
        self,
        feature_name: str,
        normalized_data: np.ndarray,
        method: Optional[NormalizationMethod] = None,
    ) -> np.ndarray:
        """
        Inverse normalize feature data.

        Args:
            feature_name: Feature name
            normalized_data: Normalized data
            method: Normalization method

        Returns:
            Original scale data
        """
        if method is None:
            feature_def = self.registry.get_feature(feature_name)
            if feature_def:
                method = feature_def.normalization_method
            else:
                method = NormalizationMethod.Z_SCORE

        if method == NormalizationMethod.NONE:
            return normalized_data

        params = self.normalization_params.get(feature_name, {})

        if method == NormalizationMethod.Z_SCORE:
            if "mean" in params and "std" in params:
                return normalized_data * params["std"] + params["mean"]

        elif method == NormalizationMethod.MIN_MAX:
            if "min" in params and "max" in params:
                return normalized_data * (params["max"] - params["min"]) + params["min"]

        elif method == NormalizationMethod.ROBUST_SCALER:
            if "median" in params and "q25" in params and "q75" in params:
                return (
                    normalized_data * (params["q75"] - params["q25"]) + params["median"]
                )

        elif method == NormalizationMethod.QUANTILE:
            if "q25" in params and "q75" in params:
                return normalized_data * (params["q75"] - params["q25"]) + params["q25"]

        elif method == NormalizationMethod.LOG_TRANSFORM:
            offset = params.get("offset", 1.0)
            return np.exp(normalized_data) - offset

        return normalized_data

    def _save_normalization_params(
        self, feature_name: str, method: NormalizationMethod, params: Dict[str, Any]
    ):
        """Save normalization parameters to database."""
        try:
            conn = sqlite3.connect(self.registry.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO normalization_params 
                (feature_name, method, params, updated_at)
                VALUES (?, ?, ?, ?)
            """,
                (
                    feature_name,
                    method.value,
                    json.dumps(params),
                    datetime.now().isoformat(),
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to save normalization params for {feature_name}: {e}")

    def _load_normalization_params(self, feature_name: str):
        """Load normalization parameters from database."""
        try:
            conn = sqlite3.connect(self.registry.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT method, params FROM normalization_params 
                WHERE feature_name = ?
            """,
                (feature_name,),
            )

            row = cursor.fetchone()
            if row:
                method = NormalizationMethod(row[0])
                params = json.loads(row[1])
                self.normalization_params[feature_name] = params

            conn.close()

        except Exception as e:
            logger.error(f"Failed to load normalization params for {feature_name}: {e}")


class FeatureStore:
    """
    Comprehensive Feature Store for managing feature engineering pipeline.
    """

    def __init__(self, db_path: str = "features.db", cache_dir: str = "feature_cache"):
        """
        Initialize feature store.

        Args:
            db_path: Path to SQLite database
            cache_dir: Directory for feature caching
        """
        self.db_path = db_path
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        self.registry = FeatureRegistry(db_path)
        self.normalizer = FeatureNormalizer(self.registry)
        self.feature_cache: Dict[str, np.ndarray] = {}

        logger.info(
            f"FeatureStore initialized: db_path={db_path}, cache_dir={cache_dir}"
        )

    def register_feature(
        self,
        name: str,
        feature_type: FeatureType,
        description: str,
        version: str = "1.0.0",
        dependencies: List[str] = None,
        parameters: Dict[str, Any] = None,
        normalization_method: NormalizationMethod = NormalizationMethod.Z_SCORE,
    ) -> bool:
        """
        Register a new feature.

        Args:
            name: Feature name
            feature_type: Feature type
            description: Feature description
            version: Feature version
            dependencies: List of dependency features
            parameters: Feature parameters
            normalization_method: Normalization method

        Returns:
            True if successful, False otherwise
        """
        feature_def = FeatureDefinition(
            name=name,
            feature_type=feature_type,
            description=description,
            version=version,
            dependencies=dependencies or [],
            parameters=parameters or {},
            normalization_method=normalization_method,
        )

        return self.registry.register_feature(feature_def)

    def compute_feature(
        self, name: str, data: Dict[str, np.ndarray], force_recompute: bool = False
    ) -> np.ndarray:
        """
        Compute feature values.

        Args:
            name: Feature name
            data: Input data dictionary
            force_recompute: Force recomputation even if cached

        Returns:
            Feature values
        """
        # Check cache first
        if not force_recompute and name in self.feature_cache:
            return self.feature_cache[name]

        # Get feature definition
        feature_def = self.registry.get_feature(name)
        if not feature_def:
            raise ValueError(f"Feature {name} not registered")

        # Check dependencies
        for dep in feature_def.dependencies:
            if dep not in data:
                raise ValueError(f"Dependency {dep} not found in data")

        # Compute feature (placeholder - would integrate with actual feature computation)
        feature_values = self._compute_feature_impl(name, data, feature_def)

        # Normalize feature
        normalized_values = self.normalizer.normalize_feature(name, feature_values)

        # Cache result
        self.feature_cache[name] = normalized_values

        return normalized_values

    def _compute_feature_impl(
        self, name: str, data: Dict[str, np.ndarray], feature_def: FeatureDefinition
    ) -> np.ndarray:
        """
        Implement feature computation.

        Args:
            name: Feature name
            data: Input data
            feature_def: Feature definition

        Returns:
            Feature values
        """
        # This is a placeholder implementation
        # In practice, this would integrate with the actual feature computation modules

        if feature_def.feature_type == FeatureType.PRICE_ACTION:
            if "close" in data:
                return data["close"]

        elif feature_def.feature_type == FeatureType.VOLUME:
            if "volume" in data:
                return data["volume"]

        elif feature_def.feature_type == FeatureType.VOLATILITY:
            if "high" in data and "low" in data:
                return data["high"] - data["low"]

        # Default: return zeros
        if "close" in data:
            return np.zeros_like(data["close"])

        return np.array([])

    def get_feature_matrix(
        self, feature_names: List[str], data: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """
        Get feature matrix for multiple features.

        Args:
            feature_names: List of feature names
            data: Input data

        Returns:
            Feature matrix (samples x features)
        """
        features = []

        for name in feature_names:
            feature_values = self.compute_feature(name, data)
            features.append(feature_values)

        return np.column_stack(features)

    def update_feature_importance(
        self, feature_names: List[str], importance_scores: List[float]
    ) -> bool:
        """
        Update feature importance scores.

        Args:
            feature_names: List of feature names
            importance_scores: List of importance scores

        Returns:
            True if successful, False otherwise
        """
        if len(feature_names) != len(importance_scores):
            return False

        success = True
        for name, score in zip(feature_names, importance_scores):
            if not self.registry.update_feature_importance(name, score):
                success = False

        return success

    def get_top_features(
        self, n: int = 10, feature_type: Optional[FeatureType] = None
    ) -> List[Tuple[str, float]]:
        """
        Get top N features by importance.

        Args:
            n: Number of top features
            feature_type: Filter by feature type

        Returns:
            List of (feature_name, importance_score) tuples
        """
        features = self.registry.list_features(feature_type=feature_type)

        # Sort by importance score
        features.sort(key=lambda f: f.importance_score, reverse=True)

        return [(f.name, f.importance_score) for f in features[:n]]

    def clear_cache(self):
        """Clear feature cache."""
        self.feature_cache.clear()
        logger.info("Feature cache cleared")

    def export_features(
        self, feature_names: List[str], data: Dict[str, np.ndarray], output_path: str
    ) -> bool:
        """
        Export features to file.

        Args:
            feature_names: List of feature names
            data: Input data
            output_path: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            feature_matrix = self.get_feature_matrix(feature_names, data)

            # Save as numpy array
            np.save(output_path, feature_matrix)

            # Save metadata
            metadata = {
                "feature_names": feature_names,
                "shape": feature_matrix.shape,
                "exported_at": datetime.now().isoformat(),
            }

            with open(f"{output_path}.meta", "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Exported {len(feature_names)} features to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export features: {e}")
            return False

    def import_features(self, input_path: str) -> Optional[np.ndarray]:
        """
        Import features from file.

        Args:
            input_path: Input file path

        Returns:
            Feature matrix or None if failed
        """
        try:
            feature_matrix = np.load(input_path)

            # Load metadata
            metadata_path = f"{input_path}.meta"
            if Path(metadata_path).exists():
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
                    logger.info(f"Imported features: {metadata['feature_names']}")

            return feature_matrix

        except Exception as e:
            logger.error(f"Failed to import features: {e}")
            return None
