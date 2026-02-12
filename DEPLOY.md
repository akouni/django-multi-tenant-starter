# Free Deployment Guide

Deploy this project for **$0** using Render + Neon + Cloudflare.

| Service | Role | Cost |
|---------|------|------|
| [Render](https://render.com) | Hosts the Django app | Free |
| [Neon](https://neon.tech) | PostgreSQL + PostGIS database | Free |
| [Cloudflare](https://cloudflare.com) | DNS + SSL + wildcard subdomains | Free |
| [FreeDNS](https://freedns.afraid.org) | Free domain name | Free |

**Total: $0/month**

> Note: Render free tier sleeps after 15 minutes of inactivity (30s cold start on wake). Perfect for demos.

---

## Step 1: Get a Free Domain (FreeDNS)

1. Go to [https://freedns.afraid.org](https://freedns.afraid.org)
2. Create an account
3. Go to **Subdomains** → **Add**
4. Choose a domain from the public list (e.g., `mooo.com`, `chickenkiller.com`, `us.to`)
5. Pick a subdomain name, e.g., `myapp.mooo.com`
6. Set **Type** to `A` and **Destination** to `1.2.3.4` (temporary, we'll change it)
7. Save — you now have a free domain like `myapp.mooo.com`

> **Alternative**: Buy a `.xyz` domain for ~$1/year on Namecheap or Porkbun for a cleaner URL.

---

## Step 2: Set Up Cloudflare

1. Go to [https://cloudflare.com](https://cloudflare.com) and create a free account
2. Click **Add a site** → enter your domain (e.g., `myapp.mooo.com`)
3. Select the **Free** plan
4. Cloudflare will give you **two nameservers** (e.g., `ada.ns.cloudflare.com`)
5. Go back to FreeDNS and update your domain's nameservers to Cloudflare's
6. Wait for propagation (usually 5-30 minutes)

### Configure DNS Records in Cloudflare

Once Cloudflare is active, go to **DNS** → **Records** and add:

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| `CNAME` | `@` | `your-app.onrender.com` | Proxied (orange cloud) |
| `CNAME` | `*` | `your-app.onrender.com` | Proxied (orange cloud) |

The `*` wildcard record is what makes `acme.myapp.mooo.com` and `helvetia.myapp.mooo.com` all point to your Render app.

### SSL Settings

1. Go to **SSL/TLS** → set mode to **Full**
2. Go to **SSL/TLS** → **Edge Certificates** → enable **Always Use HTTPS**

---

## Step 3: Create Neon Database

1. Go to [https://neon.tech](https://neon.tech) and create a free account
2. Create a new project (choose **AWS eu-central-1** for Swiss proximity)
3. Copy the **connection string** — it looks like:
   ```
   postgresql://neondb_owner:xxxx@ep-xxx-yyy.eu-central-1.aws.neon.tech/neondb?sslmode=require
   ```
4. **Enable PostGIS**: Go to **SQL Editor** in the Neon dashboard and run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   CREATE EXTENSION IF NOT EXISTS postgis_topology;
   CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
   ```

---

## Step 4: Deploy on Render

### Option A: One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/akouni/django-multi-tenant-starter)

### Option B: Manual Setup

1. Go to [https://render.com](https://render.com) and create a free account
2. Click **New** → **Web Service**
3. Connect your GitHub repo: `akouni/django-multi-tenant-starter`
4. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `django-multi-tenant-starter` |
| **Region** | Frankfurt (EU) |
| **Branch** | `main` |
| **Runtime** | Python |
| **Build Command** | `./render_build.sh` |
| **Start Command** | `gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| **Plan** | Free |

5. Add **Environment Variables**:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.13.0` |
| `DEBUG` | `False` |
| `SECRET_KEY` | *(click Generate)* |
| `DATABASE_URL` | *(paste your Neon connection string)* |
| `DOMAIN_NAME` | `myapp.mooo.com` *(your FreeDNS domain)* |
| `DJANGO_SETTINGS_MODULE` | `core.settings` |

6. Click **Create Web Service** — Render will build and deploy automatically.

7. Note your Render URL (e.g., `django-multi-tenant-starter-xxxx.onrender.com`)

---

## Step 5: Connect Custom Domain on Render

1. In your Render dashboard, go to your web service → **Settings** → **Custom Domains**
2. Add your domain: `myapp.mooo.com`
3. Add a wildcard domain: `*.myapp.mooo.com`
4. Render will show verification records — since you're using Cloudflare proxy, just make sure your CNAME records from Step 2 are in place.

---

## Step 6: Add Domain to Public Tenant

Open the Render **Shell** tab (or use the Render CLI), and run:

```bash
python manage.py shell -c "
from public_apps.customers.models import Client, Domain

tenant = Client.objects.get(schema_name='public')

# Add your custom domain
Domain.objects.get_or_create(domain='myapp.mooo.com', defaults={'tenant': tenant, 'is_primary': True})

# Add wildcard awareness (django-tenants matches exact domains)
# Tenant subdomains are added by create_demo_data
print('Domain added.')
"
```

---

## Step 7: Load Demo Data

In the Render **Shell** tab:

```bash
python manage.py create_demo_data
```

This creates 3 demo tenants. Their domains need to match your setup.
By default, the command creates domains like `acme.localhost`.

To use your real domain, update the domains after running the command:

```bash
python manage.py shell -c "
from public_apps.customers.models import Domain

# Update demo tenant domains to your real domain
updates = {
    'acme.localhost': 'acme.myapp.mooo.com',
    'helvetia.localhost': 'helvetia.myapp.mooo.com',
    'geneva.localhost': 'geneva.myapp.mooo.com',
}
for old, new in updates.items():
    Domain.objects.filter(domain=old).update(domain=new)
    print(f'{old} → {new}')
"
```

---

## Step 8: Test It

| URL | What you see |
|-----|-------------|
| `https://myapp.mooo.com` | Public landing page |
| `https://myapp.mooo.com/en/admin/` | Public admin (`admin` / `demo1234!`) |
| `https://acme.myapp.mooo.com` | Acme tenant dashboard |
| `https://acme.myapp.mooo.com/en/admin/` | Acme admin (`alice` / `demo1234!`) |
| `https://helvetia.myapp.mooo.com` | Helvetia tenant |
| `https://geneva.myapp.mooo.com` | Geneva tenant |
| `https://acme.myapp.mooo.com/en/geomap/map/` | Interactive Swiss map |

All protected by Cloudflare SSL.

---

## Troubleshooting

### "DisallowedHost" error
Add the domain to `ALLOWED_HOSTS` via the `DOMAIN_NAME` env var. The `.domain` pattern allows all subdomains automatically.

### "No tenant for hostname" error
The requested hostname doesn't have a `Domain` entry in the database. Add it via admin or shell:
```bash
python manage.py shell -c "
from public_apps.customers.models import Client, Domain
tenant = Client.objects.get(schema_name='tenant_acme')
Domain.objects.get_or_create(domain='acme.yourdomain.com', defaults={'tenant': tenant, 'is_primary': True})
"
```

### Database connection error
Verify your `DATABASE_URL` in Render env vars. Make sure PostGIS extensions are enabled in Neon.

### Static files not loading
Run `python manage.py collectstatic --noinput` in the Render shell. Whitenoise serves static files in production.
