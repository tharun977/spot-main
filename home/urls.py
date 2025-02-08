from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('parking_place/', views.parking_place, name='parking_place'),
    path('log/', views.log, name='log'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('payments/', views.payments, name='payments'),
]
