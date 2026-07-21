from django.urls import path
from . import views

app_name = 'massage_app'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('index/', views.index, name='index'),
    path('services/', views.services, name='services'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('book-now/', views.booknow, name='booknow'),
    path('login/', views.login_view, name='login'),
    path('login.html', views.login_view, name='login_html'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('register/', views.register_view, name='register'),
    # Service CRUD
    path('admin-dashboard/service/add/', views.add_service, name='add-service'),
    path('admin-dashboard/service/<int:service_id>/edit/', views.edit_service, name='edit-service'),
    path('admin-dashboard/service/<int:service_id>/delete/', views.delete_service, name='delete-service'),
    path('services/version/', views.services_version, name='services-version'),
    path('admin-dashboard/bookings/version/', views.bookings_version, name='bookings-version'),
    # Booking CRUD
    path('admin-dashboard/booking/<int:booking_id>/delete/', views.delete_booking, name='delete-booking'),
    # Notification AJAX
    path('admin-dashboard/mark-notifications-seen/', views.mark_notifications_seen, name='mark-notifications-seen'),
    # Employee AJAX
    path('admin-dashboard/add-employee/', views.add_employee, name='add-employee'),
    path('admin-dashboard/employee/<int:emp_id>/edit/', views.edit_employee, name='edit-employee'),
    path('admin-dashboard/employee/<int:emp_id>/delete/', views.delete_employee, name='delete-employee'),
    # Booking status AJAX
    path('update-booking-status/<int:booking_id>/', views.update_booking_status, name='update-booking-status'),
]
