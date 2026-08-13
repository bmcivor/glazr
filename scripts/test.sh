#!/usr/bin/env bash
set -euo pipefail

compose() {
    docker compose -f docker-compose.yml "$@"
}

cleanup() {
    compose down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup

run_backend() {
    compose run --rm --build backend-test pytest -vvv "$@"
}

run_frontend() {
    compose run --rm --build frontend-test
}

case "${1:-all}" in
    backend)
        shift
        run_backend "$@"
        ;;
    frontend)
        run_frontend
        ;;
    all)
        run_backend
        run_frontend
        ;;
    *)
        echo "usage: ${0##*/} [backend [pytest args...] | frontend]" >&2
        exit 2
        ;;
esac
