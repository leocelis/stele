#!/usr/bin/env bash
# deploy/build.sh — Stele MCP Server build for DigitalOcean App Platform.
#
# DO build_command:  bash deploy/build.sh
# Run command:       deploy/Procfile  →  python deploy/wsgi.py --port 8080
#
# Install MySQL extras at BUILD time even when STELE_STORE_DSN is RUN_TIME-only
# (otherwise the container boots green from the buildpack then crashes on first
# MySQL import).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo "============================================================"
echo "  Stele MCP Server — build"
echo "  Repo root: $REPO_ROOT"
echo "============================================================"

echo ""
echo "[build:1/3] Installing packages (core[mysql] + mcp[hosted], mcp<2)..."
python -m pip install --upgrade pip --quiet
pip install -e "packages/stele-core[mysql]" -e "packages/stele-mcp[hosted]" --quiet

echo ""
echo "[build:2/3] Verifying stele packages..."
python -c "from stele_core import __version__; print(f'  stele-core {__version__}  OK')"
python - <<'PY'
import importlib.metadata as md
ver = md.version("mcp")
maj = int(ver.split(".", 1)[0])
if maj >= 2:
    raise SystemExit(f"mcp major {maj} is unsupported; pin mcp>=1.0,<2")
print(f"  mcp {ver}  OK (<2)")
PY

echo ""
echo "[build:3/3] Verifying MCP server, auth, and MySQL backend imports..."
python - <<'PY'
from stele_mcp.server import create_app, store_mode
from stele_mcp.auth import SteleAuthMiddleware, generate_api_key
import pymysql  # noqa: F401
from stele_core.mysql_store import MySQLSteleStore  # noqa: F401

app = create_app()
_ = generate_api_key("build")
print("  stele_mcp.server.create_app  OK")
print("  stele_mcp.auth               OK")
print(f"  pymysql {pymysql.__version__}          OK")
print(f"  store_mode (build env): {store_mode()}")
PY

echo ""
echo "============================================================"
echo "  Build complete."
echo "============================================================"
