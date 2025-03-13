from django.urls import path
from . import views 
from .views import manage_staff_users, edit_staff, delete_staff , admin_dashboard , ParkingDetails , update_out_time , make_payment , delete_parking , parking_lot_details , parking_lot_details , parking_lot_list


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
    path('parking_places/<int:parking_place_id>/lots/', views.parking_lot_list, name='parking_lots_by_place'),
    path('parking_places/edit/<int:pk>/', views.edit_parking_place, name='edit_parking_place'),
    path('parking_places/delete/<int:pk>/', views.delete_parking_place, name='delete_parking_place'),

    path('parking_lots/', views.parking_lot_list, name='parking_lot_list'),  # ✅ No ID = Show all lots
    path("parking_lots/<int:lot_id>/", parking_lot_details, name="parking_lot_details"),
    path('parking_lots/<int:lot_id>/add/', views.add_parking, name='add_parking'),
    path('parking/<uuid:parking_id>/checkout/', views.checkout_parking, name='checkout_parking'),

    path('parking_lots/<int:parking_place_id>/', views.parking_lot_list, name='parking_lots_by_place'),  # ✅ ID = Filter by place

    path('delete_parking/<uuid:parking_id>/', views.delete_parking, name='delete_parking'),
    path('parking_details/<int:lot_id>/', views.parking_lot_details, name='parking_lot_details'),
    
    path('update_out_time/<uuid:parking_id>/', update_out_time, name='update_out_time'),
    path('make_payment/<uuid:parking_id>/', make_payment, name='make_payment'),

    path('parking_lots/<int:lot_id>/', views.parking_lot_details, name='parking_lot_details'),

    path('manage_staff_users/', manage_staff_users, name='manage_staff_users'),
    path('edit_staff/<int:staff_id>/', edit_staff, name='edit_staff'),
    path('delete_staff/<int:staff_id>/', delete_staff, name='delete_staff'),

    path('manage_parking_fees/', views.manage_parking_fees, name='manage_parking_fees'),
    path('edit_parking_fee/<int:pk>/', views.edit_parking_fee, name='edit_parking_fee'),  
    path('delete_parking_fee/<int:pk>/', views.delete_parking_fee, name='delete_parking_fee'),


    
    path('payments/', views.payments, name='payments'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),  
    path('settings/', views.settings, name='settings'),
]
