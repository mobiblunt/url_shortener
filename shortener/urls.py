from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('shorten/', views.shorten_url, name='shorten_url'),
    path('stats/<str:short_code>/', views.url_stats, name='url_stats'),
    path('api/urls/', views.api_urls, name='api_urls'),
    path('<str:short_code>/', views.redirect_url, name='redirect_url'),
]