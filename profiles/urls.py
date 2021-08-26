from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView

from rest_framework import routers

from .sitemaps import HomeSitemap, FaqSitemap, \
     ListSitemap, ProfilesSitemap
from . import views

router = routers.DefaultRouter()
router.register(r'api/countries', views.RepresentedCountriesViewSet)
router.register(r'api/positions', views.TopPositionsViewSet)


sitemaps = {
    'home': HomeSitemap,
    'list': ListSitemap,
    'faq': FaqSitemap,
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

    path('faq/', TemplateView.as_view(template_name='profiles/FAQs.html'),
         name='faq'),

    path('profiles-autocomplete/', views.ProfilesAutocomplete.as_view(),
         name='profiles_autocomplete'),
    path('countries-autocomplete/', views.CountriesAutocomplete.as_view(),
         name='countries_autocomplete'),

    path('account/', views.UserView.as_view(),
         name='user'),
    path('account/edit/', views.UserEditView.as_view(),
         name='user_edit'),
    path('account/change_password/', views.UserChangePasswordView.as_view(),
         name='user_change_password'),
    path('account/delete/', views.UserDeleteView.as_view(),
         name='user_delete'),

    path('profile/', views.UserProfileView.as_view(),
         name='user_profile'),
    path('profile/edit/', views.UserProfileEditView.as_view(),
         name='user_profile_edit'),

    path('signup/', views.UserCreateView.as_view(),
         name='signup'),
    path('signup/confirm/', views.UserCreateConfirmView.as_view(),
         name='signup_confirm'),
    path('login/', LoginView.as_view(),
         name='login'),
    path('logout/', LogoutView.as_view(),
         name='logout'),
    path('login/forgot', views.UserPasswordResetView.as_view(),
         name='forgot'),
    path('login/forgot/confirm', views.UserPasswordResetConfirmView.as_view(),
         name='forgot_confirm'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),

    path('', include(router.urls)),
#     path('api/', include('rest_framework.urls', namespace='rest_framework')),
]
