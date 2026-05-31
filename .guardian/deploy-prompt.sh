#!/usr/bin/env bash
# Deploy the worksite prompt from the guardian or camp dwelling.
DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$DIR/.guardian/CLAUDE.md" ]; then
  cp "$DIR/.guardian/CLAUDE.md" "$DIR/CLAUDE.md"
fi
