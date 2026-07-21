import urllib.parse
import urllib.request

url = 'http://127.0.0.1:8000/register/'
payload = {
    'username': 'auto_user_001',
    'email': 'auto_user_001@example.com',
    'password': 'TestPass123',
    'confirm-password': 'TestPass123'
}

data = urllib.parse.urlencode(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, method='POST')
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        status = resp.getcode()
        text = resp.read(8192).decode('utf-8', errors='replace')
        print('Status code:', status)
        start = text.find('Registration')
        if start == -1:
            start = 0
        print(text[start:start+800])
except Exception as e:
    print('Request error:', e)
