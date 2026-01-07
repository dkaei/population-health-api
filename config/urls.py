"""Root URLs."""

from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from health.views import index, note_create, favicon

urlpatterns = [
    path("", index, name="index"),
    path("admin/", admin.site.urls),
    path("notes/new/", note_create, name="note-create"),
    path("favicon.ico", favicon, name="favicon"),

    # API routes
    path("api/", include("health.urls")),

    # OpenAPI + Swagger UI (linked from landing page)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
