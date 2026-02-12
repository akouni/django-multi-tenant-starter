# public_apps/customers/management/commands/create_tenant.py
"""
Management command to create a new tenant with domain and admin user.

Usage:
    python manage.py create_tenant --name "Acme" --domain "acme.localhost" --email admin@acme.com
    python manage.py create_tenant --name "Acme" --domain "acme.localhost" --email admin@acme.com --password secret123
    python manage.py create_tenant --name "Acme" --domain "acme.localhost" --email admin@acme.com --schema tenant_acme
"""

import secrets
from django.core.management.base import BaseCommand, CommandError
from public_apps.customers.models import Client, Domain, generate_schema_name


class Command(BaseCommand):
    help = "Create a new tenant with a domain and an admin superuser."

    def add_arguments(self, parser):
        parser.add_argument(
            "--name",
            type=str,
            required=True,
            help="Name of the tenant organization.",
        )
        parser.add_argument(
            "--domain",
            type=str,
            required=True,
            help="Primary domain for the tenant (e.g. acme.localhost).",
        )
        parser.add_argument(
            "--email",
            type=str,
            required=True,
            help="Email address for the tenant admin user.",
        )
        parser.add_argument(
            "--password",
            type=str,
            default=None,
            help="Password for the admin user. If omitted, a random password is generated.",
        )
        parser.add_argument(
            "--schema",
            type=str,
            default=None,
            help="Schema name for the tenant. If omitted, auto-generated from the name.",
        )

    def handle(self, *args, **options):
        name = options["name"]
        domain_name = options["domain"]
        email = options["email"]
        password = options["password"]
        schema_name = options["schema"]

        if not password:
            password = secrets.token_urlsafe(16)
            password_generated = True
        else:
            password_generated = False

        if not schema_name:
            schema_name = generate_schema_name(name)

        # Check for existing schema name
        if Client.objects.filter(schema_name=schema_name).exists():
            raise CommandError(
                f"A tenant with schema name '{schema_name}' already exists."
            )

        # Check for existing domain
        if Domain.objects.filter(domain=domain_name).exists():
            raise CommandError(
                f"A domain '{domain_name}' is already in use."
            )

        self.stdout.write(f"Creating tenant '{name}' (schema: {schema_name})...")

        # Create the Client
        client = Client(
            name=name,
            schema_name=schema_name,
            type=Client.TenantType.CLIENT,
            contact_email=email,
        )
        client.save()

        # Create the schema and run migrations
        try:
            client.create_schema_manually()
        except Exception as e:
            # Clean up if schema creation fails
            client.delete()
            raise CommandError(f"Failed to create schema: {e}")

        self.stdout.write(self.style.SUCCESS(f"Schema '{schema_name}' created."))

        # Create the Domain
        Domain.objects.create(
            domain=domain_name,
            tenant=client,
            is_primary=True,
        )
        self.stdout.write(self.style.SUCCESS(f"Domain '{domain_name}' assigned."))

        # Create the admin user inside the tenant schema
        try:
            user, used_password = client.create_tenant_admin(email, password)
        except Exception as e:
            raise CommandError(f"Tenant created but admin user creation failed: {e}")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(self.style.SUCCESS("Tenant created successfully!"))
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(f"  Name:     {name}")
        self.stdout.write(f"  Schema:   {schema_name}")
        self.stdout.write(f"  Domain:   {domain_name}")
        self.stdout.write(f"  Admin:    {user.username} ({email})")
        if password_generated:
            self.stdout.write(f"  Password: {used_password}")
            self.stdout.write(
                self.style.WARNING(
                    "  (auto-generated -- save this password now!)"
                )
            )
        else:
            self.stdout.write("  Password: (as provided)")
        self.stdout.write("")
