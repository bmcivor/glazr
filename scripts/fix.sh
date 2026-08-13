#!/usr/bin/env bash
set -uo pipefail

# The write counterpart to lint.sh — everything here modifies source. Runs
# against `backend` and `frontend` rather than the `*-test` services, because
# those mount your source in the base compose file, so changes reach disk.
#
# Every step runs even when an earlier one fails, and the script exits non-zero
# if any of them did.
#
# No teardown, for the same reason as lint.sh: a run must not disturb a stack
# you already have up.

status=0

compose() {
    docker compose "$@"
}

run_backend() {
    compose run --rm --no-deps --build --user "$(id -u):$(id -g)" backend-test sh -c '
        rc=0
        echo "--- ruff format ---"
        ruff format . || rc=1
        echo "--- ruff check --fix ---"
        ruff check --fix . || rc=1
        exit $rc
    ' || status=1
}

run_frontend() {
    compose run --rm --no-deps --build --user "$(id -u):$(id -g)" frontend-test sh -c '
        rc=0
        echo "--- prettier --write ---"
        npx prettier --write . || rc=1
        echo "--- eslint --fix ---"
        npx eslint --fix . || rc=1
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
