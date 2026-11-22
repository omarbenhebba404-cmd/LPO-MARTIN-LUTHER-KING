import json, sys, zipfile
from pathlib import Path
s=json.loads(Path('../secrets.json').read_text())
c=json.load(sys.stdin)
a=c['services']
for n in ('gradle','node','vertx-cli'):
    a.pop(n,None)
for v in a.values():
    v.pop('ports',None)
a['traefik']['ports']=['127.0.0.1:8090:8090']
a['vertx']['environment']['ENABLE_REMOTE_DEBUG']='false'
a['vertx']['environment']['VERTX_CONF_PATH']='/opt/conf/entcore.json'
a['elasticsearch']['environment']['node.store.allow_mmap']='false'
a['postgres']['environment']['POSTGRES_PASSWORD']=s['postgres']
for n,target in {'postgres':'/var/lib/postgresql/data','mongo':'/data/db','neo4j':'/data','elasticsearch':'/usr/share/opensearch/data','redis':'/data','nats':'/data','zookeeper':'/data'}.items():
    volume='ent_'+n
    c.setdefault('volumes',{})[volume]={}
    mounts=a[n].setdefault('volumes',[])
    mounts[:]=[x for x in mounts if x['target']!=target]
    mounts.append({'type':'volume','source':volume,'target':target})
c['volumes'].pop('pgdata',None)
storage=Path('../storage').resolve()
storage.mkdir(exist_ok=True)
mounts=a['vertx'].setdefault('volumes',[])
mounts[:]=[x for x in mounts if not x['target'].startswith('/srv/storage')]
mounts.append({'type':'bind','source':str(storage),'target':'/srv/storage'})
p=Path('docker-entrypoint-initdb.d/init.sql')
p.write_text(p.read_text().replace('We_1234',s['postgres']))
p.chmod(0o644)
p=Path('ent-core.json')
e=json.loads(p.read_text().replace('We_1234',s['postgres']))
for service in e['services']:
    if service.get('name','').startswith('org.entcore~cas'):
        config=service['config']
        config.setdefault('publicConf',{})['skip']=False
        for registered in config.get('services',[]):
            registered['patterns']=[]
p.write_text(json.dumps(e,indent=2))
p.chmod(0o600)
def admin(data):
    v=json.loads(data)
    v.update(login='ent.admin',password=s['admin'])
    return json.dumps(v).encode()
count=0
for m in Path('mods').glob('*directory*'):
    for p in (m.rglob('*') if m.is_dir() else [m]):
        if p.name=='super-admin.json':
            p.write_bytes(admin(p.read_bytes()))
            count+=1
        elif p.suffix=='.jar' and zipfile.is_zipfile(p):
            tmp=p.with_suffix('.tmp')
            with zipfile.ZipFile(p) as src:
                if 'super-admin.json' not in src.namelist():
                    continue
                with zipfile.ZipFile(tmp,'w') as dst:
                    for entry in src.infolist():
                        data=src.read(entry)
                        dst.writestr(entry,admin(data) if entry.filename=='super-admin.json' else data)
            tmp.chmod(p.stat().st_mode & 0o777)
            tmp.replace(p)
            count+=1
if not count:
    raise SystemExit('Aucune configuration de super administrateur trouvée')
Path('compose.ent.json').write_text(json.dumps(c,indent=2))
print('RUNTIME_OK')
