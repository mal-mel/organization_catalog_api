#!/bin/bash
set -e

echo "🧪 Starting tests..."

echo "⏳ Waiting for database..."
MAX_RETRIES=30
RETRY_COUNT=0
RETRY_DELAY=2

until python scripts/wait_for_db.py; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "📊 Database is unavailable - sleeping (attempt $RETRY_COUNT/$MAX_RETRIES)"

    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "❌ Maximum number of retries ($MAX_RETRIES) reached. Exiting."
        exit 1
    fi

    sleep $RETRY_DELAY
done

echo "✅ Database is ready!"

echo "📝 Running migrations..."
alembic upgrade head

echo "🎲 Seeding test data..."
python scripts/seed_db.py

echo "🚀 Running tests with pytest..."
if pytest tests/ -v --tb=short; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Tests failed!"
    exit 1
fi