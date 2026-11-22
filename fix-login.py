import json, os, shutil
from pathlib import Path
p = Path('ent-core.json')
config = json.loads(p.read_text())
host = os.environ['CODESPACE_NAME'] + '-8090.' + os.environ['GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN']
auth = next(s['config'] for s in config['services'] if s['name'] == 'org.entcore~auth')
auth['authenticationServer']['loginCallback'] = 'https://' + host + '/userbook/mon-compte'
backup = p.with_suffix('.json.before-login-fix')
if not backup.exists(): shutil.copyfile(p,backup)
p.write_text(json.dumps(config, indent=2) + chr(10))
print('LOGIN_CALLBACK_UPDATED')
