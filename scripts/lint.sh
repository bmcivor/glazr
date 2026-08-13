#!/usr/bin/env bash
set -uo pipefail

# Checks only — nothing here rewrites source. Fixing is the developer's job.
#
# Every check runs even when an earlier one fails, so one pass shows all the
# work. The script still exits non-zero if any of them failed.
#
# Unlike test.sh there is no teardown: linting needs no database, so a run
# must not disturb a stack you already have up.

status=0

compose() {
    docker compose -f docker-compose.yml "$@"
}

run_backend() {
    compose run --rm --no-deps --build backend-test sh -c '
        rc=0
        echo "--- ruff format --check ---"
        ruff format --check . || rc=1
        echo "--- ruff check ---"
        ruff check . || rc=1
        echo "--- mypy ---"
        mypy . || rc=1
        exit $rc
    ' || status=1
}

run_frontend() {
    compose run --rm --no-deps --build frontend-test sh -c '
        rc=0
        echo "--- eslint ---"
        npm run lint || rc=1
        echo "--- prettier --check ---"
        npx prettier --check . || rc=1
        exit $rc
    ' || status=1
}

case "${1:-all}" in
    backend)
        run_backend
        ;;
    frontend)
        run_frontend
        ;;
    all)
        run_backend
        run_frontend
        ;;
    *)
        echo "usage: ${0##*/} [backend | frontend]" >&2
        exit 2
        ;;
esac

exit "$status"
