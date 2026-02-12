# Django Multi-Tenant Starter

A production-ready Django boilerplate for building multi-tenant SaaS applications using PostgreSQL schema isolation.

Each tenant gets its own PostgreSQL schema, ensuring complete data separation while sharing a single database and codebase.

## Features

- **Schema-based multi-tenancy** — powered by [django-tenants](https://github.com/django-tenants/django-tenants), each tenant runs in its own PostgreSQL schema
- **Public showcase site** — landing page, about, and contact pages (Bootstrap 5)
- **Tenant client space** — dashboard, user management, and geographic mapping
- **Dual admin panels** — separate Jazzmin-themed admin interfaces for public and tenant schemas
- **Authentication & MFA** — django-allauth with TOTP two-factor authentication
- **GIS support** — PostGIS-backed location management with OpenLayers maps
- **REST API** — Django REST Framework with GeoJSON serializers and OpenAPI docs (drf-spectacular)
- **Role-based access** — hierarchical roles with granular permission flags
- **Internationalization** — English and French with django-modeltranslation
- **Docker-ready** — docker-compose setup with PostGIS, Redis, and Django

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 5.2 |
| Multi-tenancy | django-tenants |
| Database | PostgreSQL 17 + PostGIS 3.5 |
| Cache | Redis 7 |
| Auth | django-allauth + MFA (TOTP) |
| API | Django REST Framework + drf-spectacular |
| GIS | PostGIS, django.contrib.gis, rest_framework_gis |
| Admin | Jazzmin |
| Frontend | Bootstrap 5 (CDN) |
| i18n | django-modeltranslation (en, fr) |
| Storage | S3-compatible (optional) |

## Project Structure

```
django-multi-tenant-starter/
├── core/                      # Django settings, middleware, URL routing
│   ├── settings.py            # Multi-tenant config, all env-var driven
│   ├── middleware.py           # Tenant type, Jazzmin, language middleware
│   ├── admin_utils.py         # Admin registration decorators
│   ├── public_urls.py         # Public schema URL routing
│   └── tenant_urls.py         # Tenant schema URL routing
├── public_apps/
│   ├── customers/             # Tenant (Client/Domain) models + management
│   │   └── management/commands/
│   │       └── create_tenant.py
│   └── main/                  # Public site views (home, about, contact)
├── tenant_apps/
│   ├── users/                 # CustomUser, Role, UserProfile, Teams
│   └── geomap/                # Location, LocationType, MapLayer (PostGIS)
├── templates/                 # Bootstrap 5 templates (public + tenant)
├── static/                    # CSS, JS, favicon
├── Dockerfile                 # Python 3.13 + GDAL
├── Dockerfile.postgres        # PostGIS 17-3.5
├── docker-compose.yml         # 3 services: db, redis, web
├── entrypoint.sh              # Auto-migration, public tenant setup
└── requirements.txt           # ~30 dependencies
```

## Prerequisites

- **Docker & Docker Compose** (recommended), or:
- Python 3.13+
- PostgreSQL 17 with PostGIS
- Redis
- GDAL/GEOS/PROJ system libraries

## Quick Start (Docker)

```bash
# 1. Clone the repository
git clone https://github.com/akouni/django-multi-tenant-starter.git
cd django-multi-tenant-starter

# 2. Copy and configure environment
cp .env.example .env

# 3. Build and start
docker-compose up --build

# 4. Open in your browser
# Public site:  http://localhost:8000
# Public admin: http://localhost:8000/en/admin/
```

The entrypoint script automatically:
- Initializes PostGIS extensions
- Runs migrations
- Creates the public tenant with `localhost` domain
- Creates a superuser (if `CREATE_SUPERUSER=true` in `.env`)

## Quick Start (Local)

```bash
# 1. Clone and create virtual environment
git clone https://github.com/akouni/django-multi-tenant-starter.git
cd django-multi-tenant-starter
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install system libraries (Ubuntu/Debian)
sudo apt-get install gdal-bin libgdal-dev libgeos-dev libproj-dev

# 4. Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL and Redis connection details

# 5. Initialize the database
#    (PostgreSQL must have PostGIS extension available)
python manage.py migrate

# 6. Create a superuser
python manage.py createsuperuser

# 7. Run the development server
python manage.py runserver
```

## Creating a Tenant

Use the management command to create a new tenant:

```bash
# With Docker
docker-compose exec web python manage.py create_tenant \
    --name "Acme Corp" \
    --domain "acme.localhost" \
    --email admin@acme.com

# Locally
python manage.py create_tenant \
    --name "Acme Corp" \
    --domain "acme.localhost" \
    --email admin@acme.com
```

Options:
- `--name` — Organization name (required)
- `--domain` — Primary domain for the tenant (required)
- `--email` — Admin user email (required)
- `--password` — Admin password (optional, auto-generated if omitted)
- `--schema` — Custom schema name (optional, auto-generated from name)

Then access the tenant at `http://acme.localhost:8000`.

## Configuration

All settings are driven by environment variables. See `.env.example` for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | insecure default | Django secret key |
| `DEBUG` | `True` | Debug mode |
| `DOMAIN_NAME` | — | Production domain |
| `POSTGRES_DB` | `starter_db` | Database name |
| `POSTGRES_USER` | `starter_user` | Database user |
| `POSTGRES_PASSWORD` | `change_me` | Database password |
| `REDIS_HOST` | `redis` | Redis hostname |
| `USE_S3` | `False` | Enable S3 storage |
| `CREATE_SUPERUSER` | `false` | Auto-create superuser on startup |

## How Multi-Tenancy Works

1. **Public schema** (`public`) — holds the `Client` and `Domain` models, plus the public website
2. **Tenant schemas** (`tenant_*`) — each tenant gets a dedicated PostgreSQL schema with its own tables for users, geomap, etc.
3. **Routing** — django-tenants resolves the tenant from the request hostname via the `Domain` model
4. **URL separation** — public and tenant schemas use different URL configurations (`public_urls.py` vs `tenant_urls.py`)
5. **Admin separation** — two Jazzmin admin sites, one for each context

## Apps Overview

### Public Apps

| App | Description |
|-----|-------------|
| `customers` | Tenant lifecycle — Client model, Domain model, schema creation |
| `main` | Public website — home, about, contact pages |

### Tenant Apps

| App | Description |
|-----|-------------|
| `users` | CustomUser, Role (with hierarchy), UserProfile, Team, UserInvitation, SignupCode, UserActivity |
| `geomap` | Location (PostGIS PointField), LocationType, MapLayer — with DRF API and OpenLayers map |

## License

MIT
