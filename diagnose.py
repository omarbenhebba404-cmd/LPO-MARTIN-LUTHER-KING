import json,sys
for line in sys.stdin:
    try:
        l=json.loads(line[line.index('{'):])
    except (ValueError,TypeError):
        continue
    m=l.get('message','')
    if isinstance(m,str) and any(x in m.lower() for x in ('deploy','appregistry','app-registry','error loading','failed','super admin')):
        print(l.get('level',''),m.splitlines()[0][:135])
