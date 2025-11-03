from django.contrib import admin

# Register your models here.
from .models import Customer, Service, Booking
admin.site.register(Customer)
admin.site.register(Service)
admin.site.register(Booking)