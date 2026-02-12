from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import LocationType, Location, MapLayer


class LocationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationType
        fields = ["id", "name", "icon", "color", "is_active"]


class LocationSerializer(GeoFeatureModelSerializer):
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)
    location_type_name = serializers.CharField(
        source="location_type.name", read_only=True, default=""
    )

    class Meta:
        model = Location
        geo_field = "point"
        fields = [
            "id",
            "name",
            "description",
            "location_type",
            "location_type_name",
            "latitude",
            "longitude",
            "street",
            "street_number",
            "zip_code",
            "city",
            "canton",
            "is_active",
            "image",
            "website",
            "phone",
            "email",
            "created_at",
            "updated_at",
        ]


class MapLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapLayer
        fields = [
            "id",
            "name",
            "url_template",
            "attribution",
            "is_default",
            "is_active",
            "max_zoom",
            "opacity",
            "sort_order",
        ]
