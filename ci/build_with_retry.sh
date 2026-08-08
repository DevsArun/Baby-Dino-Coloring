#!/usr/bin/env bash
# Runs a command with up to 3 attempts + backoff. Protects CI against
# transient Maven Central / Gradle plugin portal rate limits (HTTP 429).
# Usage: bash ci/build_with_retry.sh flutter build apk --debug
set -u

MAX_ATTEMPTS=3
for attempt in $(seq 1 $MAX_ATTEMPTS); do
  echo "==> Attempt $attempt/$MAX_ATTEMPTS: $*"
  if "$@"; then
    exit 0
  fi
  if [ "$attempt" -lt "$MAX_ATTEMPTS" ]; then
    wait_s=$((attempt * 45))
    echo "::warning::Attempt $attempt failed (possibly a network flake / HTTP 429). Retrying in ${wait_s}s..."
    sleep "$wait_s"
  fi
done
echo "::error::Command failed after $MAX_ATTEMPTS attempts: $*"
exit 1
