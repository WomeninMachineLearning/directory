from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from rest_framework import routers

from .sitemaps import HomeSitemap, FaqSitemap, AboutSitemap, \
     ListSitemap, ProfilesSitemap
from . import views

router = routers.DefaultRouter()
router.register(r'api/countries', views.RepresentedCountriesViewSet)
router.register(r'api/positions', views.TopPositionsViewSet)


sitemaps = {
    'home': HomeSitemap,
    'list': ListSitemap,
    'faq': FaqSitemap,
    'about': AboutSitemap,
    'profiles': ProfilesSitemap,
}

app_name = 'profiles'

urlpatterns = [
    path('', TemplateView.as_view(template_name='profiles/home.html'),
         name='home'),
    path('list/', views.ListProfiles.as_view(),
         name='index'),
    path('list/<int:pk>/', views.ProfileDetail.as_view(),
         name='detail'),
    path('list/<int:pk>/edit', views.UpdateProfile.as_view(),
         name='edit'),
    path('list/create', views.CreateProfile.as_view(),
         name='create'),
    path('faq/', TemplateView.as_view(template_name='profiles/FAQs.html'),
         name='faq'),
    path('tips/', TemplateView.as_view(template_name='profiles/tips.html'),
         name='tips'),
    path('about/', TemplateView.as_view(template_name='profiles/about.html'),
         name='about'),
    path('profiles-autocomplete', views.ProfilesAutocomplete.as_view(),
         name='profiles_autocomplete'),
    path('countries-autocomplete', views.CountriesAutocomplete.as_view(),
         name='countries_autocomplete'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path('', include(router.urls)),
]
