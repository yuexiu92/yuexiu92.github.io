#!/usr/bin/env sh

cd -- "$(dirname -- "$0")" || exit 1

available_port() (
  port="$1"
  while lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; do
    port=$((port + 1))
  done
  printf '%s' "$port"
)

preview_port=$(available_port 4000)
reload_port=$(available_port 35729)

exec /opt/homebrew/bin/bundle exec jekyll serve --livereload \
  --port "$preview_port" --livereload-port "$reload_port" "$@"
