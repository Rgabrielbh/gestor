from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# API routes
api_patterns = [
    path("auth/",          include("apps.colaboradores.urls_auth")),
    path("colaboradores/", include("apps.colaboradores.urls_api")),
    path("clientes/",      include("apps.clientes.urls_api")),
    path("contratos/",     include("apps.contratos.urls_api")),
    path("projetos/",      include("apps.projetos.urls_api")),
    path("notebooks/",     include("apps.notebooks.urls_api")),
    path("dashboard/",     include("apps.dashboard.urls_api")),
    path("relatorios/",    include("apps.relatorios.urls_api")),
    path("schema/",        SpectacularAPIView.as_view(), name="schema"),
]

urlpatterns = [
    path("admin/",     admin.site.urls),
    path("i18n/",      include("django.conf.urls.i18n")),
    path("api/v1/",    include(api_patterns)),
    path("api/docs/",  SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("",           RedirectView.as_view(url="/dashboard/", permanent=False)),
]

# Frontend views (i18n)
urlpatterns += i18n_patterns(
    path("auth/",          include("apps.colaboradores.urls_frontend")),
    path("dashboard/",     include("apps.dashboard.urls_frontend")),
    path("colaboradores/", include("apps.colaboradores.urls_views")),
    path("clientes/",      include("apps.clientes.urls_views")),
    path("contratos/",     include("apps.contratos.urls_views")),
    path("projetos/",      include("apps.projetos.urls_views")),
    path("notebooks/",     include("apps.notebooks.urls_views")),
    path("relatorios/",    include("apps.relatorios.urls_views")),
    path("timeline/",      include("apps.timeline.urls")),
    path("usuarios/",      include("apps.usuarios.urls")),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
