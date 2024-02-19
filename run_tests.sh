#!/bin/sh

set -e

docker-compose up -d --build --renew-anon-volumes
docker logs -f test-auth-service &
docker logs -f test-file_storage_service &
exitcode_auth="$(docker inspect test-auth-service --format={{.State.ExitCode}})"
exitcode_file_storage="$(docker inspect test-file_storage_service --format={{.State.ExitCode}})"
docker-compose down --remove-orphans --volumes

# Check exit codes and exit with non-zero if any tests failed
if [ "$exitcode_auth" -ne 0 ] || [ "$exitcode_file_storage" -ne 0 ]; then
  echo "One or more tests failed"
  # Exit with a code from one of the failed services or a custom one
  exit 1
fi

# If all tests passed
echo "All tests passed"
exit 0