"""Unit tests."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from health.models import Country, LifeExpectancy, SuicideMortality


class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        sg = Country.objects.create(name="Singapore")
        my = Country.objects.create(name="Malaysia")

        LifeExpectancy.objects.create(country=sg, year=2015, status="Developed", life_expectancy=83.0)
        LifeExpectancy.objects.create(country=my, year=2015, status="Developing", life_expectancy=75.0)

        SuicideMortality.objects.create(country=sg, year=2015, sex="Both sexes", rate=5.0)
        SuicideMortality.objects.create(country=my, year=2015, sex="Both sexes", rate=6.0)

    def test_countries_list(self):
        r = self.client.get("/api/countries/")
        self.assertEqual(r.status_code, 200)

    def test_life_filter(self):
        r = self.client.get("/api/life-expectancy/?country=Singapore&year_min=2015&year_max=2015")
        self.assertEqual(r.status_code, 200)

    def test_life_top(self):
        r = self.client.get("/api/life-expectancy/top/?year=2015&n=5")
        self.assertEqual(r.status_code, 200)
        self.assertIn("results", r.json())

    def test_suicide_filter(self):
        r = self.client.get("/api/suicide-mortality/?country=Singapore&sex=Both%20sexes&year_min=2015&year_max=2015")
        self.assertEqual(r.status_code, 200)

    def test_country_summary(self):
        r = self.client.get("/api/insights/country-summary/?country=Singapore&year=2015")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["country"], "Singapore")
        self.assertEqual(data["year"], 2015)

    def test_risk_flags(self):
        r = self.client.get("/api/insights/risk-flags/?year=2015&min_life=80&min_suicide=4")
        self.assertEqual(r.status_code, 200)
        self.assertIn("results", r.json())

    def test_correlation(self):
        r = self.client.get("/api/insights/correlation/?year_min=2015&year_max=2015")
        self.assertEqual(r.status_code, 200)
        self.assertIn("n", r.json())

    def test_notes_crud(self):
        # write requires auth
        r = self.client.post("/api/notes/", {"title": "Hello", "body": "World", "country": None}, format="json")
        self.assertIn(r.status_code, [401, 403])

        # auth POST allowed
        User = get_user_model()
        u = User.objects.create_user(username="admin2", password="pass1234")
        self.client.force_authenticate(user=u)

        r = self.client.post("/api/notes/", {"title": "Hello", "body": "World", "country": None}, format="json")
        self.assertEqual(r.status_code, 201)
        note_id = r.json()["id"]

        # GET allowed
        r = self.client.get(f"/api/notes/{note_id}/")
        self.assertEqual(r.status_code, 200)

        # PATCH allowed
        r = self.client.patch(f"/api/notes/{note_id}/", {"title": "Hello2"}, format="json")
        self.assertEqual(r.status_code, 200)

        # DELETE allowed
        r = self.client.delete(f"/api/notes/{note_id}/")
        self.assertEqual(r.status_code, 204)

        # deleted note
        r = self.client.get(f"/api/notes/{note_id}/")
        self.assertEqual(r.status_code, 404)

    def test_index_page(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("WHO Health API", r.content.decode("utf-8", errors="ignore"))

    def test_note_form_page(self):
        r = self.client.get("/notes/new/")
        self.assertEqual(r.status_code, 200)

