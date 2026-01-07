"""Admin registration for quick inspection of the seeded data."""

from django.contrib import admin

from .models import Country, LifeExpectancy, SuicideMortality, Note


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(LifeExpectancy)
class LifeExpectancyAdmin(admin.ModelAdmin):
    list_display = ("country", "year", "status", "life_expectancy")
    list_filter = ("status", "year")
    search_fields = ("country__name",)
    ordering = ("country__name", "-year")


@admin.register(SuicideMortality)
class SuicideMortalityAdmin(admin.ModelAdmin):
    list_display = ("country", "year", "sex", "rate")
    list_filter = ("sex", "year")
    search_fields = ("country__name", "parent_location")
    ordering = ("country__name", "-year")


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "country", "created_at")
    search_fields = ("title", "body", "country__name")
    ordering = ("-created_at",)
