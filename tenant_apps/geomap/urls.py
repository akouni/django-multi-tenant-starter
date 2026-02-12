from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    MapView,
    LocationDetailView,
    LocationViewSet,
    LocationTypeViewSet,
    MapLayerViewSet,
)

app_name = "geomap"

router = DefaultRouter()
router.register(r"locations", LocationViewSet, basename="location")
router.register(r"location-types", LocationTypeViewSet, basename="locationtype")
router.register(r"map-layers", MapLayerViewSet, basename="maplayer")

urlpatterns = [
    path("api/", include(router.urls)),
    path("map/", MapView.as_view(), name="map"),
    path(
        "locations/<int:pk>/detail/",
        LocationDetailView.as_view(),
        name="location-detail",
    ),
]
