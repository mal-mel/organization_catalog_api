#!/usr/bin/env python3
import sys
import os
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings


def wait_for_db():
    try:
        conn = psycopg2.connect(
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        conn.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


if __name__ == "__main__":
    max_retries = 30
    for i in range(max_retries):
        if wait_for_db():
            print("Database is ready!")
            sys.exit(0)
        print(f"Retry {i + 1}/{max_retries}...")
        time.sleep(2)

    print("Failed to connect to database after all retries")
    sys.exit(1)