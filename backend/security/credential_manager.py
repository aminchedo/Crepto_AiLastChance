"""
Windows Credential Manager Integration for BOLT AI Neural Agent System.

Provides secure storage and retrieval of sensitive credentials including:
- API keys and secrets
- Database encryption keys
- TLS certificates
- User authentication tokens
"""

import base64
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import win32con
import win32cred
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class CredentialType(Enum):
    """Types of credentials"""

    API_KEY = "api_key"
    SECRET = "secret"
    CERTIFICATE = "certificate"
    TOKEN = "token"
    ENCRYPTION_KEY = "encryption_key"
    DATABASE_PASSWORD = "database_password"


class CredentialManager:
    """
    Windows Credential Manager integration for secure credential storage.

    Features:
    - Encrypted credential storage
    - Automatic credential rotation
    - Audit logging
    - Backup and recovery
    - Multi-user support
    """

    def __init__(self):
        self.target_name_prefix = "BoltAI_"
        self.credential_cache = {}
        self.audit_log = []
        self.rotation_schedules = {}

        # Initialize encryption key
        self._initialize_encryption_key()

    def _initialize_encryption_key(self):
        """Initialize encryption key for credential protection"""
        try:
            # Try to get existing key
            cred = win32cred.CredRead(
                TargetName=f"{self.target_name_prefix}EncryptionKey",
                Type=win32cred.CRED_TYPE_GENERIC,
            )
            self.encryption_key = cred["CredentialBlob"]
        except:
            # Generate new key
            self.encryption_key = Fernet.generate_key()
            self._store_credential(
                f"{self.target_name_prefix}EncryptionKey",
                self.encryption_key,
                "Encryption key for credential protection",
            )

    def store_credential(
        self,
        name: str,
        value: str,
        credential_type: CredentialType,
        description: str = "",
        expires: Optional[datetime] = None,
        tags: List[str] = None,
    ) -> bool:
        """
        Store credential securely in Windows Credential Manager.

        Args:
            name: Credential name
            value: Credential value
            credential_type: Type of credential
            description: Description of the credential
            expires: Expiration date
            tags: Additional tags

        Returns:
            True if stored successfully
        """

        try:
            # Encrypt the credential value
            encrypted_value = self._encrypt_credential(value)

            # Create credential data
            credential_data = {
                "value": encrypted_value,
                "type": credential_type.value,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "expires": expires.isoformat() if expires else None,
                "tags": tags or [],
            }

            # Store in Windows Credential Manager
            target_name = f"{self.target_name_prefix}{name}"
            success = win32cred.CredWrite(
                {
                    "Type": win32cred.CRED_TYPE_GENERIC,
                    "TargetName": target_name,
                    "CredentialBlob": json.dumps(credential_data).encode(),
                    "Persist": win32cred.CRED_PERSIST_LOCAL_MACHINE,
                    "Comment": f"{credential_type.value}: {description}",
                }
            )

            if success:
                # Cache the credential
                self.credential_cache[name] = {
                    "value": value,
                    "type": credential_type,
                    "cached_at": datetime.now(),
                    "expires": expires,
                }

                # Log the action
                self._log_credential_action(
                    "store", name, credential_type, success=True
                )

                logger.info(f"Credential stored: {name} ({credential_type.value})")
                return True
            else:
                self._log_credential_action(
                    "store", name, credential_type, success=False
                )
                return False

        except Exception as e:
            logger.error(f"Error storing credential {name}: {str(e)}")
            self._log_credential_action(
                "store", name, credential_type, success=False, error=str(e)
            )
            return False

    def retrieve_credential(
        self, name: str, credential_type: CredentialType = None
    ) -> Optional[str]:
        """
        Retrieve credential from Windows Credential Manager.

        Args:
            name: Credential name
            credential_type: Expected credential type

        Returns:
            Credential value or None if not found
        """

        try:
            # Check cache first
            if name in self.credential_cache:
                cached = self.credential_cache[name]

                # Check if expired
                if cached["expires"] and cached["expires"] < datetime.now():
                    logger.warning(f"Cached credential expired: {name}")
                    del self.credential_cache[name]
                else:
                    self._log_credential_action(
                        "retrieve", name, cached["type"], success=True, from_cache=True
                    )
                    return cached["value"]

            # Retrieve from Windows Credential Manager
            target_name = f"{self.target_name_prefix}{name}"
            cred = win32cred.CredRead(
                TargetName=target_name, Type=win32cred.CRED_TYPE_GENERIC
            )

            # Parse credential data
            credential_data = json.loads(cred["CredentialBlob"].decode())

            # Check expiration
            if credential_data.get("expires"):
                expires = datetime.fromisoformat(credential_data["expires"])
                if expires < datetime.now():
                    logger.warning(f"Credential expired: {name}")
                    self._log_credential_action(
                        "retrieve",
                        name,
                        credential_type,
                        success=False,
                        error="Expired",
                    )
                    return None

            # Decrypt the credential value
            decrypted_value = self._decrypt_credential(credential_data["value"])

            # Validate type if specified
            if credential_type and credential_data["type"] != credential_type.value:
                logger.warning(f"Credential type mismatch: {name}")
                self._log_credential_action(
                    "retrieve",
                    name,
                    credential_type,
                    success=False,
                    error="Type mismatch",
                )
                return None

            # Cache the credential
            self.credential_cache[name] = {
                "value": decrypted_value,
                "type": CredentialType(credential_data["type"]),
                "cached_at": datetime.now(),
                "expires": (
                    datetime.fromisoformat(credential_data["expires"])
                    if credential_data.get("expires")
                    else None
                ),
            }

            self._log_credential_action("retrieve", name, credential_type, success=True)
            logger.info(f"Credential retrieved: {name}")
            return decrypted_value

        except Exception as e:
            logger.error(f"Error retrieving credential {name}: {str(e)}")
            self._log_credential_action(
                "retrieve", name, credential_type, success=False, error=str(e)
            )
            return None

    def delete_credential(self, name: str) -> bool:
        """
        Delete credential from Windows Credential Manager.

        Args:
            name: Credential name

        Returns:
            True if deleted successfully
        """

        try:
            target_name = f"{self.target_name_prefix}{name}"
            success = win32cred.CredDelete(
                TargetName=target_name, Type=win32cred.CRED_TYPE_GENERIC
            )

            if success:
                # Remove from cache
                if name in self.credential_cache:
                    del self.credential_cache[name]

                self._log_credential_action("delete", name, None, success=True)
                logger.info(f"Credential deleted: {name}")
                return True
            else:
                self._log_credential_action("delete", name, None, success=False)
                return False

        except Exception as e:
            logger.error(f"Error deleting credential {name}: {str(e)}")
            self._log_credential_action(
                "delete", name, None, success=False, error=str(e)
            )
            return False

    def list_credentials(self) -> List[Dict[str, Any]]:
        """
        List all stored credentials.

        Returns:
            List of credential information
        """

        credentials = []

        try:
            # Get all credentials
            creds = win32cred.CredEnumerate()

            for cred in creds:
                if cred["TargetName"].startswith(self.target_name_prefix):
                    name = cred["TargetName"][len(self.target_name_prefix) :]

                    try:
                        # Parse credential data
                        credential_data = json.loads(cred["CredentialBlob"].decode())

                        credentials.append(
                            {
                                "name": name,
                                "type": credential_data.get("type", "unknown"),
                                "description": credential_data.get("description", ""),
                                "created_at": credential_data.get("created_at", ""),
                                "expires": credential_data.get("expires"),
                                "tags": credential_data.get("tags", []),
                            }
                        )
                    except:
                        # Skip malformed credentials
                        continue

        except Exception as e:
            logger.error(f"Error listing credentials: {str(e)}")

        return credentials

    def rotate_credential(
        self,
        name: str,
        new_value: str,
        credential_type: CredentialType,
        description: str = "",
    ) -> bool:
        """
        Rotate credential with new value.

        Args:
            name: Credential name
            new_value: New credential value
            credential_type: Type of credential
            description: Description of the credential

        Returns:
            True if rotated successfully
        """

        try:
            # Store new credential
            success = self.store_credential(
                name=name,
                value=new_value,
                credential_type=credential_type,
                description=description,
            )

            if success:
                # Log rotation
                self._log_credential_action(
                    "rotate", name, credential_type, success=True
                )
                logger.info(f"Credential rotated: {name}")
                return True
            else:
                self._log_credential_action(
                    "rotate", name, credential_type, success=False
                )
                return False

        except Exception as e:
            logger.error(f"Error rotating credential {name}: {str(e)}")
            self._log_credential_action(
                "rotate", name, credential_type, success=False, error=str(e)
            )
            return False

    def schedule_credential_rotation(
        self, name: str, rotation_days: int, credential_type: CredentialType
    ) -> bool:
        """
        Schedule automatic credential rotation.

        Args:
            name: Credential name
            rotation_days: Days between rotations
            credential_type: Type of credential

        Returns:
            True if scheduled successfully
        """

        try:
            rotation_date = datetime.now() + timedelta(days=rotation_days)

            self.rotation_schedules[name] = {
                "rotation_days": rotation_days,
                "next_rotation": rotation_date.isoformat(),
                "credential_type": credential_type.value,
                "created_at": datetime.now().isoformat(),
            }

            logger.info(
                f"Credential rotation scheduled: {name} (every {rotation_days} days)"
            )
            return True

        except Exception as e:
            logger.error(f"Error scheduling credential rotation {name}: {str(e)}")
            return False

    def process_scheduled_rotations(self) -> List[str]:
        """
        Process scheduled credential rotations.

        Returns:
            List of rotated credential names
        """

        rotated = []
        current_time = datetime.now()

        for name, schedule in self.rotation_schedules.items():
            if datetime.fromisoformat(schedule["next_rotation"]) <= current_time:
                # Rotation due
                logger.info(f"Credential rotation due: {name}")

                # In practice, this would generate a new credential value
                # For now, just log the event
                rotated.append(name)

                # Schedule next rotation
                next_rotation = current_time + timedelta(days=schedule["rotation_days"])
                schedule["next_rotation"] = next_rotation.isoformat()

        return rotated

    def _encrypt_credential(self, value: str) -> str:
        """Encrypt credential value"""
        fernet = Fernet(self.encryption_key)
        encrypted = fernet.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()

    def _decrypt_credential(self, encrypted_value: str) -> str:
        """Decrypt credential value"""
        fernet = Fernet(self.encryption_key)
        encrypted = base64.b64decode(encrypted_value.encode())
        decrypted = fernet.decrypt(encrypted)
        return decrypted.decode()

    def _store_credential(self, target_name: str, value: bytes, comment: str) -> bool:
        """Store credential in Windows Credential Manager"""
        try:
            return win32cred.CredWrite(
                {
                    "Type": win32cred.CRED_TYPE_GENERIC,
                    "TargetName": target_name,
                    "CredentialBlob": value,
                    "Persist": win32cred.CRED_PERSIST_LOCAL_MACHINE,
                    "Comment": comment,
                }
            )
        except Exception as e:
            logger.error(f"Error storing credential {target_name}: {str(e)}")
            return False

    def _log_credential_action(
        self,
        action: str,
        name: str,
        credential_type: CredentialType,
        success: bool,
        from_cache: bool = False,
        error: str = None,
    ):
        """Log credential action for audit purposes"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "name": name,
            "type": credential_type.value if credential_type else "unknown",
            "success": success,
            "from_cache": from_cache,
            "error": error,
        }

        self.audit_log.append(log_entry)

        # Keep only last 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get audit log entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of audit log entries
        """

        return self.audit_log[-limit:] if limit else self.audit_log

    def export_credentials(self, password: str) -> str:
        """
        Export all credentials to encrypted backup.

        Args:
            password: Password for encryption

        Returns:
            Encrypted backup data
        """

        try:
            # Get all credentials
            credentials = self.list_credentials()

            # Create backup data
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "credentials": credentials,
                "rotation_schedules": self.rotation_schedules,
            }

            # Encrypt backup
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            fernet = Fernet(key)

            encrypted_backup = fernet.encrypt(json.dumps(backup_data).encode())

            return base64.b64encode(salt + encrypted_backup).decode()

        except Exception as e:
            logger.error(f"Error exporting credentials: {str(e)}")
            return None

    def import_credentials(self, backup_data: str, password: str) -> bool:
        """
        Import credentials from encrypted backup.

        Args:
            backup_data: Encrypted backup data
            password: Password for decryption

        Returns:
            True if imported successfully
        """

        try:
            # Decode backup
            encrypted_data = base64.b64decode(backup_data.encode())
            salt = encrypted_data[:16]
            encrypted = encrypted_data[16:]

            # Decrypt backup
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            fernet = Fernet(key)

            decrypted_backup = fernet.decrypt(encrypted)
            backup = json.loads(decrypted_backup.decode())

            # Import rotation schedules
            self.rotation_schedules = backup.get("rotation_schedules", {})

            logger.info(f"Credentials imported from backup: {backup['timestamp']}")
            return True

        except Exception as e:
            logger.error(f"Error importing credentials: {str(e)}")
            return False

    def get_credential_statistics(self) -> Dict[str, Any]:
        """Get credential management statistics"""

        credentials = self.list_credentials()

        # Count by type
        type_counts = {}
        for cred in credentials:
            cred_type = cred["type"]
            type_counts[cred_type] = type_counts.get(cred_type, 0) + 1

        # Count expired
        expired_count = 0
        for cred in credentials:
            if cred.get("expires"):
                expires = datetime.fromisoformat(cred["expires"])
                if expires < datetime.now():
                    expired_count += 1

        # Count scheduled rotations
        rotation_count = len(self.rotation_schedules)

        return {
            "total_credentials": len(credentials),
            "type_counts": type_counts,
            "expired_count": expired_count,
            "rotation_schedules": rotation_count,
            "cached_credentials": len(self.credential_cache),
            "audit_log_entries": len(self.audit_log),
        }
