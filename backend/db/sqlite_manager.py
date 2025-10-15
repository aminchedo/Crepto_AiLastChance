"""
SQLite Database Manager with SQLCipher Encryption for BOLT AI Neural Agent System.

Provides secure SQLite database management with:
- SQLCipher AES-256 encryption
- Windows Credential Manager integration
- WAL mode optimization
- Connection pooling
- Migration utilities
- Backup and restore functionality
"""

import hashlib
import json
import logging
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# SQLCipher support
try:
    import sqlcipher3 as sqlite3

    SQLCIPHER_AVAILABLE = True
except ImportError:
    SQLCIPHER_AVAILABLE = False
    import sqlite3

# Windows Credential Manager
try:
    import win32cred

    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

logger = logging.getLogger(__name__)


class SQLiteManager:
    """
    Secure SQLite database manager with encryption and Windows integration.

    Features:
    - SQLCipher AES-256 encryption
    - Windows Credential Manager for key storage
    - WAL mode for better concurrency
    - Connection pooling
    - Automatic backup and recovery
    - Migration utilities
    """

    def __init__(self, db_path: str = "data/crypto_ai.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Database configuration
        self.page_size = 4096
        self.cache_size = -64000  # 64MB cache
        self.journal_mode = "WAL"
        self.synchronous = "NORMAL"
        self.temp_store = "MEMORY"

        # Connection pool
        self._connection_pool = []
        self._pool_lock = threading.Lock()
        self._max_connections = 10

        # Encryption settings
        self.encryption_key = None
        self.kdf_iterations = 256000
        self.cipher_page_size = 4096

        # Initialize encryption key
        self._initialize_encryption_key()

        # Database schema version
        self.schema_version = 1

        logger.info(f"SQLite Manager initialized: {self.db_path}")

    def _initialize_encryption_key(self):
        """Initialize encryption key from Windows Credential Manager"""

        if not SQLCIPHER_AVAILABLE:
            logger.warning("SQLCipher not available, using standard SQLite")
            return

        if not WIN32_AVAILABLE:
            logger.warning("Windows Credential Manager not available")
            return

        try:
            # Try to get existing key
            cred = win32cred.CredRead(
                TargetName="BoltAI_SQLite_Key", Type=win32cred.CRED_TYPE_GENERIC
            )
            self.encryption_key = cred["CredentialBlob"]
            logger.info("Encryption key retrieved from Windows Credential Manager")

        except:
            # Generate new key
            self.encryption_key = os.urandom(32)  # 256-bit key

            # Store in Windows Credential Manager
            try:
                win32cred.CredWrite(
                    {
                        "Type": win32cred.CRED_TYPE_GENERIC,
                        "TargetName": "BoltAI_SQLite_Key",
                        "CredentialBlob": self.encryption_key,
                        "Persist": win32cred.CRED_PERSIST_LOCAL_MACHINE,
                        "Comment": "SQLite encryption key for BOLT AI",
                    }
                )
                logger.info(
                    "New encryption key generated and stored in Windows Credential Manager"
                )
            except Exception as e:
                logger.error(f"Failed to store encryption key: {str(e)}")
                raise

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection from pool or create new one"""

        with self._pool_lock:
            if self._connection_pool:
                conn = self._connection_pool.pop()
                # Test connection
                try:
                    conn.execute("SELECT 1")
                    return conn
                except:
                    # Connection is stale, create new one
                    pass

        # Create new connection
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False, timeout=30.0)

        # Configure connection
        self._configure_connection(conn)

        return conn

    def _return_connection(self, conn: sqlite3.Connection):
        """Return connection to pool"""

        with self._pool_lock:
            if len(self._connection_pool) < self._max_connections:
                self._connection_pool.append(conn)
            else:
                conn.close()

    def _configure_connection(self, conn: sqlite3.Connection):
        """Configure SQLite connection with optimal settings"""

        # Set encryption key if available
        if SQLCIPHER_AVAILABLE and self.encryption_key:
            conn.execute(f"PRAGMA key = '{self.encryption_key.hex()}'")
            conn.execute(f"PRAGMA cipher_page_size = {self.cipher_page_size}")
            conn.execute(f"PRAGMA kdf_iter = {self.kdf_iterations}")

        # Configure SQLite settings
        conn.execute(f"PRAGMA page_size = {self.page_size}")
        conn.execute(f"PRAGMA cache_size = {self.cache_size}")
        conn.execute(f"PRAGMA journal_mode = {self.journal_mode}")
        conn.execute(f"PRAGMA synchronous = {self.synchronous}")
        conn.execute(f"PRAGMA temp_store = {self.temp_store}")

        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")

        # Set busy timeout
        conn.execute("PRAGMA busy_timeout = 30000")

        # Create tables if they don't exist
        self._create_tables(conn)

    def _create_tables(self, conn: sqlite3.Connection):
        """Create database tables"""

        # Users table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                roles TEXT NOT NULL,  -- JSON array of roles
                permissions TEXT NOT NULL,  -- JSON array of permissions
                mfa_enabled BOOLEAN DEFAULT FALSE,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        """
        )

        # Market data table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp)
            )
        """
        )

        # Training metrics table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS training_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id TEXT NOT NULL,
                epoch INTEGER NOT NULL,
                train_loss REAL NOT NULL,
                val_loss REAL NOT NULL,
                train_r2 REAL,
                val_r2 REAL,
                learning_rate REAL,
                gradient_norm REAL,
                buffer_size INTEGER,
                instability_detected BOOLEAN DEFAULT FALSE,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Experience buffer table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS experience_buffer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state BLOB NOT NULL,
                action INTEGER NOT NULL,
                reward REAL NOT NULL,
                next_state BLOB NOT NULL,
                done INTEGER NOT NULL,
                priority REAL DEFAULT 1.0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Predictions table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                bullish_probability REAL NOT NULL,
                bearish_probability REAL NOT NULL,
                neutral_probability REAL NOT NULL,
                confidence REAL NOT NULL,
                prediction TEXT NOT NULL,
                uncertainty REAL,
                model_version TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Security events table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                user_id TEXT,
                description TEXT NOT NULL,
                severity TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                metadata TEXT,  -- JSON
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # System configuration table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create indexes for performance
        self._create_indexes(conn)

        # Update schema version
        conn.execute(
            """
            INSERT OR REPLACE INTO system_config (key, value, description)
            VALUES ('schema_version', ?, 'Database schema version')
        """,
            (str(self.schema_version),),
        )

        conn.commit()

    def _create_indexes(self, conn: sqlite3.Connection):
        """Create database indexes for performance"""

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp ON market_data(symbol, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_training_metrics_model_epoch ON training_metrics(model_id, epoch)",
            "CREATE INDEX IF NOT EXISTS idx_training_metrics_timestamp ON training_metrics(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_experience_buffer_priority ON experience_buffer(priority)",
            "CREATE INDEX IF NOT EXISTS idx_experience_buffer_timestamp ON experience_buffer(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_predictions_symbol_timestamp ON predictions(symbol, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_security_events_type ON security_events(event_type)",
            "CREATE INDEX IF NOT EXISTS idx_security_events_timestamp ON security_events(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        ]

        for index_sql in indexes:
            conn.execute(index_sql)

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = self._get_connection()
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)

    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results"""

        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""

        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """Execute query with multiple parameter sets"""

        with self.get_connection() as conn:
            cursor = conn.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get table schema information"""

        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query)

    def get_table_count(self, table_name: str) -> int:
        """Get row count for table"""

        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query)
        return result[0]["count"] if result else 0

    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""

        try:
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            with self.get_connection() as conn:
                # Create backup
                backup_conn = sqlite3.connect(str(backup_path))

                # Configure backup connection
                if SQLCIPHER_AVAILABLE and self.encryption_key:
                    backup_conn.execute(f"PRAGMA key = '{self.encryption_key.hex()}'")
                    backup_conn.execute(
                        f"PRAGMA cipher_page_size = {self.cipher_page_size}"
                    )
                    backup_conn.execute(f"PRAGMA kdf_iter = {self.kdf_iterations}")

                # Perform backup
                conn.backup(backup_conn)
                backup_conn.close()

            logger.info(f"Database backup created: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            return False

    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup"""

        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False

            # Close all connections
            with self._pool_lock:
                for conn in self._connection_pool:
                    conn.close()
                self._connection_pool.clear()

            # Remove existing database
            if self.db_path.exists():
                self.db_path.unlink()

            # Restore from backup
            backup_conn = sqlite3.connect(str(backup_path))

            if SQLCIPHER_AVAILABLE and self.encryption_key:
                backup_conn.execute(f"PRAGMA key = '{self.encryption_key.hex()}'")
                backup_conn.execute(
                    f"PRAGMA cipher_page_size = {self.cipher_page_size}"
                )
                backup_conn.execute(f"PRAGMA kdf_iter = {self.kdf_iterations}")

            restore_conn = sqlite3.connect(str(self.db_path))
            self._configure_connection(restore_conn)

            backup_conn.backup(restore_conn)
            backup_conn.close()
            restore_conn.close()

            logger.info(f"Database restored from backup: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to restore database: {str(e)}")
            return False

    def vacuum_database(self) -> bool:
        """Vacuum database to reclaim space"""

        try:
            with self.get_connection() as conn:
                conn.execute("VACUUM")
                conn.commit()

            logger.info("Database vacuum completed")
            return True

        except Exception as e:
            logger.error(f"Failed to vacuum database: {str(e)}")
            return False

    def analyze_database(self) -> bool:
        """Analyze database for query optimization"""

        try:
            with self.get_connection() as conn:
                conn.execute("ANALYZE")
                conn.commit()

            logger.info("Database analysis completed")
            return True

        except Exception as e:
            logger.error(f"Failed to analyze database: {str(e)}")
            return False

    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""

        info = {
            "path": str(self.db_path),
            "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
            "encrypted": SQLCIPHER_AVAILABLE and self.encryption_key is not None,
            "schema_version": self.schema_version,
            "page_size": self.page_size,
            "journal_mode": self.journal_mode,
            "synchronous": self.synchronous,
            "tables": {},
        }

        # Get table information
        table_names = [
            "users",
            "market_data",
            "training_metrics",
            "experience_buffer",
            "predictions",
            "security_events",
            "system_config",
        ]

        for table_name in table_names:
            try:
                count = self.get_table_count(table_name)
                info["tables"][table_name] = {
                    "row_count": count,
                    "schema": self.get_table_info(table_name),
                }
            except Exception as e:
                logger.warning(f"Failed to get info for table {table_name}: {str(e)}")
                info["tables"][table_name] = {"error": str(e)}

        return info

    def migrate_from_postgresql(self, postgresql_config: Dict[str, str]) -> bool:
        """Migrate data from PostgreSQL to SQLite"""

        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor

            # Connect to PostgreSQL
            pg_conn = psycopg2.connect(**postgresql_config)
            pg_conn.autocommit = True

            # Get table list
            with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                """
                )
                tables = [row["table_name"] for row in cursor.fetchall()]

            # Migrate each table
            for table_name in tables:
                self._migrate_table(pg_conn, table_name)

            pg_conn.close()
            logger.info("PostgreSQL to SQLite migration completed")
            return True

        except Exception as e:
            logger.error(f"PostgreSQL migration failed: {str(e)}")
            return False

    def _migrate_table(self, pg_conn, table_name: str):
        """Migrate individual table from PostgreSQL to SQLite"""

        try:
            with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get table schema
                cursor.execute(
                    """
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """,
                    (table_name,),
                )

                columns = cursor.fetchall()

                # Get table data
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()

                if not rows:
                    logger.info(f"Table {table_name} is empty, skipping")
                    return

                # Convert rows to list of tuples
                data = [tuple(row.values()) for row in rows]

                # Create table in SQLite if it doesn't exist
                self._create_table_from_pg_schema(table_name, columns)

                # Insert data
                if data:
                    placeholders = ",".join(["?" for _ in columns])
                    query = (
                        f"INSERT OR REPLACE INTO {table_name} VALUES ({placeholders})"
                    )
                    self.execute_many(query, data)

                logger.info(f"Migrated {len(data)} rows from {table_name}")

        except Exception as e:
            logger.error(f"Failed to migrate table {table_name}: {str(e)}")

    def _create_table_from_pg_schema(
        self, table_name: str, columns: List[Dict[str, Any]]
    ):
        """Create SQLite table from PostgreSQL schema"""

        # Map PostgreSQL types to SQLite types
        type_mapping = {
            "integer": "INTEGER",
            "bigint": "INTEGER",
            "smallint": "INTEGER",
            "real": "REAL",
            "double precision": "REAL",
            "numeric": "REAL",
            "text": "TEXT",
            "varchar": "TEXT",
            "character varying": "TEXT",
            "timestamp without time zone": "TIMESTAMP",
            "timestamp with time zone": "TIMESTAMP",
            "boolean": "BOOLEAN",
            "json": "TEXT",
            "jsonb": "TEXT",
        }

        # Build CREATE TABLE statement
        column_defs = []
        for col in columns:
            col_name = col["column_name"]
            col_type = type_mapping.get(col["data_type"], "TEXT")

            if col_name == "id" and col_type == "INTEGER":
                col_def = f"{col_name} INTEGER PRIMARY KEY AUTOINCREMENT"
            else:
                col_def = f"{col_name} {col_type}"

                if col["is_nullable"] == "NO":
                    col_def += " NOT NULL"

            column_defs.append(col_def)

        create_sql = (
            f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
        )

        with self.get_connection() as conn:
            conn.execute(create_sql)
            conn.commit()

    def close_all_connections(self):
        """Close all database connections"""

        with self._pool_lock:
            for conn in self._connection_pool:
                conn.close()
            self._connection_pool.clear()

        logger.info("All database connections closed")

    def __del__(self):
        """Cleanup on destruction"""
        self.close_all_connections()
