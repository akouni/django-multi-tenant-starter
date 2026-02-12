"""
Management command to populate the project with realistic demo data.

Creates tenants, domains, admin/staff/regular users, roles, locations,
location types, map layers, teams, and user profiles.

Usage:
    python manage.py create_demo_data
    python manage.py create_demo_data --flush   # Reset and recreate
"""

import logging
from django.core.management.base import BaseCommand
from django.db import connection

logger = logging.getLogger(__name__)

# ============================================================
# DEMO DATA CONSTANTS
# ============================================================

DEMO_PASSWORD = "demo1234!"

TENANTS = [
    {
        "name": "Acme Corporation",
        "schema": "tenant_acme",
        "domain": "acme.localhost",
        "contact_name": "Alice Martin",
        "contact_email": "alice@acme.localhost",
        "contact_phone": "+41 21 345 67 89",
        "street": "Rue du Marche 12",
        "city": "Lausanne",
        "zip_code": "1003",
        "canton": "VD",
        "primary_color": "#2563eb",
        "default_language": "fr",
        "active_languages": ["en", "fr"],
    },
    {
        "name": "Helvetia Tech",
        "schema": "tenant_helvetia",
        "domain": "helvetia.localhost",
        "contact_name": "Bruno Keller",
        "contact_email": "bruno@helvetia.localhost",
        "contact_phone": "+41 44 567 89 01",
        "street": "Bahnhofstrasse 42",
        "city": "Zurich",
        "zip_code": "8001",
        "canton": "ZH",
        "primary_color": "#dc2626",
        "default_language": "en",
        "active_languages": ["en", "fr"],
    },
    {
        "name": "Geneva Digital",
        "schema": "tenant_geneva",
        "domain": "geneva.localhost",
        "contact_name": "Claire Dubois",
        "contact_email": "claire@geneva.localhost",
        "contact_phone": "+41 22 789 01 23",
        "street": "Quai du Mont-Blanc 5",
        "city": "Geneva",
        "zip_code": "1201",
        "canton": "GE",
        "primary_color": "#059669",
        "default_language": "fr",
        "active_languages": ["en", "fr"],
    },
]

TENANT_USERS = {
    "tenant_acme": [
        {"username": "alice", "email": "alice@acme.localhost", "first_name": "Alice", "last_name": "Martin", "is_superuser": True, "is_staff": True, "role": "admin"},
        {"username": "marc", "email": "marc@acme.localhost", "first_name": "Marc", "last_name": "Dupont", "is_superuser": False, "is_staff": True, "role": "manager"},
        {"username": "julie", "email": "julie@acme.localhost", "first_name": "Julie", "last_name": "Bernard", "is_superuser": False, "is_staff": False, "role": "editor"},
        {"username": "thomas", "email": "thomas@acme.localhost", "first_name": "Thomas", "last_name": "Favre", "is_superuser": False, "is_staff": False, "role": "viewer"},
        {"username": "sophie", "email": "sophie@acme.localhost", "first_name": "Sophie", "last_name": "Roux", "is_superuser": False, "is_staff": False, "role": "member"},
    ],
    "tenant_helvetia": [
        {"username": "bruno", "email": "bruno@helvetia.localhost", "first_name": "Bruno", "last_name": "Keller", "is_superuser": True, "is_staff": True, "role": "admin"},
        {"username": "sarah", "email": "sarah@helvetia.localhost", "first_name": "Sarah", "last_name": "Meier", "is_superuser": False, "is_staff": True, "role": "manager"},
        {"username": "david", "email": "david@helvetia.localhost", "first_name": "David", "last_name": "Schmid", "is_superuser": False, "is_staff": False, "role": "editor"},
    ],
    "tenant_geneva": [
        {"username": "claire", "email": "claire@geneva.localhost", "first_name": "Claire", "last_name": "Dubois", "is_superuser": True, "is_staff": True, "role": "admin"},
        {"username": "luca", "email": "luca@geneva.localhost", "first_name": "Luca", "last_name": "Rossi", "is_superuser": False, "is_staff": True, "role": "manager"},
        {"username": "emma", "email": "emma@geneva.localhost", "first_name": "Emma", "last_name": "Bonnet", "is_superuser": False, "is_staff": False, "role": "editor"},
        {"username": "noah", "email": "noah@geneva.localhost", "first_name": "Noah", "last_name": "Moreau", "is_superuser": False, "is_staff": False, "role": "member"},
    ],
}

LOCATION_TYPES = [
    {"name": "Office", "icon": "bi-building", "color": "#2563eb"},
    {"name": "Warehouse", "icon": "bi-box-seam", "color": "#d97706"},
    {"name": "Client Site", "icon": "bi-person-workspace", "color": "#059669"},
    {"name": "Event Venue", "icon": "bi-calendar-event", "color": "#dc2626"},
    {"name": "Partner", "icon": "bi-handshake", "color": "#7c3aed"},
]

LOCATIONS = {
    "tenant_acme": [
        {"name": "Acme HQ", "description": "Main headquarters in Lausanne", "type": "Office", "lat": 46.5197, "lon": 6.6323, "street": "Rue du Marche 12", "city": "Lausanne", "zip_code": "1003", "canton": "VD", "phone": "+41 21 345 67 89", "email": "hq@acme.localhost", "website": "https://acme.localhost"},
        {"name": "Acme Warehouse Yverdon", "description": "Main storage facility", "type": "Warehouse", "lat": 46.7785, "lon": 6.6410, "street": "Zone Industrielle 8", "city": "Yverdon-les-Bains", "zip_code": "1400", "canton": "VD", "phone": "+41 24 456 78 90"},
        {"name": "Client - Nestle", "description": "Nestle partnership site", "type": "Client Site", "lat": 46.4614, "lon": 6.8418, "street": "Avenue Nestle 55", "city": "Vevey", "zip_code": "1800", "canton": "VD"},
        {"name": "SwissTech Convention Center", "description": "Annual tech conference venue", "type": "Event Venue", "lat": 46.5232, "lon": 6.5654, "street": "Route Louis-Favre 2", "city": "Ecublens", "zip_code": "1024", "canton": "VD"},
        {"name": "Partner - EPFL Innovation Park", "description": "Research collaboration partner", "type": "Partner", "lat": 46.5185, "lon": 6.5636, "street": "EPFL Innovation Park", "city": "Ecublens", "zip_code": "1024", "canton": "VD", "website": "https://epfl-innovationpark.ch"},
    ],
    "tenant_helvetia": [
        {"name": "Helvetia Tech HQ", "description": "Main office in Zurich", "type": "Office", "lat": 47.3769, "lon": 8.5417, "street": "Bahnhofstrasse 42", "city": "Zurich", "zip_code": "8001", "canton": "ZH", "phone": "+41 44 567 89 01", "email": "info@helvetia.localhost"},
        {"name": "Helvetia Lab Basel", "description": "R&D laboratory", "type": "Office", "lat": 47.5596, "lon": 7.5886, "street": "Steinenvorstadt 19", "city": "Basel", "zip_code": "4051", "canton": "BS"},
        {"name": "Client - Roche", "description": "Pharmaceutical client site", "type": "Client Site", "lat": 47.5629, "lon": 7.6034, "street": "Grenzacherstrasse 124", "city": "Basel", "zip_code": "4058", "canton": "BS"},
        {"name": "ETH Zurich Partnership", "description": "Academic research partner", "type": "Partner", "lat": 47.3763, "lon": 8.5482, "street": "Ramistrasse 101", "city": "Zurich", "zip_code": "8092", "canton": "ZH", "website": "https://ethz.ch"},
    ],
    "tenant_geneva": [
        {"name": "Geneva Digital Office", "description": "Main office at lakefront", "type": "Office", "lat": 46.2044, "lon": 6.1432, "street": "Quai du Mont-Blanc 5", "city": "Geneva", "zip_code": "1201", "canton": "GE", "phone": "+41 22 789 01 23", "email": "hello@geneva.localhost"},
        {"name": "CERN Meeting Point", "description": "Physics research collaboration", "type": "Partner", "lat": 46.2330, "lon": 6.0557, "street": "Esplanade des Particules 1", "city": "Meyrin", "zip_code": "1217", "canton": "GE", "website": "https://home.cern"},
        {"name": "Palexpo Conference Hall", "description": "Exhibition and conference center", "type": "Event Venue", "lat": 46.2339, "lon": 6.1114, "street": "Route Francois-Peyrot 30", "city": "Le Grand-Saconnex", "zip_code": "1218", "canton": "GE"},
        {"name": "Warehouse Nyon", "description": "Regional logistics hub", "type": "Warehouse", "lat": 46.3833, "lon": 6.2348, "street": "Route de Saint-Cergue 295", "city": "Nyon", "zip_code": "1260", "canton": "VD"},
        {"name": "Client - UN Geneva", "description": "United Nations office", "type": "Client Site", "lat": 46.2265, "lon": 6.1400, "street": "Palais des Nations", "city": "Geneva", "zip_code": "1211", "canton": "GE"},
        {"name": "Client - WHO", "description": "World Health Organization", "type": "Client Site", "lat": 46.2332, "lon": 6.1335, "street": "Avenue Appia 20", "city": "Geneva", "zip_code": "1211", "canton": "GE"},
    ],
}

MAP_LAYERS = [
    {"name": "OpenStreetMap", "url_template": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", "attribution": "&copy; OpenStreetMap contributors", "is_default": True, "max_zoom": 19, "opacity": 1.0, "sort_order": 0},
    {"name": "Satellite (Esri)", "url_template": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", "attribution": "&copy; Esri", "is_default": False, "max_zoom": 18, "opacity": 1.0, "sort_order": 1},
    {"name": "Topographic", "url_template": "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", "attribution": "&copy; OpenTopoMap", "is_default": False, "max_zoom": 17, "opacity": 1.0, "sort_order": 2},
]

TEAMS = {
    "tenant_acme": [
        {"name": "Engineering", "slug": "engineering", "description": "Software development team", "leader": "marc", "members": ["marc", "julie", "thomas"]},
        {"name": "Operations", "slug": "operations", "description": "Logistics and operations", "leader": "alice", "members": ["alice", "sophie"]},
    ],
    "tenant_helvetia": [
        {"name": "Research", "slug": "research", "description": "R&D and innovation", "leader": "sarah", "members": ["sarah", "david"]},
    ],
    "tenant_geneva": [
        {"name": "Consulting", "slug": "consulting", "description": "Client consulting team", "leader": "luca", "members": ["luca", "emma", "noah"]},
        {"name": "Management", "slug": "management", "description": "Executive team", "leader": "claire", "members": ["claire", "luca"]},
    ],
}


class Command(BaseCommand):
    help = "Create demo tenants, users, locations, and teams with realistic Swiss data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing demo tenants before recreating.",
        )

    def handle(self, *args, **options):
        from public_apps.customers.models import Client, Domain

        if options["flush"]:
            self._flush_demo_tenants()

        # 1. Create public superuser
        self._create_public_superuser()

        # 2. Create each tenant
        for tenant_data in TENANTS:
            schema = tenant_data["schema"]
            domain = tenant_data["domain"]

            if Client.objects.filter(schema_name=schema).exists():
                self.stdout.write(f"  Tenant '{schema}' already exists, skipping.")
                continue

            self.stdout.write(self.style.MIGRATE_HEADING(
                f"\n{'='*60}\n Creating tenant: {tenant_data['name']}\n{'='*60}"
            ))

            client = Client(
                name=tenant_data["name"],
                schema_name=schema,
                type="client",
                contact_name=tenant_data["contact_name"],
                contact_email=tenant_data["contact_email"],
                contact_phone=tenant_data.get("contact_phone", ""),
                street=tenant_data.get("street", ""),
                city=tenant_data.get("city", ""),
                zip_code=tenant_data.get("zip_code", ""),
                canton=tenant_data.get("canton", ""),
                primary_color=tenant_data.get("primary_color", "#337e16"),
                default_language=tenant_data.get("default_language", "en"),
                active_languages=tenant_data.get("active_languages", ["en", "fr"]),
                is_active=True,
            )
            client.save()

            # Create schema + run migrations
            try:
                client.create_schema_manually()
                self.stdout.write(self.style.SUCCESS(f"  Schema '{schema}' created."))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"  Failed to create schema: {e}"))
                client.delete()
                continue

            # Create domain
            Domain.objects.get_or_create(
                domain=domain,
                defaults={"tenant": client, "is_primary": True},
            )
            self.stdout.write(self.style.SUCCESS(f"  Domain '{domain}' assigned."))

            # Switch to tenant schema and populate
            connection.set_schema(schema)
            try:
                self._create_roles()
                self._create_users(schema)
                self._create_location_types()
                self._create_locations(schema)
                self._create_map_layers()
                self._create_teams(schema)
            finally:
                connection.set_schema_to_public()

        # Summary
        self._print_summary()

    def _flush_demo_tenants(self):
        from public_apps.customers.models import Client

        demo_schemas = [t["schema"] for t in TENANTS]
        for client in Client.objects.filter(schema_name__in=demo_schemas):
            self.stdout.write(f"  Deleting tenant '{client.schema_name}'...")
            try:
                client.delete(force_drop=True)
            except Exception:
                client.delete()
        self.stdout.write(self.style.WARNING("  Demo tenants flushed."))

    def _create_public_superuser(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@localhost",
                password=DEMO_PASSWORD,
                first_name="Admin",
                last_name="User",
            )
            self.stdout.write(self.style.SUCCESS(
                "  Public superuser 'admin' created."
            ))
        else:
            self.stdout.write("  Public superuser 'admin' already exists.")

    def _create_roles(self):
        from tenant_apps.users.models import Role
        created = Role.create_default_roles()
        if created:
            self.stdout.write(self.style.SUCCESS(
                f"  Roles created: {', '.join(r.slug for r in created)}"
            ))
        else:
            self.stdout.write("  Roles already exist.")

    def _create_users(self, schema):
        from tenant_apps.users.models import CustomUser, Role, UserProfile

        users_data = TENANT_USERS.get(schema, [])
        role_cache = {r.slug: r for r in Role.objects.all()}

        for u in users_data:
            user, created = CustomUser.objects.get_or_create(
                username=u["username"],
                defaults={
                    "email": u["email"],
                    "first_name": u["first_name"],
                    "last_name": u["last_name"],
                    "is_staff": u["is_staff"],
                    "is_superuser": u["is_superuser"],
                },
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            role_slug = u.get("role")
            if role_slug and role_slug in role_cache:
                profile.role = role_cache[role_slug]
                profile.save()

            status = "created" if created else "exists"
            role_label = u.get("role", "-")
            self.stdout.write(f"  User '{u['username']}' ({role_label}) [{status}]")

    def _create_location_types(self):
        from tenant_apps.geomap.models import LocationType

        for lt in LOCATION_TYPES:
            LocationType.objects.get_or_create(
                name=lt["name"],
                defaults={
                    "icon": lt["icon"],
                    "color": lt["color"],
                    "is_active": True,
                },
            )
        self.stdout.write(self.style.SUCCESS(
            f"  {len(LOCATION_TYPES)} location types ready."
        ))

    def _create_locations(self, schema):
        from django.contrib.gis.geos import Point
        from tenant_apps.geomap.models import Location, LocationType

        type_cache = {lt.name: lt for lt in LocationType.objects.all()}
        locations_data = LOCATIONS.get(schema, [])

        for loc in locations_data:
            lt = type_cache.get(loc.get("type"))
            Location.objects.get_or_create(
                name=loc["name"],
                defaults={
                    "description": loc.get("description", ""),
                    "location_type": lt,
                    "point": Point(loc["lon"], loc["lat"], srid=4326),
                    "street": loc.get("street", ""),
                    "city": loc.get("city", ""),
                    "zip_code": loc.get("zip_code", ""),
                    "canton": loc.get("canton", ""),
                    "phone": loc.get("phone", ""),
                    "email": loc.get("email", ""),
                    "website": loc.get("website", ""),
                    "is_active": True,
                },
            )
        self.stdout.write(self.style.SUCCESS(
            f"  {len(locations_data)} locations created."
        ))

    def _create_map_layers(self):
        from tenant_apps.geomap.models import MapLayer

        for ml in MAP_LAYERS:
            MapLayer.objects.get_or_create(
                name=ml["name"],
                defaults={
                    "url_template": ml["url_template"],
                    "attribution": ml["attribution"],
                    "is_default": ml["is_default"],
                    "max_zoom": ml["max_zoom"],
                    "opacity": ml["opacity"],
                    "sort_order": ml["sort_order"],
                    "is_active": True,
                },
            )
        self.stdout.write(self.style.SUCCESS(
            f"  {len(MAP_LAYERS)} map layers ready."
        ))

    def _create_teams(self, schema):
        from tenant_apps.users.models import CustomUser, Team

        teams_data = TEAMS.get(schema, [])
        user_cache = {u.username: u for u in CustomUser.objects.all()}

        for t in teams_data:
            leader = user_cache.get(t.get("leader"))
            team, created = Team.objects.get_or_create(
                slug=t["slug"],
                defaults={
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "leader": leader,
                    "is_active": True,
                },
            )
            if created:
                members = [user_cache[m] for m in t.get("members", []) if m in user_cache]
                team.members.set(members)

        self.stdout.write(self.style.SUCCESS(
            f"  {len(teams_data)} teams created."
        ))

    def _print_summary(self):
        self.stdout.write(self.style.SUCCESS(f"""
{'='*60}
  DEMO DATA CREATED SUCCESSFULLY
{'='*60}

  All passwords: {DEMO_PASSWORD}

  PUBLIC ADMIN
    URL:      http://localhost:8000/en/admin/
    Username: admin
    Password: {DEMO_PASSWORD}

  TENANT: Acme Corporation
    URL:      http://acme.localhost:8000/
    Admin:    http://acme.localhost:8000/en/admin/
    Users:    alice (admin), marc (manager), julie (editor),
              thomas (viewer), sophie (member)
    Locations: 5 | Teams: 2

  TENANT: Helvetia Tech
    URL:      http://helvetia.localhost:8000/
    Admin:    http://helvetia.localhost:8000/en/admin/
    Users:    bruno (admin), sarah (manager), david (editor)
    Locations: 4 | Teams: 1

  TENANT: Geneva Digital
    URL:      http://geneva.localhost:8000/
    Admin:    http://geneva.localhost:8000/en/admin/
    Users:    claire (admin), luca (manager), emma (editor),
              noah (member)
    Locations: 6 | Teams: 2
{'='*60}
"""))
