"""
Legal compliance tests for the BOLT AI Neural Agent System
"""

import json
import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from backend.legal.compliance import ComplianceManager
from backend.legal.consent import ConsentManager
from backend.legal.disclaimers import DisclaimerManager
from backend.legal.privacy import PrivacyManager


class TestLegalCompliance:
    """Legal compliance test cases"""

    @pytest.fixture
    def compliance_manager(self):
        """Create compliance manager for testing."""
        return ComplianceManager()

    @pytest.fixture
    def disclaimer_manager(self):
        """Create disclaimer manager for testing."""
        return DisclaimerManager()

    @pytest.fixture
    def consent_manager(self):
        """Create consent manager for testing."""
        return ConsentManager()

    @pytest.fixture
    def privacy_manager(self):
        """Create privacy manager for testing."""
        return PrivacyManager()

    def test_disclaimer_acceptance_tracking(self, disclaimer_manager):
        """Test disclaimer acceptance tracking."""
        # Test initial state
        assert not disclaimer_manager.is_disclaimer_accepted()

        # Test disclaimer acceptance
        disclaimer_manager.accept_disclaimer("1.0", "2023-12-01T12:00:00Z")

        assert disclaimer_manager.is_disclaimer_accepted()
        assert disclaimer_manager.get_disclaimer_version() == "1.0"
        assert disclaimer_manager.get_disclaimer_date() == "2023-12-01T12:00:00Z"

        # Test disclaimer rejection
        disclaimer_manager.reject_disclaimer()

        assert not disclaimer_manager.is_disclaimer_accepted()

    def test_disclaimer_version_management(self, disclaimer_manager):
        """Test disclaimer version management."""
        # Test version comparison
        disclaimer_manager.accept_disclaimer("1.0", "2023-12-01T12:00:00Z")

        assert disclaimer_manager.is_version_accepted("1.0")
        assert not disclaimer_manager.is_version_accepted("2.0")

        # Test version update
        disclaimer_manager.accept_disclaimer("2.0", "2023-12-02T12:00:00Z")

        assert disclaimer_manager.is_version_accepted("2.0")
        assert not disclaimer_manager.is_version_accepted("1.0")

    def test_consent_management(self, consent_manager):
        """Test consent management functionality."""
        # Test consent tracking
        feature = "trading"
        description = "Execute cryptocurrency trades"
        risk_level = "high"

        assert not consent_manager.has_consent(feature)

        # Test consent granting
        consent_manager.grant_consent(feature, description, risk_level)

        assert consent_manager.has_consent(feature)
        assert consent_manager.get_consent_details(feature)["risk_level"] == "high"

        # Test consent revocation
        consent_manager.revoke_consent(feature)

        assert not consent_manager.has_consent(feature)

    def test_consent_expiration(self, consent_manager):
        """Test consent expiration handling."""
        feature = "data_collection"
        description = "Collect user data for analysis"
        risk_level = "medium"

        # Grant consent with short expiration
        consent_manager.grant_consent(
            feature, description, risk_level, expires_in=1
        )  # 1 second

        assert consent_manager.has_consent(feature)

        # Wait for expiration
        import time

        time.sleep(2)

        assert not consent_manager.has_consent(feature)

    def test_privacy_data_collection(self, privacy_manager):
        """Test privacy data collection compliance."""
        # Test data collection consent
        assert not privacy_manager.can_collect_data("user_123")

        privacy_manager.grant_data_collection_consent("user_123")

        assert privacy_manager.can_collect_data("user_123")

        # Test data collection types
        assert privacy_manager.can_collect_data_type("user_123", "market_data")
        assert privacy_manager.can_collect_data_type("user_123", "trading_history")

        # Test data collection revocation
        privacy_manager.revoke_data_collection_consent("user_123")

        assert not privacy_manager.can_collect_data("user_123")

    def test_privacy_data_retention(self, privacy_manager):
        """Test privacy data retention compliance."""
        # Test data retention policies
        retention_policy = privacy_manager.get_retention_policy("market_data")

        assert retention_policy["max_retention_days"] == 365
        assert retention_policy["auto_delete"] is True

        # Test data deletion
        privacy_manager.schedule_data_deletion("user_123", "market_data", days=30)

        assert privacy_manager.is_deletion_scheduled("user_123", "market_data")

    def test_privacy_data_export(self, privacy_manager):
        """Test privacy data export compliance."""
        # Test data export request
        export_request = privacy_manager.create_export_request("user_123")

        assert export_request["request_id"] is not None
        assert export_request["user_id"] == "user_123"
        assert export_request["status"] == "pending"

        # Test data export generation
        export_data = privacy_manager.generate_export_data("user_123")

        assert "personal_data" in export_data
        assert "market_data" in export_data
        assert "trading_history" in export_data

    def test_privacy_data_anonymization(self, privacy_manager):
        """Test privacy data anonymization."""
        # Test data anonymization
        sensitive_data = {
            "user_id": "user_123",
            "email": "user@example.com",
            "trading_history": [{"symbol": "BTC", "amount": 1000}],
        }

        anonymized_data = privacy_manager.anonymize_data(sensitive_data)

        assert anonymized_data["user_id"] != "user_123"
        assert anonymized_data["email"] != "user@example.com"
        assert (
            anonymized_data["trading_history"] == sensitive_data["trading_history"]
        )  # Trading data preserved

    def test_compliance_audit_trail(self, compliance_manager):
        """Test compliance audit trail."""
        # Test audit event creation
        audit_event = {
            "event_type": "disclaimer_accepted",
            "user_id": "user_123",
            "timestamp": "2023-12-01T12:00:00Z",
            "details": {"version": "1.0"},
        }

        compliance_manager.log_audit_event(audit_event)

        # Test audit trail retrieval
        audit_trail = compliance_manager.get_audit_trail("user_123")

        assert len(audit_trail) > 0
        assert audit_trail[0]["event_type"] == "disclaimer_accepted"

    def test_compliance_reporting(self, compliance_manager):
        """Test compliance reporting."""
        # Test compliance report generation
        report = compliance_manager.generate_compliance_report()

        assert "disclaimer_compliance" in report
        assert "consent_compliance" in report
        assert "privacy_compliance" in report
        assert "audit_trail" in report

        # Test compliance metrics
        metrics = compliance_manager.get_compliance_metrics()

        assert "disclaimer_acceptance_rate" in metrics
        assert "consent_grant_rate" in metrics
        assert "privacy_compliance_score" in metrics

    def test_regulatory_compliance(self, compliance_manager):
        """Test regulatory compliance checks."""
        # Test GDPR compliance
        gdpr_compliance = compliance_manager.check_gdpr_compliance()

        assert gdpr_compliance["data_protection"] is True
        assert gdpr_compliance["consent_management"] is True
        assert gdpr_compliance["data_portability"] is True
        assert gdpr_compliance["right_to_deletion"] is True

        # Test CCPA compliance
        ccpa_compliance = compliance_manager.check_ccpa_compliance()

        assert ccpa_compliance["data_transparency"] is True
        assert ccpa_compliance["opt_out_rights"] is True
        assert ccpa_compliance["data_deletion"] is True

    def test_legal_disclaimer_content(self, disclaimer_manager):
        """Test legal disclaimer content."""
        # Test disclaimer content retrieval
        disclaimer_content = disclaimer_manager.get_disclaimer_content("1.0")

        assert "Not Financial Advice" in disclaimer_content
        assert "High Risk Warning" in disclaimer_content
        assert "AI Limitations" in disclaimer_content
        assert "Legal Responsibility" in disclaimer_content

        # Test disclaimer validation
        assert disclaimer_manager.validate_disclaimer_content(disclaimer_content)

    def test_legal_disclaimer_localization(self, disclaimer_manager):
        """Test legal disclaimer localization."""
        # Test disclaimer in different languages
        english_disclaimer = disclaimer_manager.get_disclaimer_content("1.0", "en")
        spanish_disclaimer = disclaimer_manager.get_disclaimer_content("1.0", "es")

        assert "Not Financial Advice" in english_disclaimer
        assert "No es asesoramiento financiero" in spanish_disclaimer

    def test_consent_granularity(self, consent_manager):
        """Test consent granularity."""
        # Test granular consent levels
        consent_manager.grant_consent("trading", "Execute trades", "high")
        consent_manager.grant_consent("data_collection", "Collect data", "medium")
        consent_manager.grant_consent("notifications", "Send notifications", "low")

        assert consent_manager.has_consent("trading")
        assert consent_manager.has_consent("data_collection")
        assert consent_manager.has_consent("notifications")

        # Test partial consent revocation
        consent_manager.revoke_consent("trading")

        assert not consent_manager.has_consent("trading")
        assert consent_manager.has_consent("data_collection")
        assert consent_manager.has_consent("notifications")

    def test_privacy_data_minimization(self, privacy_manager):
        """Test privacy data minimization."""
        # Test data minimization
        user_data = {
            "user_id": "user_123",
            "email": "user@example.com",
            "phone": "123-456-7890",
            "address": "123 Main St",
            "trading_preferences": {"risk_tolerance": "medium"},
        }

        minimized_data = privacy_manager.minimize_data(user_data, "trading_analysis")

        # Only relevant data should be retained
        assert "user_id" in minimized_data
        assert "trading_preferences" in minimized_data
        assert "email" not in minimized_data
        assert "phone" not in minimized_data
        assert "address" not in minimized_data

    def test_privacy_data_purpose_limitation(self, privacy_manager):
        """Test privacy data purpose limitation."""
        # Test purpose limitation
        data_purpose = "trading_analysis"

        assert privacy_manager.can_use_data_for_purpose("user_123", data_purpose)

        # Test purpose change
        new_purpose = "marketing"

        assert not privacy_manager.can_use_data_for_purpose("user_123", new_purpose)

        # Grant consent for new purpose
        privacy_manager.grant_purpose_consent("user_123", new_purpose)

        assert privacy_manager.can_use_data_for_purpose("user_123", new_purpose)

    def test_compliance_monitoring(self, compliance_manager):
        """Test compliance monitoring."""
        # Test compliance monitoring setup
        compliance_manager.setup_monitoring()

        assert compliance_manager.is_monitoring_active()

        # Test compliance alerts
        compliance_manager.trigger_compliance_alert("disclaimer_expired", "user_123")

        alerts = compliance_manager.get_compliance_alerts()

        assert len(alerts) > 0
        assert alerts[0]["alert_type"] == "disclaimer_expired"
        assert alerts[0]["user_id"] == "user_123"

    def test_legal_document_versioning(self, disclaimer_manager):
        """Test legal document versioning."""
        # Test document versioning
        disclaimer_manager.create_version("2.0", "Updated disclaimer content")

        assert disclaimer_manager.version_exists("2.0")
        assert disclaimer_manager.get_latest_version() == "2.0"

        # Test version comparison
        assert disclaimer_manager.compare_versions("1.0", "2.0")["changes"] is not None

        # Test version rollback
        disclaimer_manager.rollback_to_version("1.0")

        assert disclaimer_manager.get_latest_version() == "1.0"

    def test_consent_withdrawal_process(self, consent_manager):
        """Test consent withdrawal process."""
        # Test consent withdrawal
        feature = "trading"
        consent_manager.grant_consent(feature, "Execute trades", "high")

        assert consent_manager.has_consent(feature)

        # Test withdrawal process
        withdrawal_request = consent_manager.create_withdrawal_request(
            feature, "user_123"
        )

        assert withdrawal_request["request_id"] is not None
        assert withdrawal_request["status"] == "pending"

        # Test withdrawal approval
        consent_manager.approve_withdrawal(withdrawal_request["request_id"])

        assert not consent_manager.has_consent(feature)

    def test_privacy_impact_assessment(self, privacy_manager):
        """Test privacy impact assessment."""
        # Test PIA creation
        pia = privacy_manager.create_privacy_impact_assessment("new_feature")

        assert pia["feature_name"] == "new_feature"
        assert pia["risk_level"] is not None
        assert pia["mitigation_measures"] is not None

        # Test PIA approval
        privacy_manager.approve_pia(pia["pia_id"])

        assert privacy_manager.is_pia_approved(pia["pia_id"])

    def test_legal_compliance_integration(
        self, compliance_manager, disclaimer_manager, consent_manager, privacy_manager
    ):
        """Test integrated legal compliance system."""
        # Test full compliance workflow
        user_id = "user_123"

        # Step 1: Disclaimer acceptance
        disclaimer_manager.accept_disclaimer("1.0", "2023-12-01T12:00:00Z")

        # Step 2: Consent granting
        consent_manager.grant_consent("trading", "Execute trades", "high")
        consent_manager.grant_consent("data_collection", "Collect data", "medium")

        # Step 3: Privacy consent
        privacy_manager.grant_data_collection_consent(user_id)

        # Step 4: Compliance check
        compliance_status = compliance_manager.check_user_compliance(user_id)

        assert compliance_status["disclaimer_accepted"] is True
        assert compliance_status["consent_granted"] is True
        assert compliance_status["privacy_compliant"] is True
        assert compliance_status["overall_compliant"] is True

    def test_legal_compliance_edge_cases(self, compliance_manager):
        """Test legal compliance edge cases."""
        # Test compliance with missing user
        compliance_status = compliance_manager.check_user_compliance("nonexistent_user")

        assert compliance_status["disclaimer_accepted"] is False
        assert compliance_status["consent_granted"] is False
        assert compliance_status["privacy_compliant"] is False
        assert compliance_status["overall_compliant"] is False

        # Test compliance with expired consents
        import time

        time.sleep(1)  # Wait for expiration

        compliance_status = compliance_manager.check_user_compliance("user_123")

        # Should handle expired consents gracefully
        assert compliance_status is not None

    def test_legal_compliance_performance(self, compliance_manager):
        """Test legal compliance performance."""
        import time

        # Test compliance check performance
        start_time = time.time()

        for i in range(100):
            compliance_manager.check_user_compliance(f"user_{i}")

        end_time = time.time()
        avg_time = (end_time - start_time) / 100

        # Should be fast (under 0.01 seconds per check)
        assert (
            avg_time < 0.01
        ), f"Compliance check took {avg_time:.3f}s, expected < 0.01s"

    def test_legal_compliance_data_integrity(self, compliance_manager):
        """Test legal compliance data integrity."""
        # Test data integrity checks
        integrity_check = compliance_manager.check_data_integrity()

        assert integrity_check["disclaimer_data"] is True
        assert integrity_check["consent_data"] is True
        assert integrity_check["privacy_data"] is True
        assert integrity_check["audit_trail"] is True

        # Test data corruption detection
        corrupted_data = {"invalid": "data"}

        assert not compliance_manager.validate_compliance_data(corrupted_data)

    def test_legal_compliance_backup_recovery(self, compliance_manager):
        """Test legal compliance backup and recovery."""
        # Test compliance data backup
        backup_data = compliance_manager.create_backup()

        assert backup_data["disclaimers"] is not None
        assert backup_data["consents"] is not None
        assert backup_data["privacy_settings"] is not None
        assert backup_data["audit_trail"] is not None

        # Test compliance data recovery
        recovery_result = compliance_manager.restore_backup(backup_data)

        assert recovery_result["success"] is True
        assert recovery_result["restored_items"] > 0
