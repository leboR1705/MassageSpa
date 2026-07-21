from django.contrib import admin
from .models import Service, Booking, Customer, Employee, DailyBookingStat, MonthlyRevenue


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_email', 'service', 'date', 'time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('customer_name', 'customer_email', 'service')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'created_at')
    search_fields = ('name', 'title')


@admin.register(DailyBookingStat)
class DailyBookingStatAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_bookings')


@admin.register(MonthlyRevenue)
class MonthlyRevenueAdmin(admin.ModelAdmin):
    list_display = ('year', 'month', 'total_revenue')
