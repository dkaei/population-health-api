"""Database models.

The data model is intentionally small and relational:
- Country is shared by both datasets
- LifeExpectancy and SuicideMortality store the two CSVs
- Note is a simple CRUD model to demonstrate POST/PUT/PATCH/DELETE
"""

from __future__ import annotations

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Country(models.Model):
    """Country/Location dimension used across datasets."""

    name = models.CharField(max_length=120, unique=True, db_index=True)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class LifeExpectancy(models.Model):
    """Life expectancy dataset record, keyed by (country, year)."""

    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="life_expectancy_rows")
    year = models.PositiveIntegerField(validators=[MinValueValidator(1800), MaxValueValidator(2100)], db_index=True)
    status = models.CharField(max_length=32, blank=True, default="", db_index=True)

    life_expectancy = models.FloatField(null=True, blank=True)
    adult_mortality = models.FloatField(null=True, blank=True)
    infant_deaths = models.FloatField(null=True, blank=True)
    alcohol = models.FloatField(null=True, blank=True)
    percentage_expenditure = models.FloatField(null=True, blank=True)
    hepatitis_b = models.FloatField(null=True, blank=True)
    measles = models.FloatField(null=True, blank=True)
    bmi = models.FloatField(null=True, blank=True)
    under_five_deaths = models.FloatField(null=True, blank=True)
    polio = models.FloatField(null=True, blank=True)
    total_expenditure = models.FloatField(null=True, blank=True)
    diphtheria = models.FloatField(null=True, blank=True)
    hiv_aids = models.FloatField(null=True, blank=True)
    gdp = models.FloatField(null=True, blank=True)
    population = models.FloatField(null=True, blank=True)
    thinness_1_19_years = models.FloatField(null=True, blank=True)
    thinness_5_9_years = models.FloatField(null=True, blank=True)
    income_composition_of_resources = models.FloatField(null=True, blank=True)
    schooling = models.FloatField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["country", "year"], name="uniq_life_country_year")
        ]
        indexes = [
            models.Index(fields=["year"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.country.name} ({self.year})"


class SuicideMortality(models.Model):
    """Suicide mortality rate record (per 100,000), keyed by (country, year, sex)."""

    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="suicide_rows")

    indicator_code = models.CharField(max_length=40, blank=True, default="")
    indicator = models.CharField(max_length=200, blank=True, default="")

    parent_location_code = models.CharField(max_length=40, blank=True, default="")
    parent_location = models.CharField(max_length=120, blank=True, default="")
    spatial_dim_value_code = models.CharField(max_length=40, blank=True, default="")

    year = models.PositiveIntegerField(validators=[MinValueValidator(1800), MaxValueValidator(2100)], db_index=True)
    sex = models.CharField(max_length=40, blank=True, default="", db_index=True)

    rate = models.FloatField(null=True, blank=True)
    rate_low = models.FloatField(null=True, blank=True)
    rate_high = models.FloatField(null=True, blank=True)

    value_text = models.CharField(max_length=80, blank=True, default="")
    is_latest_year = models.BooleanField(default=False)
    date_modified = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["country", "year", "sex"], name="uniq_suicide_country_year_sex")
        ]
        indexes = [
            models.Index(fields=["year"]),
            models.Index(fields=["sex"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.country.name} ({self.year}, {self.sex})"


class Note(models.Model):
    """Simple CRUD model used to demonstrate POST/PUT/PATCH/DELETE."""

    title = models.CharField(max_length=120)
    body = models.TextField(blank=True, default="")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="notes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover
        return self.title
