"""Serializers."""

from __future__ import annotations

from rest_framework import serializers

from .models import Country, LifeExpectancy, SuicideMortality, Note


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name"]


class LifeExpectancySerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        source="country", queryset=Country.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = LifeExpectancy
        fields = [
            "id",
            "country",
            "country_id",
            "year",
            "status",
            "life_expectancy",
            "adult_mortality",
            "infant_deaths",
            "alcohol",
            "percentage_expenditure",
            "hepatitis_b",
            "measles",
            "bmi",
            "under_five_deaths",
            "polio",
            "total_expenditure",
            "diphtheria",
            "hiv_aids",
            "gdp",
            "population",
            "thinness_1_19_years",
            "thinness_5_9_years",
            "income_composition_of_resources",
            "schooling",
        ]

    def validate_year(self, value: int) -> int:
        if value < 1900 or value > 2025:
            raise serializers.ValidationError("Year must be within 1900–2025 for this dataset.")
        return value


class SuicideMortalitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        source="country", queryset=Country.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = SuicideMortality
        fields = [
            "id",
            "country",
            "country_id",
            "indicator_code",
            "indicator",
            "parent_location_code",
            "parent_location",
            "spatial_dim_value_code",
            "year",
            "sex",
            "rate",
            "rate_low",
            "rate_high",
            "value_text",
            "is_latest_year",
            "date_modified",
        ]


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "body", "country", "created_at"]
        read_only_fields = ["created_at"]

    def validate_title(self, value: str) -> str:
        value = (value or "").strip()
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters.")
        return value

class CountrySummaryResponseSerializer(serializers.Serializer):
    country = serializers.CharField()
    year = serializers.IntegerField()
    life_expectancy = serializers.FloatField(allow_null=True)
    status = serializers.CharField(allow_blank=True)
    suicide_rate = serializers.FloatField(allow_null=True)
    sex = serializers.CharField()
    parent_location = serializers.CharField(allow_blank=True)


class CountryTimelinePointSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    life_expectancy = serializers.FloatField(allow_null=True)
    suicide_rate = serializers.FloatField(allow_null=True)


class CountryTimelineResponseSerializer(serializers.Serializer):
    country = serializers.CharField()
    sex = serializers.CharField()
    results = CountryTimelinePointSerializer(many=True)


class RiskFlagItemSerializer(serializers.Serializer):
    country = serializers.CharField()
    year = serializers.IntegerField()
    life_expectancy = serializers.FloatField()
    suicide_rate = serializers.FloatField()


class RiskFlagsResponseSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    sex = serializers.CharField()
    count = serializers.IntegerField()
    results = RiskFlagItemSerializer(many=True)


class CorrelationResponseSerializer(serializers.Serializer):
    year_min = serializers.IntegerField()
    year_max = serializers.IntegerField()
    sex = serializers.CharField()
    n = serializers.IntegerField()
    correlation = serializers.FloatField(allow_null=True)
