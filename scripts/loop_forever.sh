#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

RUNTIME_DIR="$REPO_ROOT/.rebar/runtime"
LOCK_DIR="$RUNTIME_DIR/loop.lock.d"
mkdir -p "$RUNTIME_DIR"

acquire_lock() {
  if mkdir "$LOCK_DIR" 2>/dev/null; then
    printf '%s\n' "$$" > "$LOCK_DIR/pid"
    return 0
  fi

  if [[ -f "$LOCK_DIR/pid" ]]; then
    local holder_pid
    holder_pid="$(cat "$LOCK_DIR/pid" 2>/dev/null || true)"
    if [[ -n "$holder_pid" ]] && ! kill -0 "$holder_pid" 2>/dev/null; then
      rm -rf "$LOCK_DIR"
      mkdir "$LOCK_DIR"
      printf '%s\n' "$$" > "$LOCK_DIR/pid"
      return 0
    fi
  fi

  echo "Loop already running: $LOCK_DIR" >&2
  exit 1
}

cleanup() {
  rm -rf "$LOCK_DIR"
}

acquire_lock
trap cleanup EXIT INT TERM

force_supervisor=1
cycle_args=("$@")

while true; do
  set +e
  if [[ "$force_supervisor" -eq 1 ]]; then
    python3 scripts/rebar_ops.py cycle --force-supervisor "${cycle_args[@]}"
    force_supervisor=0
  else
    python3 scripts/rebar_ops.py cycle "${cycle_args[@]}"
  fi
  exit_code=$?
  set -e

  sleep_seconds="$(python3 scripts/rebar_ops.py sleep-seconds --exit-code "$exit_code")"
  sleep "$sleep_seconds"
done
