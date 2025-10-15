"""
Security tests for the BOLT AI Neural Agent System
"""

import base64
import hashlib
import os
import secrets
import sqlite3
import tempfile
from unittest.mock import Mock, patch

import pytest
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from backend.config import Settings
from backend.db.sqlite_manager import SQLiteManager
from backend.security.credentials import CredentialManager
from backend.security.encryption import EncryptionManager


class TestSecurity:
    """Security test cases"""

    @pytest.fixture
    def test_settings(self):
        """Create test settings."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        settings = Settings(
            DATABASE_URL=f"sqlite:///{db_path}",
            SQLITE_DB_PATH=db_path,
            SQLITE_ENCRYPTION_KEY="test_key_32_chars_long_12345",
            REDIS_URL="redis://localhost:6379/1",
            SECRET_KEY="test_secret_key_32_chars_long_12345",
            ENVIRONMENT="test",
        )

        yield settings

        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

    @pytest.fixture
    def encryption_manager(self):
        """Create encryption manager for testing."""
        return EncryptionManager()

    @pytest.fixture
    def credential_manager(self):
        """Create credential manager for testing."""
        return CredentialManager()

    def test_sqlite_encryption(self, test_settings):
        """Test SQLite database encryption."""
        manager = SQLiteManager(
            test_settings.SQLITE_DB_PATH, test_settings.SQLITE_ENCRYPTION_KEY
        )
        manager.initialize_database()

        # Test that database is encrypted
        # Read raw database file
        with open(test_settings.SQLITE_DB_PATH, "rb") as f:
            raw_data = f.read()

        # Encrypted data should not contain readable SQL
        assert b"CREATE TABLE" not in raw_data
        assert b"INSERT INTO" not in raw_data

        # Test that we can still access data through manager
        conn = manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        assert len(tables) > 0

    def test_encryption_manager(self, encryption_manager):
        """Test encryption manager functionality."""
        # Test data encryption/decryption
        test_data = "Sensitive test data"

        encrypted_data = encryption_manager.encrypt(test_data)
        decrypted_data = encryption_manager.decrypt(encrypted_data)

        assert encrypted_data != test_data
        assert decrypted_data == test_data

        # Test that encrypted data is different each time
        encrypted_data2 = encryption_manager.encrypt(test_data)
        assert encrypted_data != encrypted_data2

    def test_encryption_manager_large_data(self, encryption_manager):
        """Test encryption manager with large data."""
        # Test with large data
        large_data = "x" * 10000

        encrypted_data = encryption_manager.encrypt(large_data)
        decrypted_data = encryption_manager.decrypt(encrypted_data)

        assert decrypted_data == large_data

    def test_encryption_manager_binary_data(self, encryption_manager):
        """Test encryption manager with binary data."""
        # Test with binary data
        binary_data = os.urandom(1000)

        encrypted_data = encryption_manager.encrypt(binary_data)
        decrypted_data = encryption_manager.decrypt(encrypted_data)

        assert decrypted_data == binary_data

    def test_credential_manager(self, credential_manager):
        """Test credential manager functionality."""
        # Test storing credentials
        service_name = "test_service"
        username = "test_user"
        password = "test_password"

        credential_manager.store_credential(service_name, username, password)

        # Test retrieving credentials
        retrieved_username, retrieved_password = credential_manager.get_credential(
            service_name
        )

        assert retrieved_username == username
        assert retrieved_password == password

        # Test updating credentials
        new_password = "new_password"
        credential_manager.store_credential(service_name, username, new_password)

        retrieved_username, retrieved_password = credential_manager.get_credential(
            service_name
        )
        assert retrieved_password == new_password

        # Test deleting credentials
        credential_manager.delete_credential(service_name)

        retrieved_username, retrieved_password = credential_manager.get_credential(
            service_name
        )
        assert retrieved_username is None
        assert retrieved_password is None

    def test_credential_manager_nonexistent_service(self, credential_manager):
        """Test credential manager with nonexistent service."""
        username, password = credential_manager.get_credential("nonexistent_service")

        assert username is None
        assert password is None

    def test_password_hashing(self):
        """Test password hashing security."""
        from backend.security.password import PasswordManager

        password_manager = PasswordManager()

        # Test password hashing
        password = "test_password"
        hashed_password = password_manager.hash_password(password)

        assert hashed_password != password
        assert len(hashed_password) > 50  # Should be a long hash

        # Test password verification
        assert password_manager.verify_password(password, hashed_password)
        assert not password_manager.verify_password("wrong_password", hashed_password)

        # Test that same password produces different hashes (due to salt)
        hashed_password2 = password_manager.hash_password(password)
        assert hashed_password != hashed_password2

    def test_jwt_token_security(self):
        """Test JWT token security."""
        from backend.security.jwt import JWTManager

        jwt_manager = JWTManager("test_secret_key_32_chars_long_12345")

        # Test token creation
        payload = {"user_id": 1, "username": "test_user"}
        token = jwt_manager.create_token(payload)

        assert token is not None
        assert len(token) > 100  # JWT tokens are typically long

        # Test token verification
        decoded_payload = jwt_manager.verify_token(token)
        assert decoded_payload["user_id"] == 1
        assert decoded_payload["username"] == "test_user"

        # Test invalid token
        invalid_token = "invalid_token"
        decoded_payload = jwt_manager.verify_token(invalid_token)
        assert decoded_payload is None

    def test_jwt_token_expiration(self):
        """Test JWT token expiration."""
        from backend.security.jwt import JWTManager

        jwt_manager = JWTManager("test_secret_key_32_chars_long_12345")

        # Create token with short expiration
        payload = {"user_id": 1, "username": "test_user"}
        token = jwt_manager.create_token(payload, expires_in=1)  # 1 second

        # Token should be valid immediately
        decoded_payload = jwt_manager.verify_token(token)
        assert decoded_payload is not None

        # Wait for expiration
        import time

        time.sleep(2)

        # Token should be invalid after expiration
        decoded_payload = jwt_manager.verify_token(token)
        assert decoded_payload is None

    def test_input_validation(self):
        """Test input validation security."""
        from backend.security.validation import InputValidator

        validator = InputValidator()

        # Test SQL injection prevention
        malicious_input = "'; DROP TABLE users; --"
        assert not validator.is_safe_input(malicious_input)

        # Test XSS prevention
        xss_input = "<script>alert('xss')</script>"
        assert not validator.is_safe_input(xss_input)

        # Test valid input
        valid_input = "normal_user_input"
        assert validator.is_safe_input(valid_input)

        # Test input sanitization
        sanitized_input = validator.sanitize_input(malicious_input)
        assert validator.is_safe_input(sanitized_input)

    def test_rate_limiting(self):
        """Test rate limiting security."""
        from backend.security.rate_limit import RateLimiter

        rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

        # Test normal usage
        for i in range(10):
            assert rate_limiter.is_allowed("test_ip")

        # Test rate limit exceeded
        assert not rate_limiter.is_allowed("test_ip")

        # Test different IP
        assert rate_limiter.is_allowed("different_ip")

    def test_csrf_protection(self):
        """Test CSRF protection."""
        from backend.security.csrf import CSRFProtection

        csrf_protection = CSRFProtection()

        # Generate CSRF token
        token = csrf_protection.generate_token()
        assert token is not None

        # Verify valid token
        assert csrf_protection.verify_token(token)

        # Verify invalid token
        assert not csrf_protection.verify_token("invalid_token")

        # Test token expiration
        expired_token = csrf_protection.generate_token(expires_in=1)  # 1 second
        import time

        time.sleep(2)
        assert not csrf_protection.verify_token(expired_token)

    def test_file_upload_security(self):
        """Test file upload security."""
        from backend.security.file_upload import FileUploadValidator

        validator = FileUploadValidator()

        # Test allowed file types
        assert validator.is_allowed_file_type("test.txt")
        assert validator.is_allowed_file_type("test.csv")
        assert validator.is_allowed_file_type("test.json")

        # Test disallowed file types
        assert not validator.is_allowed_file_type("test.exe")
        assert not validator.is_allowed_file_type("test.bat")
        assert not validator.is_allowed_file_type("test.sh")

        # Test file size limits
        assert validator.is_valid_file_size(1024)  # 1KB
        assert not validator.is_valid_file_size(100 * 1024 * 1024)  # 100MB

    def test_secure_headers(self):
        """Test secure HTTP headers."""
        from backend.security.headers import SecureHeaders

        secure_headers = SecureHeaders()

        # Test header generation
        headers = secure_headers.get_headers()

        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers
        assert "Strict-Transport-Security" in headers
        assert "Content-Security-Policy" in headers

        # Test specific header values
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
        assert headers["X-XSS-Protection"] == "1; mode=block"

    def test_secure_random_generation(self):
        """Test secure random number generation."""
        from backend.security.random import SecureRandom

        secure_random = SecureRandom()

        # Test random string generation
        random_string = secure_random.generate_string(32)
        assert len(random_string) == 32
        assert isinstance(random_string, str)

        # Test random bytes generation
        random_bytes = secure_random.generate_bytes(32)
        assert len(random_bytes) == 32
        assert isinstance(random_bytes, bytes)

        # Test random number generation
        random_number = secure_random.generate_number(1, 100)
        assert 1 <= random_number <= 100

        # Test that generated values are different
        random_string2 = secure_random.generate_string(32)
        assert random_string != random_string2

    def test_secure_configuration(self, test_settings):
        """Test secure configuration management."""
        # Test that sensitive values are not logged
        config_dict = test_settings.dict()

        # Check that sensitive fields are not exposed
        sensitive_fields = ["secret_key", "encryption_key", "database_password"]
        for field in sensitive_fields:
            if field in config_dict:
                assert config_dict[field] != "test_secret_key"  # Should be masked

    def test_secure_logging(self):
        """Test secure logging practices."""
        from backend.security.logging import SecureLogger

        secure_logger = SecureLogger()

        # Test that sensitive data is not logged
        sensitive_data = "password123"
        log_message = secure_logger.sanitize_log_message(
            f"User password: {sensitive_data}"
        )

        assert sensitive_data not in log_message
        assert "***" in log_message  # Should be masked

    def test_secure_session_management(self):
        """Test secure session management."""
        from backend.security.session import SecureSession

        secure_session = SecureSession()

        # Test session creation
        session_id = secure_session.create_session({"user_id": 1})
        assert session_id is not None

        # Test session retrieval
        session_data = secure_session.get_session(session_id)
        assert session_data["user_id"] == 1

        # Test session invalidation
        secure_session.invalidate_session(session_id)
        session_data = secure_session.get_session(session_id)
        assert session_data is None

    def test_secure_api_authentication(self):
        """Test secure API authentication."""
        from backend.security.api_auth import APIAuthenticator

        api_auth = APIAuthenticator()

        # Test API key generation
        api_key = api_auth.generate_api_key()
        assert api_key is not None
        assert len(api_key) > 20

        # Test API key validation
        assert api_auth.validate_api_key(api_key)
        assert not api_auth.validate_api_key("invalid_key")

        # Test API key revocation
        api_auth.revoke_api_key(api_key)
        assert not api_auth.validate_api_key(api_key)

    def test_secure_data_transmission(self):
        """Test secure data transmission."""
        from backend.security.transmission import SecureTransmission

        secure_transmission = SecureTransmission()

        # Test data encryption for transmission
        data = "Sensitive data for transmission"
        encrypted_data = secure_transmission.encrypt_for_transmission(data)

        assert encrypted_data != data
        assert len(encrypted_data) > len(data)

        # Test data decryption
        decrypted_data = secure_transmission.decrypt_from_transmission(encrypted_data)
        assert decrypted_data == data

    def test_secure_error_handling(self):
        """Test secure error handling."""
        from backend.security.error_handling import SecureErrorHandler

        error_handler = SecureErrorHandler()

        # Test that sensitive information is not exposed in errors
        try:
            raise Exception("Database connection failed: password=secret123")
        except Exception as e:
            safe_error = error_handler.sanitize_error(str(e))

            assert "password=secret123" not in safe_error
            assert "Database connection failed" in safe_error

    def test_secure_dependency_management(self):
        """Test secure dependency management."""
        # Test that dependencies are up to date
        import pkg_resources

        # Check for known vulnerable packages
        vulnerable_packages = [
            "requests<2.25.0",
            "urllib3<1.26.0",
            "cryptography<3.4.0",
        ]

        for package in vulnerable_packages:
            try:
                pkg_resources.require(package)
                pytest.fail(f"Vulnerable package found: {package}")
            except pkg_resources.DistributionNotFound:
                pass  # Package not found, which is good

    def test_secure_file_permissions(self, test_settings):
        """Test secure file permissions."""
        # Test that database file has secure permissions
        if os.path.exists(test_settings.SQLITE_DB_PATH):
            file_stat = os.stat(test_settings.SQLITE_DB_PATH)
            file_mode = oct(file_stat.st_mode)[-3:]

            # File should not be readable by others
            assert file_mode[-1] != "4"  # Not readable by others
            assert file_mode[-1] != "6"  # Not readable/writable by others
            assert file_mode[-1] != "7"  # Not readable/writable/executable by others

    def test_secure_environment_variables(self):
        """Test secure environment variable handling."""
        # Test that sensitive environment variables are not exposed
        sensitive_vars = [
            "SECRET_KEY",
            "DATABASE_PASSWORD",
            "API_KEY",
            "ENCRYPTION_KEY",
        ]

        for var in sensitive_vars:
            if var in os.environ:
                # Environment variable should not be logged or exposed
                assert len(os.environ[var]) > 10  # Should be long enough
                assert os.environ[var] != "test"  # Should not be test value

    def test_secure_memory_handling(self):
        """Test secure memory handling."""
        from backend.security.memory import SecureMemory

        secure_memory = SecureMemory()

        # Test secure memory allocation
        sensitive_data = "sensitive_information"
        memory_handle = secure_memory.allocate_secure(len(sensitive_data))

        assert memory_handle is not None

        # Test secure memory deallocation
        secure_memory.deallocate_secure(memory_handle)

        # Memory should be cleared
        assert secure_memory.is_cleared(memory_handle)

    def test_secure_network_communication(self):
        """Test secure network communication."""
        from backend.security.network import SecureNetwork

        secure_network = SecureNetwork()

        # Test TLS configuration
        tls_config = secure_network.get_tls_config()

        assert tls_config["min_version"] == "TLSv1.2"
        assert tls_config["cipher_suites"] is not None
        assert len(tls_config["cipher_suites"]) > 0

        # Test certificate validation
        assert tls_config["verify_certificates"] is True
        assert tls_config["check_revocation"] is True

    def test_secure_backup_encryption(self):
        """Test secure backup encryption."""
        from backend.security.backup import SecureBackup

        secure_backup = SecureBackup()

        # Test backup encryption
        backup_data = "Important backup data"
        encrypted_backup = secure_backup.encrypt_backup(backup_data)

        assert encrypted_backup != backup_data

        # Test backup decryption
        decrypted_backup = secure_backup.decrypt_backup(encrypted_backup)
        assert decrypted_backup == backup_data

    def test_security_audit_logging(self):
        """Test security audit logging."""
        from backend.security.audit import SecurityAudit

        security_audit = SecurityAudit()

        # Test audit log creation
        audit_event = {
            "event_type": "login_attempt",
            "user_id": 1,
            "ip_address": "192.168.1.1",
            "timestamp": "2023-12-01T12:00:00Z",
        }

        log_entry = security_audit.create_audit_log(audit_event)

        assert log_entry is not None
        assert "login_attempt" in log_entry
        assert "192.168.1.1" in log_entry

        # Test audit log retrieval
        audit_logs = security_audit.get_audit_logs("login_attempt")
        assert len(audit_logs) > 0
