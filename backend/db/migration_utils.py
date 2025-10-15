"""
Database Migration Utilities for BOLT AI Neural Agent System.

Provides comprehensive migration tools for:
- PostgreSQL to SQLite migration
- Schema versioning and updates
- Data validation and integrity checks
- Rollback capabilities
- Migration progress tracking
"""

import hashlib
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor

from .sqlite_manager import SQLiteManager

logger = logging.getLogger(__name__)


class MigrationManager:
    """
    Database migration manager with comprehensive migration capabilities.

    Features:
    - PostgreSQL to SQLite migration
    - Schema versioning
    - Data validation
    - Rollback support
    - Progress tracking
    - Integrity checks
    """

    def __init__(self, sqlite_manager: SQLiteManager):
        self.sqlite_manager = sqlite_manager
        self.migration_log = []
        self.migration_metadata = {}

        # Migration configuration
        self.batch_size = 1000
        self.validate_data = True
        self.create_backup = True
        self.rollback_on_error = True

    def migrate_from_postgresql(
        self,
        postgresql_config: Dict[str, str],
        tables_to_migrate: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Migrate data from PostgreSQL to SQLite.

        Args:
            postgresql_config: PostgreSQL connection configuration
            tables_to_migrate: Specific tables to migrate (None for all)

        Returns:
            Migration result summary
        """

        migration_id = self._generate_migration_id()
        start_time = datetime.now()

        result = {
            "migration_id": migration_id,
            "start_time": start_time.isoformat(),
            "status": "in_progress",
            "tables_migrated": [],
            "tables_failed": [],
            "total_rows": 0,
            "errors": [],
            "warnings": [],
        }

        try:
            # Create backup if requested
            if self.create_backup:
                backup_path = f"backups/pre_migration_{migration_id}.db"
                if not self.sqlite_manager.backup_database(backup_path):
                    result["warnings"].append("Failed to create pre-migration backup")

            # Connect to PostgreSQL
            pg_conn = psycopg2.connect(**postgresql_config)
            pg_conn.autocommit = True

            # Get tables to migrate
            if tables_to_migrate is None:
                tables_to_migrate = self._get_postgresql_tables(pg_conn)

            # Migrate each table
            for table_name in tables_to_migrate:
                try:
                    table_result = self._migrate_table(pg_conn, table_name)
                    result["tables_migrated"].append(table_result)
                    result["total_rows"] += table_result["rows_migrated"]

                except Exception as e:
                    error_msg = f"Failed to migrate table {table_name}: {str(e)}"
                    result["tables_failed"].append(
                        {"table": table_name, "error": error_msg}
                    )
                    result["errors"].append(error_msg)
                    logger.error(error_msg)

            pg_conn.close()

            # Validate migration if requested
            if self.validate_data:
                validation_result = self._validate_migration(
                    postgresql_config, tables_to_migrate
                )
                result["validation"] = validation_result

                if not validation_result["valid"]:
                    result["warnings"].extend(validation_result["errors"])

            # Update migration status
            result["status"] = (
                "completed" if not result["errors"] else "completed_with_errors"
            )
            result["end_time"] = datetime.now().isoformat()
            result["duration_seconds"] = (datetime.now() - start_time).total_seconds()

            # Log migration
            self._log_migration(result)

            logger.info(f"Migration completed: {migration_id}")
            return result

        except Exception as e:
            result["status"] = "failed"
            result["end_time"] = datetime.now().isoformat()
            result["duration_seconds"] = (datetime.now() - start_time).total_seconds()
            result["errors"].append(f"Migration failed: {str(e)}")

            # Rollback if requested
            if self.rollback_on_error:
                self._rollback_migration(migration_id)

            logger.error(f"Migration failed: {migration_id} - {str(e)}")
            return result

    def _get_postgresql_tables(self, pg_conn) -> List[str]:
        """Get list of tables from PostgreSQL"""

        with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            )
            return [row["table_name"] for row in cursor.fetchall()]

    def _migrate_table(self, pg_conn, table_name: str) -> Dict[str, Any]:
        """Migrate individual table with progress tracking"""

        table_result = {
            "table": table_name,
            "rows_migrated": 0,
            "start_time": datetime.now().isoformat(),
            "errors": [],
            "warnings": [],
        }

        try:
            with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get table schema
                schema = self._get_table_schema(pg_conn, table_name)

                # Get row count
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                total_rows = cursor.fetchone()["count"]

                if total_rows == 0:
                    table_result["warnings"].append("Table is empty")
                    table_result["end_time"] = datetime.now().isoformat()
                    return table_result

                # Create table in SQLite
                self._create_sqlite_table(table_name, schema)

                # Migrate data in batches
                offset = 0
                while offset < total_rows:
                    batch_data = self._get_table_batch(
                        pg_conn, table_name, offset, self.batch_size
                    )

                    if batch_data:
                        self._insert_batch_to_sqlite(table_name, batch_data, schema)
                        table_result["rows_migrated"] += len(batch_data)

                    offset += self.batch_size

                    # Log progress
                    progress = (offset / total_rows) * 100
                    logger.info(
                        f"Migrated {table_result['rows_migrated']}/{total_rows} rows from {table_name} ({progress:.1f}%)"
                    )

                table_result["end_time"] = datetime.now().isoformat()
                table_result["duration_seconds"] = (
                    datetime.now() - datetime.fromisoformat(table_result["start_time"])
                ).total_seconds()

                logger.info(
                    f"Table migration completed: {table_name} ({table_result['rows_migrated']} rows)"
                )
                return table_result

        except Exception as e:
            table_result["errors"].append(str(e))
            table_result["end_time"] = datetime.now().isoformat()
            raise

    def _get_table_schema(self, pg_conn, table_name: str) -> List[Dict[str, Any]]:
        """Get table schema from PostgreSQL"""

        with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """,
                (table_name,),
            )

            return cursor.fetchall()

    def _create_sqlite_table(self, table_name: str, schema: List[Dict[str, Any]]):
        """Create SQLite table from PostgreSQL schema"""

        # Type mapping
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
            "bytea": "BLOB",
        }

        # Build column definitions
        column_defs = []
        for col in schema:
            col_name = col["column_name"]
            col_type = type_mapping.get(col["data_type"], "TEXT")

            # Handle special cases
            if col_name == "id" and col_type == "INTEGER":
                col_def = f"{col_name} INTEGER PRIMARY KEY AUTOINCREMENT"
            else:
                col_def = f"{col_name} {col_type}"

                if col["is_nullable"] == "NO":
                    col_def += " NOT NULL"

                if col["column_default"]:
                    col_def += f" DEFAULT {col['column_default']}"

            column_defs.append(col_def)

        # Create table
        create_sql = (
            f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
        )

        with self.sqlite_manager.get_connection() as conn:
            conn.execute(create_sql)
            conn.commit()

    def _get_table_batch(
        self, pg_conn, table_name: str, offset: int, limit: int
    ) -> List[Tuple]:
        """Get batch of data from PostgreSQL table"""

        with pg_conn.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM {table_name} ORDER BY id LIMIT %s OFFSET %s",
                (limit, offset),
            )
            return cursor.fetchall()

    def _insert_batch_to_sqlite(
        self, table_name: str, batch_data: List[Tuple], schema: List[Dict[str, Any]]
    ):
        """Insert batch of data into SQLite table"""

        if not batch_data:
            return

        # Get column names
        column_names = [col["column_name"] for col in schema]

        # Create placeholders
        placeholders = ",".join(["?" for _ in column_names])
        query = f"INSERT OR REPLACE INTO {table_name} ({','.join(column_names)}) VALUES ({placeholders})"

        # Convert data to proper types
        converted_data = []
        for row in batch_data:
            converted_row = []
            for i, value in enumerate(row):
                if value is None:
                    converted_row.append(None)
                elif schema[i]["data_type"] in ["json", "jsonb"]:
                    converted_row.append(
                        json.dumps(value) if isinstance(value, dict) else str(value)
                    )
                elif schema[i]["data_type"] == "bytea":
                    converted_row.append(value)
                else:
                    converted_row.append(value)
            converted_data.append(tuple(converted_row))

        # Insert data
        self.sqlite_manager.execute_many(query, converted_data)

    def _validate_migration(
        self, postgresql_config: Dict[str, str], tables: List[str]
    ) -> Dict[str, Any]:
        """Validate migrated data against PostgreSQL source"""

        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "table_validations": {},
        }

        try:
            pg_conn = psycopg2.connect(**postgresql_config)
            pg_conn.autocommit = True

            for table_name in tables:
                table_validation = self._validate_table(pg_conn, table_name)
                validation_result["table_validations"][table_name] = table_validation

                if not table_validation["valid"]:
                    validation_result["valid"] = False
                    validation_result["errors"].extend(table_validation["errors"])

                if table_validation["warnings"]:
                    validation_result["warnings"].extend(table_validation["warnings"])

            pg_conn.close()

        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation failed: {str(e)}")

        return validation_result

    def _validate_table(self, pg_conn, table_name: str) -> Dict[str, Any]:
        """Validate individual table migration"""

        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "row_count_match": False,
            "data_integrity": False,
        }

        try:
            # Check row count
            with pg_conn.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                pg_count = cursor.fetchone()[0]

            sqlite_count = self.sqlite_manager.get_table_count(table_name)

            if pg_count == sqlite_count:
                validation["row_count_match"] = True
            else:
                validation["valid"] = False
                validation["errors"].append(
                    f"Row count mismatch: PostgreSQL={pg_count}, SQLite={sqlite_count}"
                )

            # Check data integrity (sample check)
            if validation["row_count_match"]:
                validation["data_integrity"] = self._check_data_integrity(
                    pg_conn, table_name
                )

                if not validation["data_integrity"]:
                    validation["valid"] = False
                    validation["errors"].append("Data integrity check failed")

        except Exception as e:
            validation["valid"] = False
            validation["errors"].append(f"Table validation failed: {str(e)}")

        return validation

    def _check_data_integrity(self, pg_conn, table_name: str) -> bool:
        """Check data integrity by comparing sample records"""

        try:
            # Get sample records from PostgreSQL
            with pg_conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table_name} ORDER BY id LIMIT 10")
                pg_sample = cursor.fetchall()

            if not pg_sample:
                return True  # Empty table

            # Get corresponding records from SQLite
            sample_ids = [row[0] for row in pg_sample]  # Assuming first column is ID
            placeholders = ",".join(["?" for _ in sample_ids])
            query = (
                f"SELECT * FROM {table_name} WHERE id IN ({placeholders}) ORDER BY id"
            )

            sqlite_sample = self.sqlite_manager.execute_query(query, tuple(sample_ids))

            # Compare samples
            if len(pg_sample) != len(sqlite_sample):
                return False

            # Convert SQLite rows to tuples for comparison
            sqlite_tuples = [tuple(row.values()) for row in sqlite_sample]

            # Compare each record
            for pg_row, sqlite_row in zip(pg_sample, sqlite_tuples):
                if len(pg_row) != len(sqlite_row):
                    return False

                for pg_val, sqlite_val in zip(pg_row, sqlite_row):
                    if pg_val != sqlite_val:
                        return False

            return True

        except Exception as e:
            logger.error(f"Data integrity check failed for {table_name}: {str(e)}")
            return False

    def _rollback_migration(self, migration_id: str):
        """Rollback migration to previous state"""

        try:
            backup_path = f"backups/pre_migration_{migration_id}.db"
            if Path(backup_path).exists():
                self.sqlite_manager.restore_database(backup_path)
                logger.info(f"Migration rolled back: {migration_id}")
            else:
                logger.warning(f"Backup not found for rollback: {backup_path}")

        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")

    def _generate_migration_id(self) -> str:
        """Generate unique migration ID"""

        timestamp = datetime.now().isoformat()
        hash_obj = hashlib.md5(timestamp.encode())
        return hash_obj.hexdigest()[:8]

    def _log_migration(self, result: Dict[str, Any]):
        """Log migration result"""

        self.migration_log.append(result)

        # Keep only last 100 migrations
        if len(self.migration_log) > 100:
            self.migration_log = self.migration_log[-100:]

        # Save to file
        log_file = Path("logs/migration_log.json")
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, "w") as f:
            json.dump(self.migration_log, f, indent=2)

    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get migration history"""

        return self.migration_log

    def get_migration_status(self, migration_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific migration"""

        for migration in self.migration_log:
            if migration["migration_id"] == migration_id:
                return migration

        return None

    def create_migration_report(self, migration_id: str) -> Dict[str, Any]:
        """Create detailed migration report"""

        migration = self.get_migration_status(migration_id)
        if not migration:
            return {"error": "Migration not found"}

        report = {
            "migration_id": migration_id,
            "summary": {
                "status": migration["status"],
                "duration_seconds": migration.get("duration_seconds", 0),
                "total_rows": migration["total_rows"],
                "tables_migrated": len(migration["tables_migrated"]),
                "tables_failed": len(migration["tables_failed"]),
                "errors": len(migration["errors"]),
                "warnings": len(migration["warnings"]),
            },
            "tables": migration["tables_migrated"],
            "failed_tables": migration["tables_failed"],
            "errors": migration["errors"],
            "warnings": migration["warnings"],
            "validation": migration.get("validation", {}),
            "recommendations": self._generate_recommendations(migration),
        }

        return report

    def _generate_recommendations(self, migration: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on migration results"""

        recommendations = []

        if migration["status"] == "completed_with_errors":
            recommendations.append("Review and fix migration errors before proceeding")

        if migration["warnings"]:
            recommendations.append(
                "Address migration warnings to ensure data integrity"
            )

        if migration.get("validation", {}).get("valid", True) == False:
            recommendations.append(
                "Data validation failed - verify migrated data manually"
            )

        if migration["tables_failed"]:
            recommendations.append("Retry migration for failed tables")

        if not recommendations:
            recommendations.append(
                "Migration completed successfully - no action required"
            )

        return recommendations
