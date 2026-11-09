#!/bin/bash
set -euo pipefail

export PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
export TZ=Asia/Shanghai
export GIT_TERMINAL_PROMPT=0
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

task_state="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
task_python="$task_state/venv/bin/python"
task_checkout="$(mktemp -d /tmp/xiuyue-citations.XXXXXX)"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "$*"
}

finish() {
  task_status=$?
  if [ "$task_status" -ne 0 ]; then
    log "Citation update failed (exit $task_status); inspect this log for the error."
  fi
  rm -rf -- "$task_checkout"
  exit "$task_status"
}
trap finish EXIT

log 'Starting Google Scholar citation update.'
git clone --quiet --depth 1 --single-branch --branch main \
  https://github.com/yuexiu92/yuexiu92.github.io.git "$task_checkout"
cd "$task_checkout"
"$task_python" -m unittest discover -s .github/scripts -p 'test_*.py'
"$task_python" .github/scripts/update_scholar_citations.py

if git diff --quiet -- _config.yml _includes/about/publications.md; then
  log 'Citation data unchanged; no commit or deployment needed.'
  exit 0
fi

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add -- _config.yml _includes/about/publications.md
git commit -m 'Refresh Google Scholar citation counts'
git push origin HEAD:main
log 'Citation changes pushed to main; GitHub Actions will build and deploy the homepage.'
