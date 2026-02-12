from django.views.generic import TemplateView, DetailView
from rest_framework import viewsets
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from .models import LocationType, Location, MapLayer
from .serializers import LocationTypeSerializer, LocationSerializer, MapLayerSerializer


# ==========================================
# TEMPLATE VIEWS
# ==========================================


class MapView(TemplateView):
    """Main map page displaying all active locations."""

    template_name = "tenants/geomap/map.html"


class LocationDetailView(DetailView):
    """Detail page for a single location."""

    model = Location
    template_name = "tenants/geomap/location_detail.html"
    context_object_name = "location"

    def get_queryset(self):
        return Location.objects.filter(is_active=True).select_related("location_type")


# ==========================================
# API VIEWSETS
# ==========================================


class LocationViewSet(viewsets.ModelViewSet):
    """
    CRUD API for locations.
    Supports filtering by location_type.
    """

    queryset = Location.objects.filter(is_active=True).select_related("location_type")
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["location_type", "canton", "is_active"]


class LocationTypeViewSet(ReadOnlyModelViewSet):
    """Read-only API for location types."""

    queryset = LocationType.objects.filter(is_active=True)
    serializer_class = LocationTypeSerializer


class MapLayerViewSet(ReadOnlyModelViewSet):
    """Read-only API for map layers."""

    queryset = MapLayer.objects.filter(is_active=True)
    serializer_class = MapLayerSerializer
