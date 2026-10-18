#!/usr/bin/env sh

cd -- "$(dirname -- "$0")" || exit 1

exec /opt/homebrew/bin/bundle exec jekyll serve --livereload "$@"
