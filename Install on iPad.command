#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
exec python3 scripts/ipad-install-assistant.py
