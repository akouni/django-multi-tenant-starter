from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """Abstract base model with created/modified timestamps."""

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        abstract = True


class SwissCantons(models.TextChoices):
    """Swiss canton abbreviations."""

    AG = "AG", _("Aargau")
    AI = "AI", _("Appenzell Innerrhoden")
    AR = "AR", _("Appenzell Ausserrhoden")
    BE = "BE", _("Bern")
    BL = "BL", _("Basel-Landschaft")
    BS = "BS", _("Basel-Stadt")
    FR = "FR", _("Fribourg")
    GE = "GE", _("Geneva")
    GL = "GL", _("Glarus")
    GR = "GR", _("Graubunden")
    JU = "JU", _("Jura")
    LU = "LU", _("Lucerne")
    NE = "NE", _("Neuchatel")
    NW = "NW", _("Nidwalden")
    OW = "OW", _("Obwalden")
    SG = "SG", _("St. Gallen")
    SH = "SH", _("Schaffhausen")
    SO = "SO", _("Solothurn")
    SZ = "SZ", _("Schwyz")
    TG = "TG", _("Thurgau")
    TI = "TI", _("Ticino")
    UR = "UR", _("Uri")
    VD = "VD", _("Vaud")
    VS = "VS", _("Valais")
    ZG = "ZG", _("Zug")
    ZH = "ZH", _("Zurich")


class AddressMixin(models.Model):
    """Abstract mixin providing standard Swiss address fields."""

    street = models.CharField(_("street"), max_length=255, blank=True, default="")
    street_number = models.CharField(
        _("street number"), max_length=20, blank=True, default=""
    )
    zip_code = models.CharField(_("zip code"), max_length=10, blank=True, default="")
    city = models.CharField(_("city"), max_length=100, blank=True, default="")
    canton = models.CharField(
        _("canton"),
        max_length=2,
        choices=SwissCantons.choices,
        blank=True,
        default="",
    )

    class Meta:
        abstract = True

    @property
    def full_address(self):
        parts = filter(
            None,
            [
                f"{self.street} {self.street_number}".strip(),
                f"{self.zip_code} {self.city}".strip(),
                self.get_canton_display() if self.canton else "",
            ],
        )
        return ", ".join(parts)


class LocationType(TimeStampedModel):
    """Category/type for locations displayed on the map."""

    name = models.CharField(_("name"), max_length=100)
    icon = models.CharField(
        _("icon"),
        max_length=50,
        blank=True,
        default="",
        help_text=_("CSS icon class or emoji for map markers."),
    )
    color = models.CharField(
        _("color"),
        max_length=7,
        blank=True,
        default="#3388ff",
        help_text=_("Hex color for map markers."),
    )
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("location type")
        verbose_name_plural = _("location types")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Location(TimeStampedModel, AddressMixin):
    """A geographic point of interest displayed on the map."""

    name = models.CharField(_("name"), max_length=200)
    description = models.TextField(_("description"), blank=True, default="")
    location_type = models.ForeignKey(
        LocationType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locations",
        verbose_name=_("location type"),
    )
    point = models.PointField(
        _("coordinates"),
        srid=4326,
        null=True,
        blank=True,
        help_text=_("Geographic coordinates (longitude, latitude)."),
    )
    is_active = models.BooleanField(_("active"), default=True)
    image = models.ImageField(
        _("image"), upload_to="geomap/locations/", blank=True, null=True
    )
    website = models.URLField(_("website"), blank=True, default="")
    phone = models.CharField(_("phone"), max_length=30, blank=True, default="")
    email = models.EmailField(_("email"), blank=True, default="")

    class Meta:
        verbose_name = _("location")
        verbose_name_plural = _("locations")
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def latitude(self):
        if self.point:
            return self.point.y
        return None

    @property
    def longitude(self):
        if self.point:
            return self.point.x
        return None


class MapLayer(TimeStampedModel):
    """Configuration for tile layers or overlay layers on the map."""

    name = models.CharField(_("name"), max_length=100)
    url_template = models.URLField(
        _("URL template"),
        max_length=500,
        help_text=_(
            "Tile URL template, e.g. https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        ),
    )
    attribution = models.CharField(
        _("attribution"), max_length=300, blank=True, default=""
    )
    is_default = models.BooleanField(
        _("default layer"),
        default=False,
        help_text=_("Whether this layer is shown by default."),
    )
    is_active = models.BooleanField(_("active"), default=True)
    max_zoom = models.PositiveSmallIntegerField(_("max zoom"), default=19)
    opacity = models.FloatField(_("opacity"), default=1.0)
    sort_order = models.PositiveIntegerField(_("sort order"), default=0)

    class Meta:
        verbose_name = _("map layer")
        verbose_name_plural = _("map layers")
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name
