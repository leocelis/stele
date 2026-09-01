# Stele quickstart

## Install (PyPI)

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install stele-core stele-mcp
```

## Install (from git)

```bash
git clone https://github.com/leocelis/stele.git
cd stele
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e packages/stele-core -e packages/stele-mcp
```

## Library (60 seconds)

```bash
python examples/quickstart_core.py
```

## CLI

```bash
stele init ./.stele-store --store-id demo --now 2026-09-01T12:00:00Z
stele init ./.stele-store --store-id demo --demo --now 2026-09-01T12:00:00Z
stele doctor ./.stele-store --now 2026-09-01T12:00:00Z
```

## MCP stdio (35 tools — default)

```bash
export STELE_STORE=./.stele-store
stele-mcp
```

Full research library (~2000 tools): `stele-mcp-full`.

## Hosted (core)

```json
{
  "mcpServers": {
    "stele": {
      "url": "https://stele.leocelis.com/core/sse",
      "headers": { "Authorization": "Bearer YOUR_KEY" }
    }
  }
}
```

BYO deploy: `deploy/README.md`.
