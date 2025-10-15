"""
Checkpoint Manager for Automatic Model Recovery
Handles saving, loading, and restoring model states during training
"""

import json
import logging
import os
import pickle
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import tensorflow as tf
from tensorflow import keras

from .stability_monitor import InstabilityEvent

logger = logging.getLogger(__name__)


class CheckpointManager:
    """
    Manages model checkpoints with automatic recovery capabilities.

    Features:
    - Automatic checkpoint saving at regular intervals
    - Best model tracking based on validation metrics
    - Emergency checkpoint creation before risky operations
    - Automatic restoration on instability detection
    - Checkpoint metadata and statistics tracking
    """

    def __init__(
        self,
        checkpoint_dir: str = "./checkpoints",
        max_checkpoints: int = 10,
        save_frequency: int = 10,  # Save every N epochs
        best_metric: str = "val_loss",
        best_mode: str = "min",  # "min" or "max"
        backup_frequency: int = 50,  # Backup every N epochs
        compression: bool = True,
    ):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_dir: Directory to store checkpoints
            max_checkpoints: Maximum number of checkpoints to keep
            save_frequency: How often to save checkpoints (epochs)
            best_metric: Metric to use for best model selection
            best_mode: Whether to minimize or maximize the metric
            backup_frequency: How often to create full backups
            compression: Whether to compress checkpoints
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.max_checkpoints = max_checkpoints
        self.save_frequency = save_frequency
        self.best_metric = best_metric
        self.best_mode = best_mode
        self.backup_frequency = backup_frequency
        self.compression = compression

        # Create checkpoint directory
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # State tracking
        self.checkpoints = []
        self.best_checkpoint = None
        self.best_score = float("inf") if best_mode == "min" else float("-inf")
        self.last_save_epoch = -1
        self.last_backup_epoch = -1

        # Statistics
        self.total_saves = 0
        self.total_loads = 0
        self.total_restores = 0

        logger.info(
            f"Checkpoint manager initialized: dir={checkpoint_dir}, "
            f"max_checkpoints={max_checkpoints}, save_frequency={save_frequency}"
        )

    def _get_checkpoint_path(
        self, epoch: int, checkpoint_type: str = "regular"
    ) -> Path:
        """Get checkpoint file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"checkpoint_epoch_{epoch:04d}_{checkpoint_type}_{timestamp}"

        if self.compression:
            filename += ".tar.gz"
        else:
            filename += ".h5"

        return self.checkpoint_dir / filename

    def _get_metadata_path(self, checkpoint_path: Path) -> Path:
        """Get metadata file path for checkpoint."""
        return checkpoint_path.with_suffix(".json")

    def _save_model_weights(self, model: keras.Model, path: Path) -> bool:
        """Save model weights to file."""
        try:
            if self.compression:
                # Save as compressed archive
                import tarfile

                with tarfile.open(path, "w:gz") as tar:
                    # Create temporary H5 file
                    temp_h5 = path.with_suffix(".h5")
                    model.save_weights(temp_h5)
                    tar.add(temp_h5, arcname="model_weights.h5")
                    os.remove(temp_h5)
            else:
                # Save directly as H5
                model.save_weights(path)

            return True
        except Exception as e:
            logger.error(f"Failed to save model weights to {path}: {e}")
            return False

    def _load_model_weights(self, model: keras.Model, path: Path) -> bool:
        """Load model weights from file."""
        try:
            if self.compression:
                # Load from compressed archive
                import tarfile

                with tarfile.open(path, "r:gz") as tar:
                    # Extract to temporary file
                    temp_h5 = path.with_suffix(".h5")
                    tar.extract("model_weights.h5", path=path.parent)
                    extracted_path = path.parent / "model_weights.h5"
                    extracted_path.rename(temp_h5)

                    # Load weights
                    model.load_weights(temp_h5)
                    os.remove(temp_h5)
            else:
                # Load directly from H5
                model.load_weights(path)

            return True
        except Exception as e:
            logger.error(f"Failed to load model weights from {path}: {e}")
            return False

    def _save_optimizer_state(
        self, optimizer: keras.optimizers.Optimizer, path: Path
    ) -> bool:
        """Save optimizer state."""
        try:
            optimizer_path = path.with_suffix(".optimizer.pkl")
            with open(optimizer_path, "wb") as f:
                pickle.dump(optimizer.get_config(), f)
            return True
        except Exception as e:
            logger.error(f"Failed to save optimizer state: {e}")
            return False

    def _load_optimizer_state(
        self, optimizer: keras.optimizers.Optimizer, path: Path
    ) -> bool:
        """Load optimizer state."""
        try:
            optimizer_path = path.with_suffix(".optimizer.pkl")
            if optimizer_path.exists():
                with open(optimizer_path, "rb") as f:
                    config = pickle.load(f)
                optimizer.from_config(config)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to load optimizer state: {e}")
            return False

    def save_checkpoint(
        self,
        model: keras.Model,
        optimizer: keras.optimizers.Optimizer,
        epoch: int,
        metrics: Dict[str, float],
        checkpoint_type: str = "regular",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Path]:
        """
        Save model checkpoint.

        Args:
            model: Keras model to save
            optimizer: Optimizer to save
            epoch: Current epoch
            metrics: Training metrics
            checkpoint_type: Type of checkpoint ("regular", "best", "emergency")
            metadata: Additional metadata to save

        Returns:
            Path to saved checkpoint, None if failed
        """
        try:
            checkpoint_path = self._get_checkpoint_path(epoch, checkpoint_type)
            metadata_path = self._get_metadata_path(checkpoint_path)

            # Save model weights
            if not self._save_model_weights(model, checkpoint_path):
                return None

            # Save optimizer state
            self._save_optimizer_state(optimizer, checkpoint_path)

            # Create metadata
            checkpoint_metadata = {
                "epoch": epoch,
                "checkpoint_type": checkpoint_type,
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics,
                "model_config": model.get_config(),
                "optimizer_config": optimizer.get_config(),
                "checkpoint_size": (
                    checkpoint_path.stat().st_size if checkpoint_path.exists() else 0
                ),
            }

            if metadata:
                checkpoint_metadata.update(metadata)

            # Save metadata
            with open(metadata_path, "w") as f:
                json.dump(checkpoint_metadata, f, indent=2)

            # Track checkpoint
            checkpoint_info = {
                "path": checkpoint_path,
                "metadata_path": metadata_path,
                "epoch": epoch,
                "type": checkpoint_type,
                "metrics": metrics,
                "timestamp": datetime.now(),
                "size": (
                    checkpoint_path.stat().st_size if checkpoint_path.exists() else 0
                ),
            }

            self.checkpoints.append(checkpoint_info)
            self.total_saves += 1
            self.last_save_epoch = epoch

            # Check if this is the best checkpoint
            if self.best_metric in metrics:
                score = metrics[self.best_metric]
                is_better = (self.best_mode == "min" and score < self.best_score) or (
                    self.best_mode == "max" and score > self.best_score
                )

                if is_better:
                    self.best_checkpoint = checkpoint_info
                    self.best_score = score
                    logger.info(
                        f"New best checkpoint: epoch={epoch}, "
                        f"{self.best_metric}={score:.6f}"
                    )

            # Cleanup old checkpoints
            self._cleanup_old_checkpoints()

            logger.info(
                f"Checkpoint saved: {checkpoint_path.name}, "
                f"epoch={epoch}, type={checkpoint_type}, size={checkpoint_info['size']} bytes"
            )

            return checkpoint_path

        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            return None

    def load_checkpoint(
        self,
        model: keras.Model,
        optimizer: keras.optimizers.Optimizer,
        checkpoint_path: Optional[Path] = None,
        load_optimizer: bool = True,
    ) -> bool:
        """
        Load model checkpoint.

        Args:
            model: Keras model to load into
            optimizer: Optimizer to load into
            checkpoint_path: Path to checkpoint (None for best checkpoint)
            load_optimizer: Whether to load optimizer state

        Returns:
            True if successful, False otherwise
        """
        try:
            if checkpoint_path is None:
                if self.best_checkpoint is None:
                    logger.error("No checkpoint available to load")
                    return False
                checkpoint_path = self.best_checkpoint["path"]

            if not checkpoint_path.exists():
                logger.error(f"Checkpoint file not found: {checkpoint_path}")
                return False

            # Load model weights
            if not self._load_model_weights(model, checkpoint_path):
                return False

            # Load optimizer state
            if load_optimizer:
                self._load_optimizer_state(optimizer, checkpoint_path)

            self.total_loads += 1

            # Load metadata
            metadata_path = self._get_metadata_path(checkpoint_path)
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)

                logger.info(
                    f"Checkpoint loaded: {checkpoint_path.name}, "
                    f"epoch={metadata.get('epoch', 'unknown')}, "
                    f"metrics={metadata.get('metrics', {})}"
                )
            else:
                logger.info(f"Checkpoint loaded: {checkpoint_path.name}")

            return True

        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return False

    def restore_from_instability(
        self,
        model: keras.Model,
        optimizer: keras.optimizers.Optimizer,
        events: List[InstabilityEvent],
        current_epoch: int,
    ) -> bool:
        """
        Restore model from instability events.

        Args:
            model: Keras model to restore
            optimizer: Optimizer to restore
            events: List of instability events
            current_epoch: Current epoch number

        Returns:
            True if restoration successful, False otherwise
        """
        try:
            # Determine restoration strategy based on events
            has_critical = any(
                e.severity == "critical" or e.event_type.value == "nan_inf"
                for e in events
            )

            if has_critical:
                # Use best checkpoint for critical events
                checkpoint_path = None  # Will use best checkpoint
                logger.info(
                    "Restoring from best checkpoint due to critical instability"
                )
            else:
                # Use most recent checkpoint for non-critical events
                if self.checkpoints:
                    checkpoint_path = self.checkpoints[-1]["path"]
                    logger.info("Restoring from most recent checkpoint")
                else:
                    checkpoint_path = None  # Will use best checkpoint
                    logger.info("No recent checkpoints, using best checkpoint")

            # Load checkpoint
            success = self.load_checkpoint(model, optimizer, checkpoint_path)

            if success:
                self.total_restores += 1

                # Log restoration details
                logger.info(
                    f"Model restored from instability: "
                    f"epoch={current_epoch}, events={len(events)}, "
                    f"total_restores={self.total_restores}"
                )

                # Log event details
                for event in events:
                    logger.warning(
                        f"Instability event: {event.event_type.value}, "
                        f"severity={event.severity}, value={event.value:.6f}"
                    )

            return success

        except Exception as e:
            logger.error(f"Failed to restore from instability: {e}")
            return False

    def should_save_checkpoint(self, epoch: int) -> bool:
        """Check if checkpoint should be saved this epoch."""
        return (
            epoch % self.save_frequency == 0
            or epoch == 1
            or epoch - self.last_save_epoch >= self.save_frequency
        )

    def should_create_backup(self, epoch: int) -> bool:
        """Check if backup should be created this epoch."""
        return (
            epoch % self.backup_frequency == 0
            or epoch - self.last_backup_epoch >= self.backup_frequency
        )

    def create_backup(
        self, model: keras.Model, optimizer: keras.optimizers.Optimizer, epoch: int
    ) -> bool:
        """Create full backup of model and training state."""
        try:
            backup_dir = self.checkpoint_dir / "backups"
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"backup_epoch_{epoch:04d}_{timestamp}.h5"

            # Save full model (not just weights)
            model.save(backup_path)

            # Save optimizer state
            optimizer_path = backup_path.with_suffix(".optimizer.pkl")
            with open(optimizer_path, "wb") as f:
                pickle.dump(optimizer.get_config(), f)

            # Save backup metadata
            metadata_path = backup_path.with_suffix(".json")
            backup_metadata = {
                "epoch": epoch,
                "timestamp": datetime.now().isoformat(),
                "backup_type": "full",
                "model_size": backup_path.stat().st_size,
                "checkpoint_count": len(self.checkpoints),
                "total_saves": self.total_saves,
                "total_loads": self.total_loads,
                "total_restores": self.total_restores,
            }

            with open(metadata_path, "w") as f:
                json.dump(backup_metadata, f, indent=2)

            self.last_backup_epoch = epoch

            logger.info(f"Backup created: {backup_path.name}, epoch={epoch}")
            return True

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False

    def _cleanup_old_checkpoints(self):
        """Remove old checkpoints to stay within max_checkpoints limit."""
        if len(self.checkpoints) <= self.max_checkpoints:
            return

        # Sort by epoch (oldest first)
        self.checkpoints.sort(key=lambda x: x["epoch"])

        # Remove oldest checkpoints
        while len(self.checkpoints) > self.max_checkpoints:
            old_checkpoint = self.checkpoints.pop(0)

            try:
                # Remove files
                if old_checkpoint["path"].exists():
                    old_checkpoint["path"].unlink()
                if old_checkpoint["metadata_path"].exists():
                    old_checkpoint["metadata_path"].unlink()

                logger.debug(f"Removed old checkpoint: {old_checkpoint['path'].name}")
            except Exception as e:
                logger.warning(f"Failed to remove old checkpoint: {e}")

    def get_checkpoint_list(self) -> List[Dict[str, Any]]:
        """Get list of available checkpoints."""
        return [
            {
                "epoch": cp["epoch"],
                "type": cp["type"],
                "timestamp": cp["timestamp"].isoformat(),
                "size": cp["size"],
                "metrics": cp["metrics"],
                "path": str(cp["path"]),
            }
            for cp in self.checkpoints
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get checkpoint manager statistics."""
        return {
            "total_checkpoints": len(self.checkpoints),
            "total_saves": self.total_saves,
            "total_loads": self.total_loads,
            "total_restores": self.total_restores,
            "last_save_epoch": self.last_save_epoch,
            "last_backup_epoch": self.last_backup_epoch,
            "best_checkpoint": (
                {
                    "epoch": (
                        self.best_checkpoint["epoch"] if self.best_checkpoint else None
                    ),
                    "score": self.best_score,
                    "metric": self.best_metric,
                }
                if self.best_checkpoint
                else None
            ),
            "checkpoint_dir": str(self.checkpoint_dir),
            "max_checkpoints": self.max_checkpoints,
            "save_frequency": self.save_frequency,
        }
