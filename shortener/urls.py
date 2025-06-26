from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.views.decorators.csrf import csrf_exempt
from .views import CustomLogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('my-urls/', views.my_urls, name='my_urls'),
    path('shorten/', views.shorten_url, name='shorten_url'),
    path('stats/<str:short_code>/', views.url_stats, name='url_stats'),
    path('api/urls/', views.api_urls, name='api_urls'),
    path('<str:short_code>/', views.redirect_url, name='redirect_url'),
]