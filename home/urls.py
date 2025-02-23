from django.urls import path
from . import views 
from .views import parking_lot_list, manage_staff_users, edit_staff, delete_staff , admin_dashboard


urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # ✅ Redirect Admins here
    path('home/', views.home, name='home'),  
    
    # Staff and User Dashboards
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),

    path('parking_places/<int:parking_place_id>/lots/', views.parking_lot_list, name='parking_lot_list'),
    path('parking_places/<int:parking_place_id>/add_lots/', views.add_multiple_parking_lots, name='add_parking_lots'),
    path('parking_places/<int:parking_place_id>/lots/delete/', views.delete_parking_lots, name='delete_parking_lots'),


    path('parking_places/', views.manage_parking_places, name='manage_parking_places'),
    path('parking_places/<int:pk>/', views.parking_place_detail, name='parking_place_detail'),
    path('parking_places/<int:pk>/lots/', views.parking_lot_list, name='parking_lot_list'),
    path('parking_places/edit/<int:pk>/', views.edit_parking_place, name='edit_parking_place'),
    path('parking_places/delete/<int:pk>/', views.delete_parking_place, name='delete_parking_place'),
    path('parking_fees/', views.manage_parking_fees, name='manage_parking_fees'),

    path('manage_staff_users/', manage_staff_users, name='manage_staff_users'),
    path('edit_staff/<int:staff_id>/', edit_staff, name='edit_staff'),
    path('delete_staff/<int:staff_id>/', delete_staff, name='delete_staff'),

    path('payments/', views.payments, name='payments'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),  
    path('settings/', views.settings, name='settings'),
]
