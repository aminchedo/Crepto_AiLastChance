"""
Database Migration API for BOLT AI Neural Agent System.

Provides REST API endpoints for:
- PostgreSQL to SQLite migration
- Migration status tracking
- Data validation
- Rollback operations
- Migration reports
"""

import logging
from typing import Any, Dict, List, Optional

from db.migration_utils import MigrationManager
from db.sqlite_manager import SQLiteManager
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel

from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/migration", tags=["migration"])

# Global instances
sqlite_manager = SQLiteManager()
migration_manager = MigrationManager(sqlite_manager)


class MigrationRequest(BaseModel):
    """Migration request model"""

    postgresql_config: Dict[str, str]
    tables_to_migrate: Optional[List[str]] = None
    create_backup: bool = True
    validate_data: bool = True
    rollback_on_error: bool = True


class MigrationStatus(BaseModel):
    """Migration status model"""

    migration_id: str
    status: str
    progress_percentage: float
    current_table: Optional[str]
    tables_completed: int
    total_tables: int
    rows_migrated: int
    errors: List[str]
    warnings: List[str]


class MigrationReport(BaseModel):
    """Migration report model"""

    migration_id: str
    summary: Dict[str, Any]
    tables: List[Dict[str, Any]]
    failed_tables: List[Dict[str, Any]]
    errors: List[str]
    warnings: List[str]
    validation: Dict[str, Any]
    recommendations: List[str]


# In-memory migration status tracking
migration_statuses: Dict[str, Dict[str, Any]] = {}


@router.post("/start", response_model=Dict[str, str])
async def start_migration(request: MigrationRequest, background_tasks: BackgroundTasks):
    """
    Start PostgreSQL to SQLite migration.

    Args:
        request: Migration configuration
        background_tasks: Background task manager

    Returns:
        Migration ID for tracking
    """

    try:
        # Update migration manager configuration
        migration_manager.create_backup = request.create_backup
        migration_manager.validate_data = request.validate_data
        migration_manager.rollback_on_error = request.rollback_on_error

        # Start migration in background
        migration_id = migration_manager._generate_migration_id()

        # Initialize status tracking
        migration_statuses[migration_id] = {
            "migration_id": migration_id,
            "status": "starting",
            "progress_percentage": 0.0,
            "current_table": None,
            "tables_completed": 0,
            "total_tables": 0,
            "rows_migrated": 0,
            "errors": [],
            "warnings": [],
            "start_time": None,
            "end_time": None,
        }

        # Add background task
        background_tasks.add_task(
            _run_migration_background,
            migration_id,
            request.postgresql_config,
            request.tables_to_migrate,
        )

        logger.info(f"Migration started: {migration_id}")
        return {
            "migration_id": migration_id,
            "status": "started",
            "message": "Migration started in background",
        }

    except Exception as e:
        logger.error(f"Failed to start migration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{migration_id}", response_model=MigrationStatus)
async def get_migration_status(migration_id: str):
    """
    Get migration status.

    Args:
        migration_id: Migration identifier

    Returns:
        Current migration status
    """

    if migration_id not in migration_statuses:
        raise HTTPException(status_code=404, detail="Migration not found")

    status = migration_statuses[migration_id]

    return MigrationStatus(
        migration_id=migration_id,
        status=status["status"],
        progress_percentage=status["progress_percentage"],
        current_table=status["current_table"],
        tables_completed=status["tables_completed"],
        total_tables=status["total_tables"],
        rows_migrated=status["rows_migrated"],
        errors=status["errors"],
        warnings=status["warnings"],
    )


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_migration_history():
    """
    Get migration history.

    Returns:
        List of completed migrations
    """

    try:
        history = migration_manager.get_migration_history()
        return history

    except Exception as e:
        logger.error(f"Failed to get migration history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{migration_id}", response_model=MigrationReport)
async def get_migration_report(migration_id: str):
    """
    Get detailed migration report.

    Args:
        migration_id: Migration identifier

    Returns:
        Detailed migration report
    """

    try:
        report = migration_manager.create_migration_report(migration_id)

        if "error" in report:
            raise HTTPException(status_code=404, detail=report["error"])

        return MigrationReport(**report)

    except Exception as e:
        logger.error(f"Failed to get migration report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rollback/{migration_id}")
async def rollback_migration(migration_id: str):
    """
    Rollback migration to previous state.

    Args:
        migration_id: Migration identifier to rollback

    Returns:
        Rollback result
    """

    try:
        if migration_id not in migration_statuses:
            raise HTTPException(status_code=404, detail="Migration not found")

        # Check if migration is still running
        status = migration_statuses[migration_id]
        if status["status"] in ["starting", "in_progress"]:
            raise HTTPException(
                status_code=400, detail="Cannot rollback running migration"
            )

        # Perform rollback
        migration_manager._rollback_migration(migration_id)

        # Update status
        status["status"] = "rolled_back"
        status["end_time"] = datetime.now().isoformat()

        logger.info(f"Migration rolled back: {migration_id}")
        return {
            "migration_id": migration_id,
            "status": "rolled_back",
            "message": "Migration rolled back successfully",
        }

    except Exception as e:
        logger.error(f"Failed to rollback migration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/database/info")
async def get_database_info():
    """
    Get SQLite database information.

    Returns:
        Database information and statistics
    """

    try:
        info = sqlite_manager.get_database_info()
        return info

    except Exception as e:
        logger.error(f"Failed to get database info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/database/backup")
async def create_database_backup(backup_path: Optional[str] = None):
    """
    Create database backup.

    Args:
        backup_path: Optional custom backup path

    Returns:
        Backup result
    """

    try:
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups/crypto_ai_backup_{timestamp}.db"

        success = sqlite_manager.backup_database(backup_path)

        if success:
            return {
                "status": "success",
                "backup_path": backup_path,
                "message": "Backup created successfully",
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create backup")

    except Exception as e:
        logger.error(f"Failed to create backup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/database/restore")
async def restore_database(backup_path: str):
    """
    Restore database from backup.

    Args:
        backup_path: Path to backup file

    Returns:
        Restore result
    """

    try:
        success = sqlite_manager.restore_database(backup_path)

        if success:
            return {
                "status": "success",
                "backup_path": backup_path,
                "message": "Database restored successfully",
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to restore database")

    except Exception as e:
        logger.error(f"Failed to restore database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/database/vacuum")
async def vacuum_database():
    """
    Vacuum database to reclaim space.

    Returns:
        Vacuum result
    """

    try:
        success = sqlite_manager.vacuum_database()

        if success:
            return {"status": "success", "message": "Database vacuum completed"}
        else:
            raise HTTPException(status_code=500, detail="Failed to vacuum database")

    except Exception as e:
        logger.error(f"Failed to vacuum database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/database/analyze")
async def analyze_database():
    """
    Analyze database for query optimization.

    Returns:
        Analysis result
    """

    try:
        success = sqlite_manager.analyze_database()

        if success:
            return {"status": "success", "message": "Database analysis completed"}
        else:
            raise HTTPException(status_code=500, detail="Failed to analyze database")

    except Exception as e:
        logger.error(f"Failed to analyze database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables")
async def get_table_list():
    """
    Get list of database tables.

    Returns:
        List of tables with row counts
    """

    try:
        tables = [
            "users",
            "market_data",
            "training_metrics",
            "experience_buffer",
            "predictions",
            "security_events",
            "system_config",
        ]

        table_info = []
        for table_name in tables:
            try:
                count = sqlite_manager.get_table_count(table_name)
                schema = sqlite_manager.get_table_info(table_name)

                table_info.append(
                    {"name": table_name, "row_count": count, "columns": len(schema)}
                )
            except Exception as e:
                table_info.append({"name": table_name, "error": str(e)})

        return {"tables": table_info, "total_tables": len(tables)}

    except Exception as e:
        logger.error(f"Failed to get table list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables/{table_name}")
async def get_table_info(table_name: str):
    """
    Get detailed information about a specific table.

    Args:
        table_name: Name of the table

    Returns:
        Table schema and statistics
    """

    try:
        # Get table schema
        schema = sqlite_manager.get_table_info(table_name)

        # Get row count
        count = sqlite_manager.get_table_count(table_name)

        # Get sample data
        sample_query = f"SELECT * FROM {table_name} LIMIT 5"
        sample_data = sqlite_manager.execute_query(sample_query)

        return {
            "name": table_name,
            "row_count": count,
            "schema": schema,
            "sample_data": sample_data,
        }

    except Exception as e:
        logger.error(f"Failed to get table info for {table_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def _run_migration_background(
    migration_id: str,
    postgresql_config: Dict[str, str],
    tables_to_migrate: Optional[List[str]],
):
    """Run migration in background thread"""

    try:
        # Update status
        migration_statuses[migration_id]["status"] = "in_progress"
        migration_statuses[migration_id]["start_time"] = datetime.now().isoformat()

        # Run migration
        result = migration_manager.migrate_from_postgresql(
            postgresql_config=postgresql_config, tables_to_migrate=tables_to_migrate
        )

        # Update final status
        migration_statuses[migration_id].update(
            {
                "status": result["status"],
                "end_time": result["end_time"],
                "rows_migrated": result["total_rows"],
                "errors": result["errors"],
                "warnings": result["warnings"],
                "progress_percentage": 100.0,
            }
        )

        logger.info(f"Background migration completed: {migration_id}")

    except Exception as e:
        # Update error status
        migration_statuses[migration_id].update(
            {
                "status": "failed",
                "end_time": datetime.now().isoformat(),
                "errors": [str(e)],
                "progress_percentage": 100.0,
            }
        )

        logger.error(f"Background migration failed: {migration_id} - {str(e)}")


# Import datetime for background task
from datetime import datetime
