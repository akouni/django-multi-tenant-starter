#!/usr/bin/env bash
# Render.com build script
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Generate migrations (not committed to repo — starter template)
python manage.py makemigrations customers main users geomap

# Apply migrations to shared/public schema
python manage.py migrate_schemas --shared

# Collect static files with whitenoise
python manage.py collectstatic --noinput

# Setup public tenant + demo data
python << 'PYTHON_SCRIPT'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from public_apps.customers.models import Client, Domain

domain_name = os.environ.get('DOMAIN_NAME', '')
render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')

# Create public tenant if needed
if not Client.objects.filter(schema_name='public').exists():
    print("Creating public tenant...")
    tenant = Client(
        schema_name='public',
        name='Multi-Tenant Starter - Public',
        type='public',
        is_active=True,
        active_languages=['en', 'fr'],
        default_language='en',
    )
    tenant.auto_create_schema = False
    tenant.auto_drop_schema = False
    tenant.save()

    # Add domains
    for dn in ['localhost', '127.0.0.1']:
        Domain.objects.get_or_create(domain=dn, defaults={'tenant': tenant, 'is_primary': (dn == 'localhost')})

    if render_host:
        Domain.objects.get_or_create(domain=render_host, defaults={'tenant': tenant, 'is_primary': False})

    if domain_name:
        Domain.objects.get_or_create(domain=domain_name, defaults={'tenant': tenant, 'is_primary': True})
        Domain.objects.filter(domain='localhost').update(is_primary=False)
        Domain.objects.filter(domain=domain_name).update(is_primary=True)

    print("Public tenant created.")
else:
    print("Public tenant already exists.")
    # Ensure render host domain exists (hostname may change between deploys)
    tenant = Client.objects.get(schema_name='public')
    if render_host:
        Domain.objects.get_or_create(domain=render_host, defaults={'tenant': tenant, 'is_primary': False})
    if domain_name:
        Domain.objects.get_or_create(domain=domain_name, defaults={'tenant': tenant, 'is_primary': True})
PYTHON_SCRIPT

# Create demo data (tenants, users, locations, teams)
python manage.py create_demo_data

# Update demo tenant domains to match Render/custom domain
python << 'PYTHON_SCRIPT'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from public_apps.customers.models import Domain

domain_name = os.environ.get('DOMAIN_NAME', '')
render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')

# Pick the best base domain: custom domain > render hostname > localhost
base_domain = domain_name or render_host or 'localhost'

updates = {
    'acme.localhost': f'acme.{base_domain}',
    'helvetia.localhost': f'helvetia.{base_domain}',
    'geneva.localhost': f'geneva.{base_domain}',
}

for old, new in updates.items():
    if old == new:
        continue
    updated = Domain.objects.filter(domain=old).update(domain=new)
    if updated:
        print(f'  {old} -> {new}')
    else:
        # Domain may already be updated from a previous build
        if Domain.objects.filter(domain=new).exists():
            print(f'  {new} (already set)')
        else:
            print(f'  {old} not found, skipping')

print("Demo domains updated.")
PYTHON_SCRIPT

echo "Build complete."
