from django.db import models

class Booking(models.Model):
    # SERVICE_CHOICES kept for backward compatibility with older views/forms
    # (some code expects these labels). Service authoritative data lives in
    # the `Service` model; this constant is only a fallback and does not
    # change the database schema.
    SERVICE_CHOICES = [
        ('swedish', 'Swedish Massage'),
        ('hotstone', 'Hot Stone Therapy'),
        ('aroma', 'Aromatherapy'),
        ('deeptissue', 'Deep Tissue'),
        ('footspa', 'Foot Spa & Reflexology'),
        ('couples', 'Couples Retreat'),
    ]

    # THERAPIST_CHOICES is kept as a convenience for form dropdowns / UI.
    # The `therapist` field stores free-text (or a choice key) so views/templates
    # can accept either a human-friendly name or a short code. This avoids
    # validation errors if the UI supplies a full name instead of a key.
    THERAPIST_CHOICES = [
        ('cris', 'Cris Adrian Aquino'),
        ('rodel', 'Rodel Cabanos'),
        ('rhomar', 'Rhomar Manarang'),
    ]

    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField()
    customer_address = models.CharField(max_length=255, blank=True)
    
    # Allow storing either a therapist code (from THERAPIST_CHOICES) or a free-text name.
    # Using a larger max_length and allowing blank avoids validation errors when views
    # set the therapist to a full name instead of the choice key.
    therapist = models.CharField(max_length=100, blank=True)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    notification_seen = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.customer_name} - {self.service} on {self.date} at {self.time}"

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)

class Employee(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('On Leave', 'On Leave')], default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.title}"

class DailyBookingStat(models.Model):
    date = models.DateField(unique=True)
    total_bookings = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} — {self.total_bookings} bookings"

class MonthlyRevenue(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ('year', 'month')
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.year}-{self.month:02d} — ₱{self.total_revenue}"
