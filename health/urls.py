"""API URLs."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CountryViewSet,
    LifeExpectancyViewSet,
    SuicideMortalityViewSet,
    NoteViewSet,
    CountrySummary,
    CountryTimeline,
    RiskFlags,
    Correlation,
)

router = DefaultRouter()
router.register(r"countries", CountryViewSet, basename="countries")
router.register(r"life-expectancy", LifeExpectancyViewSet, basename="life-expectancy")
router.register(r"suicide-mortality", SuicideMortalityViewSet, basename="suicide-mortality")
router.register(r"notes", NoteViewSet, basename="notes")

urlpatterns = [
    # REST API
    path("", include(router.urls)),

    # Custom "interesting" endpoints
    path("insights/country-summary/", CountrySummary.as_view(), name="country-summary"),
    path("insights/country-timeline/", CountryTimeline.as_view(), name="country-timeline"),
    path("insights/risk-flags/", RiskFlags.as_view(), name="risk-flags"),
    path("insights/correlation/", Correlation.as_view(), name="correlation"),
]