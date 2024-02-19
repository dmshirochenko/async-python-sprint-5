#!/bin/sh

set -e

docker-compose up -d --build --renew-anon-volumes
docker logs -f test-auth-service
exitcode="$(docker inspect test-auth-service --format={{.State.ExitCode}})"
docker-compose down --remove-orphans --volumes
exit "$exitcode"