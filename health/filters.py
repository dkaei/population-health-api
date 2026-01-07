"""django-filter FilterSets for clean, reusable query filtering."""

import django_filters

from .models import LifeExpectancy, SuicideMortality


class LifeExpectancyFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(field_name="country__name", lookup_expr="icontains")
    year_min = django_filters.NumberFilter(field_name="year", lookup_expr="gte")
    year_max = django_filters.NumberFilter(field_name="year", lookup_expr="lte")

    class Meta:
        model = LifeExpectancy
        fields = ["country", "status", "year_min", "year_max"]


class SuicideMortalityFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(field_name="country__name", lookup_expr="icontains")
    year_min = django_filters.NumberFilter(field_name="year", lookup_expr="gte")
    year_max = django_filters.NumberFilter(field_name="year", lookup_expr="lte")

    class Meta:
        model = SuicideMortality
        fields = ["country", "sex", "year_min", "year_max"]
