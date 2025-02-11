from django.urls import path
from . import views 
from .views import register, user_login, user_logout

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('home/', views.home, name='home'),
    path('parking_places/', views.manage_parking_places, name='manage_parking_places'),
    path('parking_places/<int:pk>/', views.parking_place_detail, name='parking_place_detail'),
    path('parking_fees/', views.manage_parking_fees, name='manage_parking_fees'),
    path('parking_places/edit/<int:pk>/', views.edit_parking_place, name='edit_parking_place'),
    path('parking_places/delete/<int:pk>/', views.delete_parking_place, name='delete_parking_place'),
    path('payments/', views.payments, name='payments'),
    path('logs/', views.logs, name='logs'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
