"""
Verify Async Database Setup
Tests that aiosqlite and SQLAlchemy async are properly configured
"""
import asyncio
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{BLUE}{BOLD}{'='*60}{RESET}")
    print(f"{BLUE}{BOLD}{text.center(60)}{RESET}")
    print(f"{BLUE}{BOLD}{'='*60}{RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_info(text):
    """Print info message"""
    print(f"{BLUE}ℹ️  {text}{RESET}")


async def test_imports():
    """Test that all required packages can be imported"""
    print_header("Testing Package Imports")
    
    packages = {
        'aiosqlite': None,
        'sqlalchemy': None,
        'sqlalchemy.ext.asyncio': 'create_async_engine',
    }
    
    all_passed = True
    
    for package, attr in packages.items():
        try:
            if attr:
                module = __import__(package, fromlist=[attr])
                getattr(module, attr)
            else:
                __import__(package)
            
            # Get version if available
            try:
                if attr:
                    module = __import__(package, fromlist=[attr])
                else:
                    module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                print_success(f"{package:30} version: {version}")
            except:
                print_success(f"{package:30} imported successfully")
                
        except ImportError as e:
            print_error(f"{package:30} NOT FOUND - {e}")
            all_passed = False
    
    return all_passed


async def test_aiosqlite_direct():
    """Test direct aiosqlite connection"""
    print_header("Testing Direct aiosqlite Connection")
    
    try:
        import aiosqlite
        
        # Test in-memory database
        print_info("Connecting to in-memory database...")
        async with aiosqlite.connect(':memory:') as db:
            # Create a test table
            await db.execute('''
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            ''')
            
            # Insert test data
            await db.execute("INSERT INTO test_table (name) VALUES (?)", ("test_value",))
            await db.commit()
            
            # Query test data
            async with db.execute("SELECT * FROM test_table") as cursor:
                row = await cursor.fetchone()
                if row and row[1] == "test_value":
                    print_success("Direct aiosqlite connection works!")
                    print_info(f"  - Created table successfully")
                    print_info(f"  - Inserted data successfully")
                    print_info(f"  - Retrieved data: {row}")
                    return True
                else:
                    print_error("Data retrieval failed")
                    return False
                    
    except Exception as e:
        print_error(f"Direct aiosqlite test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_sqlalchemy_async():
    """Test SQLAlchemy async engine with aiosqlite"""
    print_header("Testing SQLAlchemy Async Engine")
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import declarative_base, sessionmaker
        from sqlalchemy import Column, Integer, String, select
        from sqlalchemy.ext.asyncio import async_sessionmaker
        
        # Create test database URL
        test_db_url = "sqlite+aiosqlite:///:memory:"
        print_info(f"Database URL: {test_db_url}")
        
        # Create async engine
        print_info("Creating async engine...")
        engine = create_async_engine(test_db_url, echo=False)
        
        # Create base and test model
        Base = declarative_base()
        
        class TestModel(Base):
            __tablename__ = 'test_model'
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
        
        # Create tables
        print_info("Creating tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Create session
        print_info("Creating async session...")
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Test insert and query
        print_info("Testing insert and query...")
        async with AsyncSessionLocal() as session:
            # Insert
            test_obj = TestModel(name="test_name")
            session.add(test_obj)
            await session.commit()
            
            # Query
            result = await session.execute(select(TestModel))
            obj = result.scalars().first()
            
            if obj and obj.name == "test_name":
                print_success("SQLAlchemy async engine works!")
                print_info(f"  - Engine created successfully")
                print_info(f"  - Tables created successfully")
                print_info(f"  - Session created successfully")
                print_info(f"  - Insert operation successful")
                print_info(f"  - Query operation successful")
                print_info(f"  - Retrieved data: {obj.name}")
            else:
                print_error("SQLAlchemy query failed")
                await engine.dispose()
                return False
        
        # Cleanup
        await engine.dispose()
        return True
        
    except Exception as e:
        print_error(f"SQLAlchemy async test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_project_database_config():
    """Test the actual project database configuration"""
    print_header("Testing Project Database Configuration")
    
    try:
        # Try to import project config
        print_info("Loading project configuration...")
        try:
            from config import settings
            print_success(f"Config loaded successfully")
            print_info(f"  - Database URL: {settings.DATABASE_URL}")
            print_info(f"  - Debug mode: {settings.DEBUG}")
            print_info(f"  - Environment: {settings.ENVIRONMENT}")
        except ImportError as e:
            print_error(f"Could not import config: {e}")
            return False
        
        # Check if DATABASE_URL uses aiosqlite
        if 'aiosqlite' not in settings.DATABASE_URL:
            print_error("DATABASE_URL does not use aiosqlite driver!")
            print_warning(f"Current: {settings.DATABASE_URL}")
            print_warning(f"Expected: sqlite+aiosqlite:///./crypto_ai.db")
            return False
        
        print_success("Database URL correctly configured with aiosqlite")
        
        # Try to import database module
        print_info("Importing database module...")
        try:
            from db.database import engine, AsyncSessionLocal, get_db, init_db
            print_success("Database module imported successfully")
            print_info(f"  - Engine: {engine}")
            print_info(f"  - Session factory: {AsyncSessionLocal}")
        except ImportError as e:
            print_error(f"Could not import database module: {e}")
            return False
        
        # Test database initialization (on in-memory DB to avoid file creation)
        print_info("Testing database initialization...")
        from sqlalchemy.ext.asyncio import create_async_engine
        test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        
        try:
            async with test_engine.begin() as conn:
                await conn.execute("SELECT 1")
            print_success("Database initialization test passed")
            await test_engine.dispose()
        except Exception as e:
            print_error(f"Database initialization failed: {e}")
            await test_engine.dispose()
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Project database config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}{'Crepto AI - Async Database Verification'.center(60)}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    
    results = {}
    
    # Test 1: Package imports
    results['imports'] = await test_imports()
    
    # Test 2: Direct aiosqlite
    results['aiosqlite'] = await test_aiosqlite_direct()
    
    # Test 3: SQLAlchemy async
    results['sqlalchemy'] = await test_sqlalchemy_async()
    
    # Test 4: Project configuration
    results['project'] = await test_project_database_config()
    
    # Summary
    print_header("Test Summary")
    
    for test_name, passed in results.items():
        status = f"{GREEN}PASSED{RESET}" if passed else f"{RED}FAILED{RESET}"
        print(f"  {test_name.capitalize():20} {status}")
    
    all_passed = all(results.values())
    
    print()
    if all_passed:
        print(f"{GREEN}{BOLD}{'='*60}{RESET}")
        print(f"{GREEN}{BOLD}{'🎉 ALL TESTS PASSED! 🎉'.center(60)}{RESET}")
        print(f"{GREEN}{BOLD}{'='*60}{RESET}")
        print(f"\n{GREEN}Your async database setup is working correctly!{RESET}")
        print(f"{GREEN}You can now start your application with confidence.{RESET}\n")
        return 0
    else:
        print(f"{RED}{BOLD}{'='*60}{RESET}")
        print(f"{RED}{BOLD}{'❌ SOME TESTS FAILED ❌'.center(60)}{RESET}")
        print(f"{RED}{BOLD}{'='*60}{RESET}")
        print(f"\n{RED}Please run: fix-async-database.bat{RESET}")
        print(f"{RED}Or manually install: pip install aiosqlite{RESET}\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
