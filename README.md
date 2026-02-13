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
- **Demo data included** — 3 tenants, 12 users, 15 locations across Switzerland

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
│   │       ├── create_tenant.py
│   │       └── create_demo_data.py
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

# 4. Load demo data (in another terminal)
docker-compose exec web python manage.py create_demo_data

# 5. Open in your browser (see Demo Access below)
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

# 5. Generate and apply migrations
python manage.py makemigrations customers main users geomap
python manage.py migrate

# 6. Load demo data (creates superuser + 3 tenants + users + locations)
python manage.py create_demo_data

# 7. Run the development server
python manage.py runserver
```

## Demo Access

> **All demo accounts use the same password: `demo1234!`**

### Public Site

| URL | Credentials |
|-----|-------------|
| http://localhost:8000 | Public landing page (no login required) |
| http://localhost:8000/en/admin/ | Username: `admin` / Password: `demo1234!` |

### Tenant: Acme Corporation

| URL | Description |
|-----|-------------|
| http://acme.localhost:8000 | Tenant home (redirects to dashboard) |
| http://acme.localhost:8000/en/admin/ | Tenant admin panel |
| http://acme.localhost:8000/en/geomap/map/ | Interactive map (5 locations) |
| http://acme.localhost:8000/en/users/ | User management |

| Username | Role | Staff |
|----------|------|-------|
| `alice` | Admin | Yes (superuser) |
| `marc` | Manager | Yes |
| `julie` | Editor | No |
| `thomas` | Viewer | No |
| `sophie` | Member | No |

### Tenant: Helvetia Tech

| URL | Description |
|-----|-------------|
| http://helvetia.localhost:8000 | Tenant home |
| http://helvetia.localhost:8000/en/admin/ | Tenant admin panel |
| http://helvetia.localhost:8000/en/geomap/map/ | Interactive map (4 locations) |

| Username | Role | Staff |
|----------|------|-------|
| `bruno` | Admin | Yes (superuser) |
| `sarah` | Manager | Yes |
| `david` | Editor | No |

### Tenant: Geneva Digital

| URL | Description |
|-----|-------------|
| http://geneva.localhost:8000 | Tenant home |
| http://geneva.localhost:8000/en/admin/ | Tenant admin panel |
| http://geneva.localhost:8000/en/geomap/map/ | Interactive map (6 locations) |

| Username | Role | Staff |
|----------|------|-------|
| `claire` | Admin | Yes (superuser) |
| `luca` | Manager | Yes |
| `emma` | Editor | No |
| `noah` | Member | No |

### Demo Data Summary

| | Acme Corporation | Helvetia Tech | Geneva Digital |
|---|---|---|---|
| Schema | `tenant_acme` | `tenant_helvetia` | `tenant_geneva` |
| Domain | `acme.localhost` | `helvetia.localhost` | `geneva.localhost` |
| City | Lausanne (VD) | Zurich (ZH) | Geneva (GE) |
| Users | 5 | 3 | 4 |
| Locations | 5 | 4 | 6 |
| Teams | 2 | 1 | 2 |
| Language | French | English | French |

### GeoMap Locations

All demo locations are real Swiss addresses with accurate GPS coordinates:

- **Acme**: Lausanne HQ, Yverdon warehouse, Nestle (Vevey), SwissTech Convention Center, EPFL Innovation Park
- **Helvetia**: Zurich HQ, Basel R&D lab, Roche (Basel), ETH Zurich
- **Geneva**: Geneva lakefront office, CERN, Palexpo, Nyon warehouse, UN Geneva, WHO

## Creating a Tenant

Use the management command to create a new tenant manually:

```bash
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

## Management Commands

| Command | Description |
|---------|-------------|
| `create_demo_data` | Create 3 demo tenants with users, locations, teams |
| `create_demo_data --flush` | Delete demo tenants and recreate from scratch |
| `create_tenant` | Create a single tenant with admin user |

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

```
Request: http://acme.localhost:8000/en/admin/
  → django-tenants looks up Domain where domain = "acme.localhost"
  → Finds Client with schema_name = "tenant_acme"
  → Sets PostgreSQL search_path to "tenant_acme"
  → Uses tenant_urls.py → tenant_admin_site
  → All queries now run against the tenant_acme schema
```

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

## Hosting & Deployment

### Production Hosting

For production deployments, we recommend [Hostinger](https://hostinger.fr?REFERRALCODE=PL3PAULAKLFD) — affordable VPS plans with full root access, Docker support, and excellent performance for Django + PostgreSQL stacks.


## License

MIT
