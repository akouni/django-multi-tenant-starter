from django.contrib.gis import admin as gis_admin
from django.contrib import admin

from core.admin_utils import register_tenant_only
from .models import LocationType, Location, MapLayer


@register_tenant_only(LocationType)
class LocationTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "color", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@register_tenant_only(Location)
class LocationAdmin(gis_admin.GISModelAdmin):
    list_display = (
        "name",
        "location_type",
        "city",
        "canton",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "location_type", "canton")
    search_fields = ("name", "description", "city", "street")
    raw_id_fields = ("location_type",)


@register_tenant_only(MapLayer)
class MapLayerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_default",
        "is_active",
        "max_zoom",
        "opacity",
        "sort_order",
    )
    list_filter = ("is_active", "is_default")
    search_fields = ("name",)
    list_editable = ("sort_order", "is_active", "is_default")
