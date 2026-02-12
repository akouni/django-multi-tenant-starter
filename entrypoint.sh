#!/bin/bash
set -e

: ${ENVIRONMENT:="development"}
echo "Running in $ENVIRONMENT environment"

# Initialize PostGIS extensions
init_postgis_db() {
    local db_name=$1
    echo "Initializing PostGIS for database: $db_name"
    PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$db_name" -c "CREATE EXTENSION IF NOT EXISTS postgis;"
    PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$db_name" -c "CREATE EXTENSION IF NOT EXISTS postgis_topology;"
    PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$db_name" -c "CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;"
    echo "All extensions created successfully"
}

# Wait for PostgreSQL
echo "Waiting for PostgreSQL to be ready..."
RETRY_COUNT=0
MAX_RETRIES=60

while ! PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' > /dev/null 2>&1; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "Failed to connect to PostgreSQL after $MAX_RETRIES attempts"
    exit 1
  fi
  >&2 echo "Postgres is unavailable - sleeping (attempt $RETRY_COUNT/$MAX_RETRIES)"
  sleep 2
done
>&2 echo "Postgres is up - executing command"

# Create PostGIS extensions
init_postgis_db "$POSTGRES_DB"

# Create directories
mkdir -p /app/staticfiles /app/media

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Migrations
echo "Creating any missing migrations..."
python manage.py makemigrations

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Migrations applied successfully."

# Setup public tenant
echo "Setting up public tenant..."
python << 'PYTHON_SCRIPT'
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from public_apps.customers.models import Client, Domain

def setup_public_tenant():
    print("Configuring public tenant...")

    try:
        public_tenant = Client.objects.filter(schema_name='public').first()

        if public_tenant:
            print("Public tenant already exists")
        else:
            print("Creating public tenant...")
            public_tenant = Client(
                schema_name='public',
                name='Multi-Tenant Starter - Public',
                type='public',
                is_active=True,
                active_languages=['en', 'fr'],
                default_language='en',
            )
            public_tenant.auto_create_schema = False
            public_tenant.auto_drop_schema = False
            public_tenant.save()
            print("Public tenant created")

        # Create domains
        domains_config = [
            ('localhost', True),
            ('127.0.0.1', False),
        ]

        domain_name = os.environ.get('DOMAIN_NAME', '')
        if domain_name and domain_name not in ('localhost', '127.0.0.1'):
            domains_config.append((domain_name, False))
            domains_config.append((f'www.{domain_name}', False))

        for dn, is_primary in domains_config:
            domain, created = Domain.objects.get_or_create(
                domain=dn,
                defaults={
                    'tenant': public_tenant,
                    'is_primary': is_primary,
                }
            )
            if created:
                print(f"Domain '{dn}' created")
            else:
                print(f"Domain '{dn}' already exists")

        print("Public tenant setup completed!")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

success = setup_public_tenant()
sys.exit(0 if success else 1)
PYTHON_SCRIPT

if [ $? -ne 0 ]; then
    echo "Warning: Failed to setup public tenant. Continuing anyway..."
else
    echo "Public tenant setup completed."
fi

# Create superuser in development
if [ "$ENVIRONMENT" = "development" ] && [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "Creating superuser for development..."
    python << 'PYTHON_SCRIPT'
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@localhost')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created")
else:
    print(f"Superuser '{username}' already exists")
PYTHON_SCRIPT
    echo "Superuser setup completed."
fi

# Start server
echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000
