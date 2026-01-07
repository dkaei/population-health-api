"""Bulk load WHO CSV files into SQLite.

Required deliverable:
- load and store script (bulk load)
- performs basic cleaning and type conversion
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from health.models import Country, LifeExpectancy, SuicideMortality


def _to_float(v: Any) -> Optional[float]:
    try:
        if v is None:
            return None
        if isinstance(v, float) and pd.isna(v):
            return None
        if isinstance(v, str) and v.strip() == "":
            return None
        return float(v)
    except Exception:
        return None


def _to_int(v: Any) -> Optional[int]:
    try:
        if v is None:
            return None
        if isinstance(v, float) and pd.isna(v):
            return None
        if isinstance(v, str) and v.strip() == "":
            return None
        return int(float(v))
    except Exception:
        return None


class Command(BaseCommand):
    help = "Loads WHO life expectancy and suicide mortality CSVs into SQLite."

    def add_arguments(self, parser):
        parser.add_argument("--life", type=str, default="data/life-expectancy-who.csv")
        parser.add_argument("--suicide", type=str, default="data/suicide-rates-who-filtered.csv")

    @transaction.atomic
    def handle(self, *args, **options):
        base_dir = Path.cwd()
        life_path = (base_dir / options["life"]).resolve()
        suicide_path = (base_dir / options["suicide"]).resolve()

        if not life_path.exists():
            self.stderr.write(f"Life CSV not found: {life_path}")
            return
        if not suicide_path.exists():
            self.stderr.write(f"Suicide CSV not found: {suicide_path}")
            return

        self.stdout.write(f"Loading life dataset from: {life_path}")
        life_df = pd.read_csv(life_path)
        self.stdout.write(f"Loading suicide dataset from: {suicide_path}")
        sui_df = pd.read_csv(suicide_path)

        # Countries from both datasets
        countries = set(life_df["country"].dropna().astype(str).str.strip())
        countries |= set(sui_df["Location"].dropna().astype(str).str.strip())

        existing = set(Country.objects.filter(name__in=list(countries)).values_list("name", flat=True))
        to_create = [Country(name=name) for name in sorted(countries) if name not in existing]
        if to_create:
            Country.objects.bulk_create(to_create, ignore_conflicts=True)

        country_map = {c.name: c for c in Country.objects.all()}

        # LifeExpectancy rows
        life_rows = []
        for _, r in life_df.iterrows():
            name = str(r.get("country", "")).strip()
            c = country_map.get(name)
            if not c:
                continue

            year = _to_int(r.get("year"))
            if year is None:
                continue

            life_rows.append(
                LifeExpectancy(
                    country=c,
                    year=year,
                    status=str(r.get("status", "") or "").strip(),
                    life_expectancy=_to_float(r.get("life_expectancy")),
                    adult_mortality=_to_float(r.get("adult_mortality")),
                    infant_deaths=_to_float(r.get("infant_deaths")),
                    alcohol=_to_float(r.get("alcohol")),
                    percentage_expenditure=_to_float(r.get("percentage_expenditure")),
                    hepatitis_b=_to_float(r.get("hepatitis_b")),
                    measles=_to_float(r.get("measles")),
                    bmi=_to_float(r.get("bmi")),
                    under_five_deaths=_to_float(r.get("under_five_deaths")),
                    polio=_to_float(r.get("polio")),
                    total_expenditure=_to_float(r.get("total_expenditure")),
                    diphtheria=_to_float(r.get("diphtheria")),
                    hiv_aids=_to_float(r.get("hiv_aids")),
                    gdp=_to_float(r.get("gdp")),
                    population=_to_float(r.get("population")),
                    thinness_1_19_years=_to_float(r.get("thinness_1_19_years")),
                    thinness_5_9_years=_to_float(r.get("thinness_5_9_years")),
                    income_composition_of_resources=_to_float(r.get("income_composition_of_resources")),
                    schooling=_to_float(r.get("schooling")),
                )
            )

        if life_rows:
            LifeExpectancy.objects.bulk_create(life_rows, ignore_conflicts=True)
        self.stdout.write(f"Inserted LifeExpectancy rows: {len(life_rows)} (duplicates ignored)")

        # SuicideMortality rows
        sui_rows = []
        for _, r in sui_df.iterrows():
            name = str(r.get("Location", "")).strip()
            c = country_map.get(name)
            if not c:
                continue

            year = _to_int(r.get("Period"))
            if year is None:
                continue

            sex = str(r.get("Dim1", "") or "").strip()

            sui_rows.append(
                SuicideMortality(
                    country=c,
                    indicator_code=str(r.get("IndicatorCode", "") or "").strip(),
                    indicator=str(r.get("Indicator", "") or "").strip(),
                    parent_location_code=str(r.get("ParentLocationCode", "") or "").strip(),
                    parent_location=str(r.get("ParentLocation", "") or "").strip(),
                    spatial_dim_value_code=str(r.get("SpatialDimValueCode", "") or "").strip(),
                    year=year,
                    sex=sex,
                    rate=_to_float(r.get("FactValueNumeric")),
                    rate_low=_to_float(r.get("FactValueNumericLow")),
                    rate_high=_to_float(r.get("FactValueNumericHigh")),
                    value_text=str(r.get("Value", "") or "").strip(),
                    is_latest_year=str(r.get("IsLatestYear", "") or "").strip().lower() in ("true", "1", "yes"),
                    date_modified=str(r.get("DateModified", "") or "").strip(),
                )
            )

        if sui_rows:
            SuicideMortality.objects.bulk_create(sui_rows, ignore_conflicts=True)
        self.stdout.write(f"Inserted SuicideMortality rows: {len(sui_rows)} (duplicates ignored)")

        self.stdout.write("Done.")
