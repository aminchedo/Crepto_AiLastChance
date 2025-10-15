#!/usr/bin/env python3
"""Test script to verify configuration loading"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

print("Environment variables:")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")
print(f"ALGORITHM: {os.getenv('ALGORITHM')}")
print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')}")

# Test Pydantic settings
try:
    from pydantic_settings import BaseSettings
    from pydantic import ConfigDict
    
    class TestSettings(BaseSettings):
        model_config = ConfigDict(
            env_file="../.env",
            case_sensitive=True,
            extra="ignore"
        )
        
        DATABASE_URL: str
        SECRET_KEY: str
        ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    settings = TestSettings()
    print("\nPydantic settings loaded successfully:")
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    print(f"SECRET_KEY: {settings.SECRET_KEY}")
    print(f"ALGORITHM: {settings.ALGORITHM}")
    print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
    
except Exception as e:
    print(f"\nPydantic error: {e}")
