from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('parking_places/', views.parking_places, name='parking_places'),
    path('parking_places/edit/<int:pk>/', views.edit_parking_place, name='edit_parking_place'),
    path('parking_places/delete/<int:pk>/', views.delete_parking_place, name='delete_parking_place'),
    path('payments/', views.payments, name='payments'),
    path('logs/', views.logs, name='logs'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
