from django.urls import path
from . import views 
from .views import parking_lot_list, add_parking_lot, edit_parking_lot, delete_parking_lot


urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),

    # ✅ Redirect Admins here
    path('home/', views.home, name='home'),  
    
    # Staff and User Dashboards
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),

    path('parking_place/<int:pk>/lots/', parking_lot_list, name='parking_lot_list'),
    path('parking_place/<int:pk>/lots/add/', add_parking_lot, name='add_parking_lot'),
    path('parking_place/lots/<int:lot_pk>/edit/', edit_parking_lot, name='edit_parking_lot'),
    path('parking_place/lots/<int:lot_pk>/delete/', delete_parking_lot, name='delete_parking_lot'),

    path('parking_places/', views.manage_parking_places, name='manage_parking_places'),
    path('parking_places/<int:pk>/', views.parking_place_detail, name='parking_place_detail'),
    path('parking_places/<int:pk>/lots/', views.parking_lot_list, name='parking_lot_list'),
    path('parking_places/edit/<int:pk>/', views.edit_parking_place, name='edit_parking_place'),
    path('parking_places/delete/<int:pk>/', views.delete_parking_place, name='delete_parking_place'),
    path('parking_fees/', views.manage_parking_fees, name='manage_parking_fees'),

    path('payments/', views.payments, name='payments'),
    path('logs/', views.logs, name='logs'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),  
    path('settings/', views.settings, name='settings'),
]
