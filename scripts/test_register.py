import os
import sys

# Ensure project root is on path
proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MassageSpa.settings')

import django
django.setup()

from django.contrib.auth.models import User

print('Django initialized. DB engine:', __import__('django.conf').conf.settings.DATABASES)

try:
    username = 'test_user_auto'
    email = 'test_user_auto@example.com'
    password = 'testing123'
    # If user exists, delete to test creation
    existing = User.objects.filter(username=username)
    if existing.exists():
        print('Existing test user found; deleting')
        existing.delete()
    user = User.objects.create_user(username=username, email=email, password=password)
    print('User created:', user.username, user.email)
except Exception as e:
    import traceback
    print('Error creating user:', e)
    traceback.print_exc()

# Report counts
try:
    print('Total users:', User.objects.count())
except Exception as e:
    print('Error counting users:', e)
    import traceback
    traceback.print_exc()
