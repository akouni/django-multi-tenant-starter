# core/storage.py - Tenant-aware S3 storage backend
import logging
import json
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django_tenants.utils import get_public_schema_name
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def get_current_tenant_schema():
    """Get the current tenant's schema name."""
    try:
        from django.db import connection
        if hasattr(connection, 'tenant') and connection.tenant:
            return connection.tenant.schema_name
    except Exception:
        pass
    return get_public_schema_name()


def get_s3_client():
    """Create and return a boto3 S3 client."""
    return boto3.client(
        's3',
        endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL', None),
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1'),
    )


def create_tenant_bucket(schema_name, set_policy=True):
    """Create a S3 bucket for a tenant."""
    if not getattr(settings, 'USE_S3', False):
        return True

    bucket_name = schema_name

    try:
        s3_client = get_s3_client()

        bucket_exists = False
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            logger.info(f"Bucket '{bucket_name}' already exists")
            bucket_exists = True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code != '404':
                logger.error(f"Error checking bucket '{bucket_name}': {e}")
                return False

        if not bucket_exists:
            logger.info(f"Creating bucket '{bucket_name}'...")
            endpoint_url = getattr(settings, 'AWS_S3_ENDPOINT_URL', None)
            region = getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')

            if endpoint_url:
                s3_client.create_bucket(Bucket=bucket_name)
            elif region != 'us-east-1':
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            else:
                s3_client.create_bucket(Bucket=bucket_name)

            logger.info(f"Bucket '{bucket_name}' created successfully")

        if set_policy:
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadMedia",
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                    }
                ]
            }
            try:
                s3_client.put_bucket_policy(
                    Bucket=bucket_name,
                    Policy=json.dumps(bucket_policy)
                )
            except ClientError as e:
                logger.warning(f"Could not set bucket policy for '{bucket_name}': {e}")

        return True

    except Exception as e:
        logger.error(f"Error creating bucket '{bucket_name}': {e}")
        return False


class TenantS3Storage(S3Boto3Storage):
    """S3 storage with dedicated bucket per tenant."""

    def __init__(self, *args, **kwargs):
        kwargs.pop('bucket_name', None)
        super().__init__(*args, **kwargs)

    @property
    def bucket_name(self):
        return get_current_tenant_schema()

    @bucket_name.setter
    def bucket_name(self, value):
        pass


class TenantMediaStorage(TenantS3Storage):
    """Storage for media files with tenant isolation."""
    location = 'media'
    file_overwrite = False


class TenantPrivateStorage(TenantS3Storage):
    """Storage for private files with signed URLs."""
    location = 'private'
    default_acl = 'private'
    file_overwrite = False
    querystring_auth = True
    querystring_expire = 3600
