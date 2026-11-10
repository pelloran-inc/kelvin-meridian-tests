#!/usr/bin/env bash
# The CI gates without GitHub Actions: runs exactly `.github/workflows/ci.yml`'s two jobs, `python` and `secret-scan`,
# on this host. From a full clone:
#
#     bash ci/gates.sh [all|python|secret-scan]        (default: all)
#
# It installs nothing. Every missing prerequisite is named, and the run stops before any gate:
#   - python3, 3.10 or newer
#   - for secret-scan: gitleaks 8.30.1 on PATH, and a full (non-shallow) clone
#
# Exit: 0 every gate passed · 1 a gate failed · 2 a prerequisite is missing, or the usage is wrong.
set -uo pipefail

python_job() {
  step 'python3 -c "import sys; assert sys.version_info >= (3, 10), sys.version"' &&
  step 'python3 -m compileall -q -x "(/data/|/\.git/)" .' &&
  step 'python3 tests/keys_needed.py > /dev/null' &&
  step 'python3 ci/check_repo.py'
}

secret_scan_job() {
  step 'gitleaks git --redact --no-banner --exit-code 1 .'
}

step() {
  echo "## $1"
  eval "$1"
  local rc=$?
  echo "exit=$rc"
  return $rc
}

cd "$(dirname "$0")/.." || exit 2
selected=${1:-all}
case "$selected" in
  all) selected="python secret-scan" ;;
  python | secret-scan) ;;
  *) echo "usage: bash ci/gates.sh [all|python|secret-scan]" >&2; exit 2 ;;
esac
command -v python3 >/dev/null || { echo "missing: python3" >&2; exit 2; }
case " $selected " in *" secret-scan "*)
  command -v gitleaks >/dev/null || { echo "missing: gitleaks 8.30.1 on PATH" >&2; exit 2; }
  [ "$(git rev-parse --is-shallow-repository 2>/dev/null)" = "false" ] || { echo "secret-scan needs a full clone" >&2; exit 2; } ;;
esac

failed=0
for job in $selected; do
  echo "# job: $job"
  case "$job" in
    python) python_job || failed=1 ;;
    secret-scan) secret_scan_job || failed=1 ;;
  esac
done
[ "$failed" -eq 0 ] && echo "ALL GATES PASSED" || echo "A GATE FAILED"
exit "$failed"
