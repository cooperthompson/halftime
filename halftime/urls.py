"""halftime URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from rest_framework import routers
from api.views import *
from django.contrib import admin

from game_schedules.autocomplete import TeamAutocomplete
import game_schedules.views as game_schedule_views
import api.views as api_views
import webcal.views as webcal_views

from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = settings.ADMIN_SITE_HEADER

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'fields', FieldViewSet)
router.register(r'seasons', SeasonViewSet)
router.register(r'leagues', LeagueViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'games', GameViewSet)

urlpatterns = [
    url(r'^$', game_schedule_views.home_view, name='home'),
    url(r'^team/$', game_schedule_views.team_view, name='team'),
    url(r'^league/$', game_schedule_views.league_view, name='league'),
    url(r'^admin/', admin.site.urls),
    url(r'^api/events/', api_views.team_events, name='events'),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^team-autocomplete/$', TeamAutocomplete.as_view(), name='team-autocomplete'),
    url(r'^webcal/', webcal_views.ics)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
