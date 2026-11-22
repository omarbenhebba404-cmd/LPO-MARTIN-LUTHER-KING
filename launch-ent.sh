#!/usr/bin/env bash
set -euo pipefail
cd /workspaces/open-ent/springboard
umask 077
while [ ! -s ../build.exit ]; do sleep 3; done
[ "$(cat ../build.exit)" = 0 ]
test -s docker-compose.yml && test -s ent-core.json
bash build.sh buildFront > ../front.log 2>&1
docker compose -f docker-compose.yml config --format json | python3 ../configure-runtime.py
docker compose -p openent-ng -f compose.ent.json up -d --wait --wait-timeout 300 traefik vertx elasticsearch pdf localstack
curl -sS --max-time 10 -o /dev/null -w 'ENT_HTTP=%{http_code}\n' http://127.0.0.1:8090/auth/login
