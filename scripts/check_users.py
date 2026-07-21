import os, sys
proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MassageSpa.settings')
import django
django.setup()
from django.contrib.auth.models import User

print('Total users:', User.objects.count())
print('Last 10 users:')
for u in User.objects.all().order_by('-id')[:10]:
    print('-', u.id, u.username, u.email)

print('\nExists test_user_auto:', User.objects.filter(username='test_user_auto').exists())
print('Exists test_user_auto2:', User.objects.filter(username='test_user_auto2').exists())
