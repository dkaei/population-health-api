"""Views.

- landing page
- REST API endpoints
- HTML note form
"""

from __future__ import annotations

import platform
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import Any

import numpy as np
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema

from .filters import LifeExpectancyFilter, SuicideMortalityFilter
from .forms import NoteForm
from .models import Country, LifeExpectancy, SuicideMortality, Note
from .serializers import (
    CountrySerializer,
    LifeExpectancySerializer,
    SuicideMortalitySerializer,
    NoteSerializer,
    CountrySummaryResponseSerializer,
    CountryTimelineResponseSerializer,
    RiskFlagsResponseSerializer,
    CorrelationResponseSerializer,
)

def _pkg_ver(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "unknown"

def index(request: HttpRequest) -> HttpResponse:
    """Landing page required by the assignment spec."""

    def abs_url(path: str) -> str:
        return request.build_absolute_uri(path)

    endpoints = [
        {
            "method": "GET",
            "url": abs_url("/api/countries/?search=singapore"),
            "desc": "Search countries (DRF SearchFilter: ?search=...)",
        },
        {
            "method": "GET",
            "url": abs_url("/api/life-expectancy/?country=Singapore&year_min=2000&year_max=2015"),
            "desc": "Life expectancy filter (country + year range)",
        },
        {
            "method": "GET",
            "url": abs_url("/api/life-expectancy/top/?year=2015&n=10"),
            "desc": "Top-N life expectancy for a year",
        },
        {
            "method": "GET",
            "url": abs_url("/api/suicide-mortality/?country=Singapore&sex=Both%20sexes&year_min=2000&year_max=2015"),
            "desc": "Suicide mortality filter (country + sex + year range)",
        },
        {
            "method": "GET",
            "url": abs_url("/api/insights/country-summary/?country=Singapore&year=2015"),
            "desc": "Merged country-year summary (join across both datasets)",
        },
        {
            "method": "GET",
            "url": abs_url("/api/insights/country-timeline/?country=Singapore&year_min=2000&year_max=2015"),
            "desc": "Country timeline (trend series)",
        },
        {
            "method": "GET",
            "url": abs_url("/api/insights/risk-flags/?year=2015&min_life=60&min_suicide=10"),
            "desc": "Compound risk flag query (threshold filters)",
        },
        {
            "method": "GET",
            "url": abs_url("/api/insights/correlation/?year_min=2000&year_max=2015"),
            "desc": "Correlation analysis (advanced query endpoint)",
        },
        {"method": "POST", "url": abs_url("/api/notes/"), "desc": "Create a note (POST JSON)"},
        {"method": "HTML", "url": abs_url("/notes/new/"), "desc": "Create a note using a Django Form"},
        {"method": "DOCS", "url": abs_url("/api/docs/"), "desc": "Swagger UI (OpenAPI via drf-spectacular)"},
    ]

    context = {
        "endpoints": endpoints,
        "admin_user": "admin",
        "admin_pass": "admin1234",
        "os_info": platform.platform(),
        "python_version": sys.version.split()[0],
        "django_version": _pkg_ver("Django"),
        "packages": {
            "djangorestframework": _pkg_ver("djangorestframework"),
            "django-filter": _pkg_ver("django-filter"),
            "drf-spectacular": _pkg_ver("drf-spectacular"),
            "pandas": _pkg_ver("pandas"),
        },
        "seed_cmd": "python manage.py load_who_data",
        "test_cmd": "python manage.py test",
        "admin_url": abs_url("/admin/"),
    }
    return render(request, "index.html", context)

def note_create(request: HttpRequest) -> HttpResponse:
    """HTML form endpoint to demonstrate Django Forms + validation."""
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("index"))
    else:
        form = NoteForm()
    return render(request, "note_create.html", {"form": form})

def favicon(request: HttpRequest) -> HttpResponse:
    """Return an empty favicon response to avoid 404 noise in demo logs."""
    return HttpResponse(status=204)


class CountryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Country.objects.all().order_by("name")
    serializer_class = CountrySerializer
    search_fields = ["name"]

class LifeExpectancyViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = LifeExpectancy.objects.select_related("country").all().order_by("country__name", "year")
    serializer_class = LifeExpectancySerializer
    filterset_class = LifeExpectancyFilter
    search_fields = ["country__name", "status"]
    ordering_fields = ["year", "life_expectancy"]

    @action(detail=False, methods=["get"], url_path="top")
    def top(self, request: Request) -> Response:
        """Top-N countries by life expectancy for a given year (optional: status filter)."""
        year = int(request.query_params.get("year", "2015"))
        n = int(request.query_params.get("n", "10"))
        status_filter = request.query_params.get("status")

        qs = self.get_queryset().filter(year=year).exclude(life_expectancy__isnull=True)
        if status_filter:
            qs = qs.filter(status__iexact=status_filter)
        qs = qs.order_by("-life_expectancy")[: max(1, min(n, 50))]

        data = [
            {
                "country": row.country.name,
                "year": row.year,
                "status": row.status,
                "life_expectancy": row.life_expectancy,
            }
            for row in qs
        ]
        return Response({"year": year, "count": len(data), "results": data})

class SuicideMortalityViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = SuicideMortality.objects.select_related("country").all().order_by("country__name", "year")
    serializer_class = SuicideMortalitySerializer
    filterset_class = SuicideMortalityFilter
    search_fields = ["country__name", "sex", "parent_location"]
    ordering_fields = ["year", "rate"]

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.select_related("country").all().order_by("-created_at")
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ["title", "body", "country__name"]
    ordering_fields = ["created_at", "title"]

class CountrySummary(APIView):
    """Join both datasets for a single country-year."""

    @extend_schema(responses=CountrySummaryResponseSerializer)
    def get(self, request: Request) -> Response:
        country_name = (request.query_params.get("country") or "").strip()
        year = int(request.query_params.get("year", "2015"))
        sex = request.query_params.get("sex") or "Both sexes"

        if not country_name:
            return Response({"error": "country param is required"}, status=status.HTTP_400_BAD_REQUEST)

        country = Country.objects.filter(name__iexact=country_name).first()
        if not country:
            return Response({"error": "country not found"}, status=status.HTTP_404_NOT_FOUND)

        life = LifeExpectancy.objects.filter(country=country, year=year).first()
        suicide = SuicideMortality.objects.filter(country=country, year=year, sex__iexact=sex).first()

        return Response(
            {
                "country": country.name,
                "year": year,
                "life_expectancy": None if not life else life.life_expectancy,
                "status": "" if not life else life.status,
                "suicide_rate": None if not suicide else suicide.rate,
                "sex": sex,
                "parent_location": "" if not suicide else suicide.parent_location,
            }
        )

class CountryTimeline(APIView):
    """Return a timeline (year series) for a country, merging both datasets."""

    @extend_schema(responses=CountryTimelineResponseSerializer)
    def get(self, request: Request) -> Response:
        country_name = (request.query_params.get("country") or "").strip()
        year_min = int(request.query_params.get("year_min", "2000"))
        year_max = int(request.query_params.get("year_max", "2015"))
        sex = request.query_params.get("sex") or "Both sexes"

        if not country_name:
            return Response({"error": "country param is required"}, status=status.HTTP_400_BAD_REQUEST)

        country = Country.objects.filter(name__iexact=country_name).first()
        if not country:
            return Response({"error": "country not found"}, status=status.HTTP_404_NOT_FOUND)

        years = list(range(year_min, year_max + 1))
        life_map = {r.year: r for r in LifeExpectancy.objects.filter(country=country, year__gte=year_min, year__lte=year_max)}
        sui_map = {r.year: r for r in SuicideMortality.objects.filter(country=country, year__gte=year_min, year__lte=year_max, sex__iexact=sex)}

        results = []
        for y in years:
            life = life_map.get(y)
            sui = sui_map.get(y)
            results.append(
                {
                    "year": y,
                    "life_expectancy": None if not life else life.life_expectancy,
                    "suicide_rate": None if not sui else sui.rate,
                }
            )

        return Response({"country": country.name, "sex": sex, "results": results})

class RiskFlags(APIView):
    """Compound query: low life expectancy AND high suicide rate for a year."""

    @extend_schema(responses=RiskFlagsResponseSerializer)
    def get(self, request: Request) -> Response:
        year = int(request.query_params.get("year", "2015"))
        min_life = float(request.query_params.get("min_life", "60"))
        min_suicide = float(request.query_params.get("min_suicide", "10"))
        sex = request.query_params.get("sex") or "Both sexes"

        life_qs = LifeExpectancy.objects.select_related("country").filter(year=year, life_expectancy__lte=min_life).exclude(life_expectancy__isnull=True)
        sui_qs = SuicideMortality.objects.select_related("country").filter(year=year, sex__iexact=sex, rate__gte=min_suicide).exclude(rate__isnull=True)

        life_countries = {r.country_id: r for r in life_qs}
        results = []
        for s in sui_qs:
            life = life_countries.get(s.country_id)
            if not life:
                continue
            results.append(
                {
                    "country": s.country.name,
                    "year": year,
                    "life_expectancy": life.life_expectancy,
                    "suicide_rate": s.rate,
                }
            )

        results.sort(key=lambda x: (x["life_expectancy"] if x["life_expectancy"] is not None else 9999, -(x["suicide_rate"] or 0)))
        return Response({"year": year, "sex": sex, "count": len(results), "results": results})

class Correlation(APIView):
    """Compute Pearson correlation between life expectancy and suicide rate over a year range.

    For each country:
      - life = average life expectancy in range
      - suicide = average suicide rate in range (sex filter)
    Then correlate across countries (advanced technique).
    """

    @extend_schema(responses=CorrelationResponseSerializer)
    def get(self, request: Request) -> Response:
        year_min = int(request.query_params.get("year_min", "2000"))
        year_max = int(request.query_params.get("year_max", "2015"))
        sex = request.query_params.get("sex") or "Both sexes"

        # Aggregate per country in python for clarity (dataset is small).
        pairs: list[tuple[float, float]] = []
        countries = Country.objects.all()

        for c in countries:
            life_vals = list(
                LifeExpectancy.objects.filter(country=c, year__gte=year_min, year__lte=year_max)
                .exclude(life_expectancy__isnull=True)
                .values_list("life_expectancy", flat=True)
            )
            sui_vals = list(
                SuicideMortality.objects.filter(country=c, year__gte=year_min, year__lte=year_max, sex__iexact=sex)
                .exclude(rate__isnull=True)
                .values_list("rate", flat=True)
            )

            if not life_vals or not sui_vals:
                continue

            life_avg = float(np.mean(life_vals))
            sui_avg = float(np.mean(sui_vals))
            pairs.append((life_avg, sui_avg))

        if len(pairs) < 3:
            return Response(
                {"year_min": year_min, "year_max": year_max, "sex": sex, "n": len(pairs), "correlation": None},
                status=status.HTTP_200_OK,
            )

        xs = np.array([p[0] for p in pairs], dtype=float)
        ys = np.array([p[1] for p in pairs], dtype=float)
        corr = float(np.corrcoef(xs, ys)[0, 1])

        return Response(
            {
                "year_min": year_min,
                "year_max": year_max,
                "sex": sex,
                "n": len(pairs),
                "correlation": corr,
            }
        )
