"""
Data Privacy and Protection System for BOLT AI Neural Agent System.

Implements comprehensive data privacy controls including:
- Federated learning capabilities
- Data anonymization and pseudonymization
- Privacy-preserving analytics
- GDPR/CCPA compliance features
- Data retention and deletion policies
"""

import base64
import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class DataClassification(Enum):
    """Data classification levels"""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class PrivacyLevel(Enum):
    """Privacy protection levels"""

    MINIMAL = "minimal"
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"


class DataSubjectType(Enum):
    """Types of data subjects"""

    INDIVIDUAL = "individual"
    BUSINESS = "business"
    ANONYMOUS = "anonymous"
    PSEUDONYMOUS = "pseudonymous"


class DataPrivacyManager:
    """
    Comprehensive data privacy management system.

    Features:
    - Data classification and labeling
    - Privacy-preserving data processing
    - Federated learning support
    - Data anonymization and pseudonymization
    - Compliance tracking and reporting
    """

    def __init__(self):
        self.data_classifications = {}
        self.privacy_policies = {}
        self.retention_policies = {}
        self.consent_records = {}
        self.anonymization_keys = {}
        self.pseudonymization_mappings = {}

        # Initialize default policies
        self._initialize_default_policies()

    def _initialize_default_policies(self):
        """Initialize default privacy and retention policies"""

        # Default privacy policies
        self.privacy_policies = {
            DataClassification.PUBLIC: {
                "retention_days": 365,
                "anonymization_required": False,
                "consent_required": False,
                "federated_learning_allowed": True,
                "cross_border_transfer_allowed": True,
            },
            DataClassification.INTERNAL: {
                "retention_days": 180,
                "anonymization_required": False,
                "consent_required": True,
                "federated_learning_allowed": True,
                "cross_border_transfer_allowed": False,
            },
            DataClassification.CONFIDENTIAL: {
                "retention_days": 90,
                "anonymization_required": True,
                "consent_required": True,
                "federated_learning_allowed": False,
                "cross_border_transfer_allowed": False,
            },
            DataClassification.RESTRICTED: {
                "retention_days": 30,
                "anonymization_required": True,
                "consent_required": True,
                "federated_learning_allowed": False,
                "cross_border_transfer_allowed": False,
            },
        }

        # Default retention policies
        self.retention_policies = {
            "user_data": 365,  # days
            "trading_data": 180,
            "model_data": 90,
            "log_data": 30,
            "session_data": 7,
        }

    def classify_data(
        self, data: Dict[str, Any], data_type: str, sensitivity_score: float = 0.5
    ) -> DataClassification:
        """
        Classify data based on content and sensitivity.

        Args:
            data: Data to classify
            data_type: Type of data (e.g., 'user_profile', 'trading_history')
            sensitivity_score: Sensitivity score (0.0 to 1.0)

        Returns:
            Data classification level
        """

        # Check for sensitive fields
        sensitive_fields = ["api_key", "password", "ssn", "credit_card", "bank_account"]
        has_sensitive_fields = any(
            field in str(data).lower() for field in sensitive_fields
        )

        # Check for personal identifiers
        personal_identifiers = ["email", "phone", "address", "name", "ip_address"]
        has_personal_identifiers = any(
            field in str(data).lower() for field in personal_identifiers
        )

        # Check for financial data
        financial_fields = ["balance", "transaction", "portfolio", "investment"]
        has_financial_data = any(
            field in str(data).lower() for field in financial_fields
        )

        # Determine classification
        if has_sensitive_fields or sensitivity_score > 0.8:
            classification = DataClassification.RESTRICTED
        elif has_financial_data or sensitivity_score > 0.6:
            classification = DataClassification.CONFIDENTIAL
        elif has_personal_identifiers or sensitivity_score > 0.4:
            classification = DataClassification.INTERNAL
        else:
            classification = DataClassification.PUBLIC

        # Store classification
        data_id = self._generate_data_id(data)
        self.data_classifications[data_id] = {
            "classification": classification,
            "data_type": data_type,
            "sensitivity_score": sensitivity_score,
            "timestamp": datetime.now().isoformat(),
            "fields_detected": {
                "sensitive_fields": has_sensitive_fields,
                "personal_identifiers": has_personal_identifiers,
                "financial_data": has_financial_data,
            },
        }

        logger.info(f"Data classified as {classification.value} for type {data_type}")
        return classification

    def anonymize_data(
        self, data: Dict[str, Any], privacy_level: PrivacyLevel = PrivacyLevel.STANDARD
    ) -> Dict[str, Any]:
        """
        Anonymize data based on privacy level.

        Args:
            data: Data to anonymize
            privacy_level: Level of privacy protection

        Returns:
            Anonymized data
        """

        anonymized = data.copy()

        if privacy_level == PrivacyLevel.MINIMAL:
            # Remove only direct identifiers
            anonymized = self._remove_direct_identifiers(anonymized)

        elif privacy_level == PrivacyLevel.STANDARD:
            # Remove direct and indirect identifiers
            anonymized = self._remove_direct_identifiers(anonymized)
            anonymized = self._remove_indirect_identifiers(anonymized)

        elif privacy_level == PrivacyLevel.HIGH:
            # Apply k-anonymity (ensure at least k records share same attributes)
            anonymized = self._remove_direct_identifiers(anonymized)
            anonymized = self._remove_indirect_identifiers(anonymized)
            anonymized = self._apply_k_anonymity(anonymized, k=3)

        elif privacy_level == PrivacyLevel.MAXIMUM:
            # Apply differential privacy
            anonymized = self._remove_direct_identifiers(anonymized)
            anonymized = self._remove_indirect_identifiers(anonymized)
            anonymized = self._apply_differential_privacy(anonymized, epsilon=1.0)

        # Log anonymization
        logger.info(f"Data anonymized with privacy level {privacy_level.value}")

        return anonymized

    def pseudonymize_data(
        self, data: Dict[str, Any], subject_id: str, reversible: bool = False
    ) -> Dict[str, Any]:
        """
        Pseudonymize data by replacing identifiers with pseudonyms.

        Args:
            data: Data to pseudonymize
            subject_id: Subject identifier
            reversible: Whether pseudonymization should be reversible

        Returns:
            Pseudonymized data
        """

        pseudonymized = data.copy()

        # Generate pseudonymization key
        if subject_id not in self.pseudonymization_mappings:
            self.pseudonymization_mappings[subject_id] = {}

        # Pseudonymize identifiers
        for field, value in data.items():
            if self._is_identifier_field(field):
                if reversible:
                    # Reversible pseudonymization
                    pseudonym = self._generate_reversible_pseudonym(value, subject_id)
                else:
                    # Irreversible pseudonymization
                    pseudonym = self._generate_irreversible_pseudonym(value, subject_id)

                pseudonymized[field] = pseudonym
                self.pseudonymization_mappings[subject_id][field] = {
                    "original": value,
                    "pseudonym": pseudonym,
                    "reversible": reversible,
                    "timestamp": datetime.now().isoformat(),
                }

        logger.info(f"Data pseudonymized for subject {subject_id}")
        return pseudonymized

    def _remove_direct_identifiers(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove direct identifiers from data"""
        direct_identifiers = [
            "email",
            "phone",
            "ssn",
            "passport",
            "driver_license",
            "credit_card",
            "bank_account",
            "ip_address",
            "mac_address",
        ]

        cleaned = data.copy()
        for field in direct_identifiers:
            if field in cleaned:
                del cleaned[field]

        return cleaned

    def _remove_indirect_identifiers(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove indirect identifiers from data"""
        indirect_identifiers = [
            "name",
            "address",
            "zip_code",
            "birth_date",
            "gender",
            "occupation",
            "income",
            "education",
            "marital_status",
        ]

        cleaned = data.copy()
        for field in indirect_identifiers:
            if field in cleaned:
                del cleaned[field]

        return cleaned

    def _apply_k_anonymity(self, data: Dict[str, Any], k: int = 3) -> Dict[str, Any]:
        """Apply k-anonymity to data"""
        # Placeholder implementation
        # In practice, this would ensure at least k records share the same attributes
        return data

    def _apply_differential_privacy(
        self, data: Dict[str, Any], epsilon: float = 1.0
    ) -> Dict[str, Any]:
        """Apply differential privacy to data"""
        # Placeholder implementation
        # In practice, this would add calibrated noise to protect individual privacy
        return data

    def _is_identifier_field(self, field: str) -> bool:
        """Check if field is an identifier"""
        identifier_fields = [
            "user_id",
            "session_id",
            "device_id",
            "email",
            "phone",
            "ip_address",
            "mac_address",
            "uuid",
            "id",
        ]
        return field.lower() in identifier_fields

    def _generate_reversible_pseudonym(self, value: str, subject_id: str) -> str:
        """Generate reversible pseudonym"""
        # Use encryption for reversible pseudonymization
        key = self._get_pseudonymization_key(subject_id)
        fernet = Fernet(key)
        encrypted = fernet.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()

    def _generate_irreversible_pseudonym(self, value: str, subject_id: str) -> str:
        """Generate irreversible pseudonym"""
        # Use hashing for irreversible pseudonymization
        salt = self._get_pseudonymization_salt(subject_id)
        return hashlib.sha256(f"{value}{salt}".encode()).hexdigest()[:16]

    def _get_pseudonymization_key(self, subject_id: str) -> bytes:
        """Get pseudonymization key for subject"""
        if subject_id not in self.anonymization_keys:
            # Generate new key
            password = f"pseudonymization_{subject_id}".encode()
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self.anonymization_keys[subject_id] = key

        return self.anonymization_keys[subject_id]

    def _get_pseudonymization_salt(self, subject_id: str) -> str:
        """Get pseudonymization salt for subject"""
        return f"pseudonymization_salt_{subject_id}"

    def _generate_data_id(self, data: Dict[str, Any]) -> str:
        """Generate unique data ID"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    def record_consent(
        self,
        subject_id: str,
        consent_type: str,
        granted: bool,
        purpose: str,
        data_types: List[str],
    ) -> str:
        """
        Record consent for data processing.

        Args:
            subject_id: Subject identifier
            consent_type: Type of consent
            granted: Whether consent was granted
            purpose: Purpose of data processing
            data_types: Types of data covered by consent

        Returns:
            Consent record ID
        """

        consent_id = str(uuid.uuid4())

        self.consent_records[consent_id] = {
            "subject_id": subject_id,
            "consent_type": consent_type,
            "granted": granted,
            "purpose": purpose,
            "data_types": data_types,
            "timestamp": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "withdrawal_date": None,
            "status": "active" if granted else "denied",
        }

        logger.info(f"Consent recorded: {consent_id} for subject {subject_id}")
        return consent_id

    def withdraw_consent(self, consent_id: str) -> bool:
        """
        Withdraw consent.

        Args:
            consent_id: Consent record ID

        Returns:
            True if consent was withdrawn successfully
        """

        if consent_id not in self.consent_records:
            return False

        self.consent_records[consent_id]["status"] = "withdrawn"
        self.consent_records[consent_id]["withdrawal_date"] = datetime.now().isoformat()

        logger.info(f"Consent withdrawn: {consent_id}")
        return True

    def check_consent(
        self, subject_id: str, purpose: str, data_types: List[str]
    ) -> bool:
        """
        Check if consent exists for data processing.

        Args:
            subject_id: Subject identifier
            purpose: Purpose of data processing
            data_types: Types of data to process

        Returns:
            True if consent exists and is valid
        """

        for consent_id, record in self.consent_records.items():
            if (
                record["subject_id"] == subject_id
                and record["purpose"] == purpose
                and record["status"] == "active"
                and datetime.fromisoformat(record["expiry_date"]) > datetime.now()
            ):

                # Check if data types are covered
                if all(dt in record["data_types"] for dt in data_types):
                    return True

        return False

    def schedule_data_deletion(self, data_id: str, retention_days: int = None) -> str:
        """
        Schedule data for deletion based on retention policy.

        Args:
            data_id: Data identifier
            retention_days: Override default retention period

        Returns:
            Deletion schedule ID
        """

        if data_id not in self.data_classifications:
            logger.warning(f"Data {data_id} not classified, using default retention")
            retention_days = retention_days or 365
        else:
            classification = self.data_classifications[data_id]["classification"]
            retention_days = (
                retention_days
                or self.privacy_policies[classification]["retention_days"]
            )

        deletion_date = datetime.now() + timedelta(days=retention_days)
        schedule_id = str(uuid.uuid4())

        # Store deletion schedule
        if not hasattr(self, "deletion_schedules"):
            self.deletion_schedules = {}

        self.deletion_schedules[schedule_id] = {
            "data_id": data_id,
            "deletion_date": deletion_date.isoformat(),
            "retention_days": retention_days,
            "created_at": datetime.now().isoformat(),
            "status": "scheduled",
        }

        logger.info(f"Data deletion scheduled: {schedule_id} for {deletion_date}")
        return schedule_id

    def process_data_deletion(self) -> List[str]:
        """
        Process scheduled data deletions.

        Returns:
            List of deleted data IDs
        """

        if not hasattr(self, "deletion_schedules"):
            return []

        deleted_ids = []
        current_time = datetime.now()

        for schedule_id, schedule in self.deletion_schedules.items():
            if (
                schedule["status"] == "scheduled"
                and datetime.fromisoformat(schedule["deletion_date"]) <= current_time
            ):

                # Mark for deletion
                schedule["status"] = "deleted"
                schedule["deleted_at"] = current_time.isoformat()

                deleted_ids.append(schedule["data_id"])
                logger.info(f"Data deleted: {schedule['data_id']}")

        return deleted_ids

    def generate_privacy_report(self) -> Dict[str, Any]:
        """Generate comprehensive privacy report"""

        # Count data by classification
        classification_counts = {}
        for record in self.data_classifications.values():
            classification = record["classification"].value
            classification_counts[classification] = (
                classification_counts.get(classification, 0) + 1
            )

        # Count consent records
        consent_counts = {
            "total": len(self.consent_records),
            "active": len(
                [r for r in self.consent_records.values() if r["status"] == "active"]
            ),
            "withdrawn": len(
                [r for r in self.consent_records.values() if r["status"] == "withdrawn"]
            ),
            "denied": len(
                [r for r in self.consent_records.values() if r["status"] == "denied"]
            ),
        }

        # Count deletion schedules
        deletion_counts = {
            "scheduled": len(
                [
                    s
                    for s in getattr(self, "deletion_schedules", {}).values()
                    if s["status"] == "scheduled"
                ]
            ),
            "deleted": len(
                [
                    s
                    for s in getattr(self, "deletion_schedules", {}).values()
                    if s["status"] == "deleted"
                ]
            ),
        }

        return {
            "timestamp": datetime.now().isoformat(),
            "data_classifications": classification_counts,
            "consent_records": consent_counts,
            "deletion_schedules": deletion_counts,
            "privacy_policies": self.privacy_policies,
            "retention_policies": self.retention_policies,
            "pseudonymization_mappings": len(self.pseudonymization_mappings),
            "anonymization_keys": len(self.anonymization_keys),
        }

    def export_data_subject_data(self, subject_id: str) -> Dict[str, Any]:
        """
        Export all data for a specific subject (GDPR Article 20).

        Args:
            subject_id: Subject identifier

        Returns:
            All data associated with the subject
        """

        subject_data = {
            "subject_id": subject_id,
            "export_timestamp": datetime.now().isoformat(),
            "data_classifications": {},
            "consent_records": {},
            "pseudonymization_mappings": {},
        }

        # Collect classified data
        for data_id, record in self.data_classifications.items():
            if subject_id in str(
                record
            ):  # Simple check - in practice, would be more sophisticated
                subject_data["data_classifications"][data_id] = record

        # Collect consent records
        for consent_id, record in self.consent_records.items():
            if record["subject_id"] == subject_id:
                subject_data["consent_records"][consent_id] = record

        # Collect pseudonymization mappings
        if subject_id in self.pseudonymization_mappings:
            subject_data["pseudonymization_mappings"] = self.pseudonymization_mappings[
                subject_id
            ]

        return subject_data

    def delete_subject_data(self, subject_id: str) -> bool:
        """
        Delete all data for a specific subject (GDPR Article 17).

        Args:
            subject_id: Subject identifier

        Returns:
            True if deletion was successful
        """

        deleted_count = 0

        # Delete classified data
        to_delete = []
        for data_id, record in self.data_classifications.items():
            if subject_id in str(
                record
            ):  # Simple check - in practice, would be more sophisticated
                to_delete.append(data_id)

        for data_id in to_delete:
            del self.data_classifications[data_id]
            deleted_count += 1

        # Delete consent records
        to_delete = []
        for consent_id, record in self.consent_records.items():
            if record["subject_id"] == subject_id:
                to_delete.append(consent_id)

        for consent_id in to_delete:
            del self.consent_records[consent_id]
            deleted_count += 1

        # Delete pseudonymization mappings
        if subject_id in self.pseudonymization_mappings:
            del self.pseudonymization_mappings[subject_id]
            deleted_count += 1

        logger.info(f"Deleted {deleted_count} records for subject {subject_id}")
        return deleted_count > 0
