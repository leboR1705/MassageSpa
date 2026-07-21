import re
import json
from urllib import request, parse
import http.cookiejar

SERVICE_ID = 13
BASE = 'http://127.0.0.1:8000'
ADMIN_URL = BASE + '/admin-dashboard/'
EDIT_URL = BASE + f'/admin-dashboard/service/{SERVICE_ID}/edit/'

cj = http.cookiejar.CookieJar()
opener = request.build_opener(request.HTTPCookieProcessor(cj))
print('Fetching admin dashboard to obtain CSRF token and cookies...')
resp = opener.open(ADMIN_URL)
html = resp.read().decode('utf-8')
# look for csrf token in hidden input
m = re.search(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']', html)
if not m:
    print('CSRF token not found in HTML. Showing a small snippet:')
    print(html[:1200])
    raise SystemExit(1)
csrf_token = m.group(1)
print('Found CSRF token:', csrf_token)

# Prepare POST data
post_data = {
    'name': 'Swedish Massage DEBUG',
    'description': 'Debugging edit endpoint',
    'price': '1111.00',
    'duration': '60 min'
}
encoded = parse.urlencode(post_data).encode('utf-8')
req = request.Request(EDIT_URL, data=encoded, method='POST')
req.add_header('X-Requested-With', 'XMLHttpRequest')
req.add_header('X-CSRFToken', csrf_token)
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
# cookies are handled by opener
print('Sending POST to', EDIT_URL)
try:
    r = opener.open(req)
    body = r.read().decode('utf-8')
    print('Response code:', r.getcode())
    print('Response headers:', r.getheaders())
    print('Response body:', body)
except Exception as e:
    print('Request failed:', e)
    import traceback
    traceback.print_exc()
    # also print any cookies
    print('Cookies:', list(cj))
