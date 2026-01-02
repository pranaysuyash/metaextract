#!/bin/bash
# Database Initialization Script
# Runs automatically when PostgreSQL container starts

set -e

echo "🔧 Starting MetaExtract database initialization..."

# Wait for PostgreSQL to be ready
until pg_isready -U metaextract -d metaextract; do
  echo "⏳ Waiting for PostgreSQL to be ready..."
  sleep 2
done

echo "✅ PostgreSQL is ready"

# Run migrations in order
echo "📊 Running database migrations..."

if [ -d /docker-entrypoint-initdb.d ]; then
  for migration in /docker-entrypoint-initdb.d/*.sql; do
    if [ -f "$migration" ]; then
      echo "📄 Running migration: $(basename "$migration")"
      psql -U metaextract -d metaextract -f "$migration"
      echo "✅ Migration completed: $(basename "$migration")"
    fi
  done
fi

echo "🎉 Database initialization complete!"
echo "📊 Database schema is ready for MetaExtract v4.0"