import http.client, http.cookies, json, os, time, urllib.parse
host = os.environ['CODESPACE_NAME'] + '-8090.' + os.environ['GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN']
base = 'https://' + host
headers = {'Host': 'localhost:8090', 'X-Forwarded-Host': host, 'X-Forwarded-Proto': 'https', 'Origin': base, 'Referer': base + '/auth/login'}
conn = http.client.HTTPConnection('127.0.0.1',8090, timeout=12)
for _ in range(20):
    conn.request('GET','/auth/login',headers=headers)
    r = conn.getresponse(); r.read()
    if r.status == 200: break
    time.sleep(3)
else: raise SystemExit('Login page unavailable')
body = urllib.parse.urlencode({'email':'ent.admin','password':json.load(open('secrets.json'))['admin']})
headers['Content-Type']='application/x-www-form-urlencoded'
conn.request('POST','/auth/login',body,headers)
r = conn.getresponse()
loc=urllib.parse.urlparse(r.getheader('Location',''))
cookies=http.cookies.SimpleCookie()
for k,v in r.getheaders():
    if k.lower()=='set-cookie': cookies.load(v)
r.read()
print('REDIRECT_OK', r.status==302 and loc.hostname==host and loc.path=='/userbook/mon-compte', loc.hostname, loc.path)
print('SESSION_OK','oneSessionId' in cookies)
headers['Cookie']='; '.join(k+'='+v.coded_value for k,v in cookies.items())
headers['Host']=host
conn.request('GET','/userbook/mon-compte',headers=headers)
r=conn.getresponse()
print('ACCOUNT_HTTP',r.status)
