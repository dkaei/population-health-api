# Generated manually for submission reproducibility.
# Creates all health app tables.

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Country",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(db_index=True, max_length=120, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="LifeExpectancy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("year", models.PositiveIntegerField(db_index=True, validators=[django.core.validators.MinValueValidator(1800), django.core.validators.MaxValueValidator(2100)])),
                ("status", models.CharField(blank=True, db_index=True, default="", max_length=32)),
                ("life_expectancy", models.FloatField(blank=True, null=True)),
                ("adult_mortality", models.FloatField(blank=True, null=True)),
                ("infant_deaths", models.FloatField(blank=True, null=True)),
                ("alcohol", models.FloatField(blank=True, null=True)),
                ("percentage_expenditure", models.FloatField(blank=True, null=True)),
                ("hepatitis_b", models.FloatField(blank=True, null=True)),
                ("measles", models.FloatField(blank=True, null=True)),
                ("bmi", models.FloatField(blank=True, null=True)),
                ("under_five_deaths", models.FloatField(blank=True, null=True)),
                ("polio", models.FloatField(blank=True, null=True)),
                ("total_expenditure", models.FloatField(blank=True, null=True)),
                ("diphtheria", models.FloatField(blank=True, null=True)),
                ("hiv_aids", models.FloatField(blank=True, null=True)),
                ("gdp", models.FloatField(blank=True, null=True)),
                ("population", models.FloatField(blank=True, null=True)),
                ("thinness_1_19_years", models.FloatField(blank=True, null=True)),
                ("thinness_5_9_years", models.FloatField(blank=True, null=True)),
                ("income_composition_of_resources", models.FloatField(blank=True, null=True)),
                ("schooling", models.FloatField(blank=True, null=True)),
                ("country", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="life_expectancy_rows", to="health.country")),
            ],
            options={
                "indexes": [models.Index(fields=["year"], name="health_life_year_8d0d3a_idx"), models.Index(fields=["status"], name="health_life_status_2df3c4_idx")],
            },
        ),
        migrations.CreateModel(
            name="SuicideMortality",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("indicator_code", models.CharField(blank=True, default="", max_length=40)),
                ("indicator", models.CharField(blank=True, default="", max_length=200)),
                ("parent_location_code", models.CharField(blank=True, default="", max_length=40)),
                ("parent_location", models.CharField(blank=True, default="", max_length=120)),
                ("spatial_dim_value_code", models.CharField(blank=True, default="", max_length=40)),
                ("year", models.PositiveIntegerField(db_index=True, validators=[django.core.validators.MinValueValidator(1800), django.core.validators.MaxValueValidator(2100)])),
                ("sex", models.CharField(blank=True, db_index=True, default="", max_length=40)),
                ("rate", models.FloatField(blank=True, null=True)),
                ("rate_low", models.FloatField(blank=True, null=True)),
                ("rate_high", models.FloatField(blank=True, null=True)),
                ("value_text", models.CharField(blank=True, default="", max_length=80)),
                ("is_latest_year", models.BooleanField(default=False)),
                ("date_modified", models.CharField(blank=True, default="", max_length=40)),
                ("country", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="suicide_rows", to="health.country")),
            ],
            options={
                "indexes": [models.Index(fields=["year"], name="health_sui_year_6be1db_idx"), models.Index(fields=["sex"], name="health_sui_sex_0a8a55_idx")],
            },
        ),
        migrations.CreateModel(
            name="Note",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120)),
                ("body", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("country", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="notes", to="health.country")),
            ],
        ),
        migrations.AddConstraint(
            model_name="lifeexpectancy",
            constraint=models.UniqueConstraint(fields=("country", "year"), name="uniq_life_country_year"),
        ),
        migrations.AddConstraint(
            model_name="suicidemortality",
            constraint=models.UniqueConstraint(fields=("country", "year", "sex"), name="uniq_suicide_country_year_sex"),
        ),
    ]
