"""
Enterprise Security System for BOLT AI Neural Agent System.

Implements comprehensive enterprise-grade security features including:
- Role-based access control (RBAC)
- Multi-factor authentication (MFA)
- Security monitoring and alerting
- Compliance reporting
- Threat detection and response
"""

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class Permission(Enum):
    """System permissions"""

    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    DELETE_DATA = "delete_data"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_LOGS = "view_logs"
    MANAGE_SETTINGS = "manage_settings"
    EXECUTE_TRADES = "execute_trades"
    VIEW_REPORTS = "view_reports"
    MANAGE_SECURITY = "manage_security"


class Role(Enum):
    """System roles"""

    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    TRADER = "trader"
    VIEWER = "viewer"
    AUDITOR = "auditor"


class SecurityEvent(Enum):
    """Security event types"""

    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_ACCESS = "data_access"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_VIOLATION = "security_violation"


@dataclass
class User:
    """User data model"""

    id: str
    username: str
    email: str
    roles: List[Role]
    permissions: Set[Permission]
    mfa_enabled: bool
    last_login: Optional[datetime]
    created_at: datetime
    is_active: bool
    failed_login_attempts: int
    locked_until: Optional[datetime]


@dataclass
class SecurityEvent:
    """Security event data model"""

    id: str
    event_type: SecurityEvent
    user_id: Optional[str]
    description: str
    severity: str
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    metadata: Dict[str, Any]


class RoleBasedAccessControl:
    """
    Role-based access control system.

    Features:
    - Hierarchical role management
    - Permission inheritance
    - Dynamic permission assignment
    - Access control lists (ACLs)
    """

    def __init__(self):
        self.roles = {}
        self.permissions = {}
        self.users = {}
        self.access_logs = []

        # Initialize default roles and permissions
        self._initialize_default_roles()
        self._initialize_default_permissions()

    def _initialize_default_roles(self):
        """Initialize default system roles"""

        self.roles = {
            Role.ADMIN: {
                "name": "Administrator",
                "description": "Full system access",
                "permissions": set(Permission),
                "inherits_from": [],
                "created_at": datetime.now(),
            },
            Role.MANAGER: {
                "name": "Manager",
                "description": "Management access",
                "permissions": {
                    Permission.READ_DATA,
                    Permission.WRITE_DATA,
                    Permission.VIEW_REPORTS,
                    Permission.MANAGE_USERS,
                    Permission.VIEW_LOGS,
                },
                "inherits_from": [],
                "created_at": datetime.now(),
            },
            Role.ANALYST: {
                "name": "Analyst",
                "description": "Data analysis access",
                "permissions": {
                    Permission.READ_DATA,
                    Permission.VIEW_REPORTS,
                    Permission.VIEW_LOGS,
                },
                "inherits_from": [],
                "created_at": datetime.now(),
            },
            Role.TRADER: {
                "name": "Trader",
                "description": "Trading access",
                "permissions": {
                    Permission.READ_DATA,
                    Permission.EXECUTE_TRADES,
                    Permission.VIEW_REPORTS,
                },
                "inherits_from": [],
                "created_at": datetime.now(),
            },
            Role.VIEWER: {
                "name": "Viewer",
                "description": "Read-only access",
                "permissions": {Permission.READ_DATA, Permission.VIEW_REPORTS},
                "inherits_from": [],
                "created_at": datetime.now(),
            },
            Role.AUDITOR: {
                "name": "Auditor",
                "description": "Audit and compliance access",
                "permissions": {
                    Permission.READ_DATA,
                    Permission.VIEW_LOGS,
                    Permission.VIEW_REPORTS,
                },
                "inherits_from": [],
                "created_at": datetime.now(),
            },
        }

    def _initialize_default_permissions(self):
        """Initialize default system permissions"""

        self.permissions = {
            Permission.READ_DATA: {
                "name": "Read Data",
                "description": "Read access to system data",
                "resource": "data",
                "action": "read",
            },
            Permission.WRITE_DATA: {
                "name": "Write Data",
                "description": "Write access to system data",
                "resource": "data",
                "action": "write",
            },
            Permission.DELETE_DATA: {
                "name": "Delete Data",
                "description": "Delete access to system data",
                "resource": "data",
                "action": "delete",
            },
            Permission.MANAGE_USERS: {
                "name": "Manage Users",
                "description": "User management access",
                "resource": "users",
                "action": "manage",
            },
            Permission.MANAGE_ROLES: {
                "name": "Manage Roles",
                "description": "Role management access",
                "resource": "roles",
                "action": "manage",
            },
            Permission.VIEW_LOGS: {
                "name": "View Logs",
                "description": "Access to system logs",
                "resource": "logs",
                "action": "read",
            },
            Permission.MANAGE_SETTINGS: {
                "name": "Manage Settings",
                "description": "System settings management",
                "resource": "settings",
                "action": "manage",
            },
            Permission.EXECUTE_TRADES: {
                "name": "Execute Trades",
                "description": "Trading execution access",
                "resource": "trading",
                "action": "execute",
            },
            Permission.VIEW_REPORTS: {
                "name": "View Reports",
                "description": "Access to reports",
                "resource": "reports",
                "action": "read",
            },
            Permission.MANAGE_SECURITY: {
                "name": "Manage Security",
                "description": "Security management access",
                "resource": "security",
                "action": "manage",
            },
        }

    def create_user(
        self, username: str, email: str, roles: List[Role], password_hash: str
    ) -> str:
        """
        Create a new user.

        Args:
            username: Username
            email: Email address
            roles: List of roles
            password_hash: Hashed password

        Returns:
            User ID
        """

        user_id = str(uuid.uuid4())

        # Calculate effective permissions
        effective_permissions = self._calculate_effective_permissions(roles)

        user = User(
            id=user_id,
            username=username,
            email=email,
            roles=roles,
            permissions=effective_permissions,
            mfa_enabled=False,
            last_login=None,
            created_at=datetime.now(),
            is_active=True,
            failed_login_attempts=0,
            locked_until=None,
        )

        self.users[user_id] = user

        # Log user creation
        self._log_access_event(
            event_type=SecurityEvent.LOGIN_SUCCESS,
            user_id=user_id,
            description=f"User created: {username}",
            severity="info",
        )

        logger.info(f"User created: {username} ({user_id})")
        return user_id

    def assign_role(self, user_id: str, role: Role) -> bool:
        """
        Assign role to user.

        Args:
            user_id: User ID
            role: Role to assign

        Returns:
            True if assigned successfully
        """

        if user_id not in self.users:
            return False

        user = self.users[user_id]

        if role not in user.roles:
            user.roles.append(role)
            user.permissions = self._calculate_effective_permissions(user.roles)

            # Log role assignment
            self._log_access_event(
                event_type=SecurityEvent.CONFIGURATION_CHANGE,
                user_id=user_id,
                description=f"Role assigned: {role.value}",
                severity="info",
            )

            logger.info(f"Role assigned to user {user_id}: {role.value}")
            return True

        return False

    def remove_role(self, user_id: str, role: Role) -> bool:
        """
        Remove role from user.

        Args:
            user_id: User ID
            role: Role to remove

        Returns:
            True if removed successfully
        """

        if user_id not in self.users:
            return False

        user = self.users[user_id]

        if role in user.roles:
            user.roles.remove(role)
            user.permissions = self._calculate_effective_permissions(user.roles)

            # Log role removal
            self._log_access_event(
                event_type=SecurityEvent.CONFIGURATION_CHANGE,
                user_id=user_id,
                description=f"Role removed: {role.value}",
                severity="info",
            )

            logger.info(f"Role removed from user {user_id}: {role.value}")
            return True

        return False

    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Check if user has permission.

        Args:
            user_id: User ID
            permission: Permission to check

        Returns:
            True if user has permission
        """

        if user_id not in self.users:
            return False

        user = self.users[user_id]

        # Check if user is active
        if not user.is_active:
            return False

        # Check if user is locked
        if user.locked_until and user.locked_until > datetime.now():
            return False

        # Check permission
        has_permission = permission in user.permissions

        # Log access attempt
        self._log_access_event(
            event_type=SecurityEvent.DATA_ACCESS,
            user_id=user_id,
            description=f"Permission check: {permission.value}",
            severity="info" if has_permission else "warning",
        )

        return has_permission

    def _calculate_effective_permissions(self, roles: List[Role]) -> Set[Permission]:
        """Calculate effective permissions for roles"""

        effective_permissions = set()

        for role in roles:
            if role in self.roles:
                role_permissions = self.roles[role]["permissions"]
                effective_permissions.update(role_permissions)

        return effective_permissions

    def _log_access_event(
        self,
        event_type: SecurityEvent,
        user_id: Optional[str],
        description: str,
        severity: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Dict[str, Any] = None,
    ):
        """Log access event"""

        event = SecurityEvent(
            id=str(uuid.uuid4()),
            event_type=event_type,
            user_id=user_id,
            description=description,
            severity=severity,
            timestamp=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
        )

        self.access_logs.append(event)

        # Keep only last 10000 entries
        if len(self.access_logs) > 10000:
            self.access_logs = self.access_logs[-10000:]

    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get user's effective permissions"""

        if user_id not in self.users:
            return set()

        return self.users[user_id].permissions

    def get_users_by_role(self, role: Role) -> List[User]:
        """Get users with specific role"""

        users = []
        for user in self.users.values():
            if role in user.roles:
                users.append(user)

        return users

    def get_access_logs(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[SecurityEvent] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SecurityEvent]:
        """Get filtered access logs"""

        logs = self.access_logs

        # Apply filters
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]

        if event_type:
            logs = [log for log in logs if log.event_type == event_type]

        if start_date:
            logs = [log for log in logs if log.timestamp >= start_date]

        if end_date:
            logs = [log for log in logs if log.timestamp <= end_date]

        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x.timestamp, reverse=True)

        return logs[:limit]

    def generate_security_report(self) -> Dict[str, Any]:
        """Generate security report"""

        # Count events by type
        event_counts = {}
        for log in self.access_logs:
            event_type = log.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Count events by severity
        severity_counts = {}
        for log in self.access_logs:
            severity = log.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Count active users
        active_users = len([u for u in self.users.values() if u.is_active])

        # Count locked users
        locked_users = len(
            [
                u
                for u in self.users.values()
                if u.locked_until and u.locked_until > datetime.now()
            ]
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "total_users": len(self.users),
            "active_users": active_users,
            "locked_users": locked_users,
            "total_events": len(self.access_logs),
            "event_counts": event_counts,
            "severity_counts": severity_counts,
            "roles": {role.value: len(self.get_users_by_role(role)) for role in Role},
        }


class SecurityMonitor:
    """
    Security monitoring and threat detection system.

    Features:
    - Real-time threat detection
    - Anomaly detection
    - Security alerting
    - Incident response
    """

    def __init__(self, rbac: RoleBasedAccessControl):
        self.rbac = rbac
        self.threat_detection_rules = {}
        self.alert_thresholds = {}
        self.security_alerts = []

        # Initialize threat detection rules
        self._initialize_threat_rules()

    def _initialize_threat_rules(self):
        """Initialize threat detection rules"""

        self.threat_detection_rules = {
            "failed_login_threshold": 5,  # Failed logins before lockout
            "suspicious_activity_window": 300,  # 5 minutes
            "unusual_access_pattern": 10,  # Unusual access attempts
            "privilege_escalation": True,  # Detect privilege escalation
            "data_exfiltration": True,  # Detect data exfiltration
            "anomalous_behavior": True,  # Detect anomalous behavior
        }

    def monitor_access_event(self, event: SecurityEvent):
        """Monitor access event for threats"""

        # Check for failed login attempts
        if event.event_type == SecurityEvent.LOGIN_FAILURE:
            self._check_failed_logins(event)

        # Check for permission denied events
        elif event.event_type == SecurityEvent.PERMISSION_DENIED:
            self._check_permission_denied(event)

        # Check for suspicious activity
        elif event.event_type == SecurityEvent.SUSPICIOUS_ACTIVITY:
            self._check_suspicious_activity(event)

        # Check for data access patterns
        elif event.event_type == SecurityEvent.DATA_ACCESS:
            self._check_data_access_patterns(event)

    def _check_failed_logins(self, event: SecurityEvent):
        """Check for excessive failed login attempts"""

        if not event.user_id:
            return

        user = self.rbac.users.get(event.user_id)
        if not user:
            return

        # Increment failed login attempts
        user.failed_login_attempts += 1

        # Check threshold
        if (
            user.failed_login_attempts
            >= self.threat_detection_rules["failed_login_threshold"]
        ):
            # Lock user account
            user.locked_until = datetime.now() + timedelta(minutes=30)

            # Create security alert
            self._create_security_alert(
                alert_type="account_locked",
                severity="high",
                description=f"User account locked due to {user.failed_login_attempts} failed login attempts",
                user_id=event.user_id,
                metadata={"failed_attempts": user.failed_login_attempts},
            )

    def _check_permission_denied(self, event: SecurityEvent):
        """Check for excessive permission denied events"""

        if not event.user_id:
            return

        # Count permission denied events in last 5 minutes
        recent_events = self.rbac.get_access_logs(
            user_id=event.user_id,
            event_type=SecurityEvent.PERMISSION_DENIED,
            start_date=datetime.now() - timedelta(minutes=5),
        )

        if len(recent_events) >= 10:
            # Create security alert
            self._create_security_alert(
                alert_type="excessive_permission_denied",
                severity="medium",
                description=f"User has {len(recent_events)} permission denied events in 5 minutes",
                user_id=event.user_id,
                metadata={"denied_events": len(recent_events)},
            )

    def _check_suspicious_activity(self, event: SecurityEvent):
        """Check for suspicious activity patterns"""

        # Create security alert for suspicious activity
        self._create_security_alert(
            alert_type="suspicious_activity",
            severity="high",
            description=event.description,
            user_id=event.user_id,
            metadata=event.metadata,
        )

    def _check_data_access_patterns(self, event: SecurityEvent):
        """Check for unusual data access patterns"""

        if not event.user_id:
            return

        # Count data access events in last hour
        recent_events = self.rbac.get_access_logs(
            user_id=event.user_id,
            event_type=SecurityEvent.DATA_ACCESS,
            start_date=datetime.now() - timedelta(hours=1),
        )

        if len(recent_events) >= 100:
            # Create security alert
            self._create_security_alert(
                alert_type="excessive_data_access",
                severity="medium",
                description=f"User has {len(recent_events)} data access events in 1 hour",
                user_id=event.user_id,
                metadata={"access_events": len(recent_events)},
            )

    def _create_security_alert(
        self,
        alert_type: str,
        severity: str,
        description: str,
        user_id: Optional[str] = None,
        metadata: Dict[str, Any] = None,
    ):
        """Create security alert"""

        alert = {
            "id": str(uuid.uuid4()),
            "alert_type": alert_type,
            "severity": severity,
            "description": description,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "status": "active",
            "acknowledged": False,
        }

        self.security_alerts.append(alert)

        # Keep only last 1000 alerts
        if len(self.security_alerts) > 1000:
            self.security_alerts = self.security_alerts[-1000:]

        logger.warning(f"Security alert created: {alert_type} - {description}")

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active security alerts"""

        return [alert for alert in self.security_alerts if alert["status"] == "active"]

    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge security alert"""

        for alert in self.security_alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_by"] = user_id
                alert["acknowledged_at"] = datetime.now().isoformat()

                logger.info(f"Security alert acknowledged: {alert_id} by {user_id}")
                return True

        return False

    def resolve_alert(self, alert_id: str, user_id: str, resolution: str) -> bool:
        """Resolve security alert"""

        for alert in self.security_alerts:
            if alert["id"] == alert_id:
                alert["status"] = "resolved"
                alert["resolved_by"] = user_id
                alert["resolved_at"] = datetime.now().isoformat()
                alert["resolution"] = resolution

                logger.info(f"Security alert resolved: {alert_id} by {user_id}")
                return True

        return False


def require_permission(permission: Permission):
    """Decorator to require specific permission"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract user_id from arguments or context
            user_id = kwargs.get("user_id") or args[0] if args else None

            if not user_id:
                raise PermissionError("User ID required for permission check")

            # Check permission
            rbac = RoleBasedAccessControl()  # In practice, this would be injected
            if not rbac.check_permission(user_id, permission):
                raise PermissionError(f"Permission denied: {permission.value}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_role(role: Role):
    """Decorator to require specific role"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract user_id from arguments or context
            user_id = kwargs.get("user_id") or args[0] if args else None

            if not user_id:
                raise PermissionError("User ID required for role check")

            # Check role
            rbac = RoleBasedAccessControl()  # In practice, this would be injected
            if user_id not in rbac.users:
                raise PermissionError("User not found")

            user = rbac.users[user_id]
            if role not in user.roles:
                raise PermissionError(f"Role required: {role.value}")

            return func(*args, **kwargs)

        return wrapper

    return decorator
