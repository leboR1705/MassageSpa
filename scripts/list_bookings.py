import os, sys
proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MassageSpa.settings')
import django
django.setup()
from massage_app.models import Booking
print('Total bookings:', Booking.objects.count())
for b in Booking.objects.all().order_by('-created_at')[:10]:
    print(b.id, b.customer_name, b.customer_email, b.status, b.created_at)
