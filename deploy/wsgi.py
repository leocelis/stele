"""
Production entry point for the Stele MCP Server on DigitalOcean App Platform.

Serves both transports, full and core-only, from a single process:
  /health       — unauthenticated health check (DO load balancer)
  /sse          — SSE transport, full tool surface (Cursor and legacy MCP clients)
  /mcp          — Streamable HTTP transport, full tool surface (modern clients)
  /core/sse     — SSE transport, governed-ledger tools only (see
                  stele_mcp.server._CORE_TOOL_NAMES)
  /core/mcp     — Streamable HTTP transport, governed-ledger tools only

The core-only routes exist because the full surface carries ~2000 PEFT/agent-
pattern research-reproduction tools alongside the ~34-tool governed ledger
(ROADMAP.md Phase 9+ / CHANGELOG.md) — a client that only wants the ledger
(stele_add/promote/search/doctor/...) should point at /core/sse or /core/mcp
instead of /sse or /mcp.

Auth:  Bearer token via SteleAuthMiddleware (reads STELE_API_KEYS env var).
       /health is always exempt.

Usage:
    python deploy/wsgi.py --port 8080

Secrets (STELE_API_KEYS, STELE_STORE_DSN, STELE_MYSQL_SSL_CA_B64) must be set
in the platform console — never committed.
"""

from __future__ import annotations

import argparse
import os
import sys
from contextlib import asynccontextmanager

_here = os.path.dirname(os.path.abspath(__file__))
_repo = os.path.dirname(_here)
for _pkg in (
    os.path.join(_repo, "packages", "stele-core", "src"),
    os.path.join(_repo, "packages", "stele-mcp", "src"),
    _repo,
):
    if _pkg not in sys.path:
        sys.path.insert(0, _pkg)

os.environ.setdefault("STELE_ENV", "production")

from stele_core import __version__  # noqa: E402
from stele_mcp.auth import SteleAuthMiddleware  # noqa: E402
from stele_mcp.server import create_app, create_core_app, store_mode  # noqa: E402

import uvicorn  # noqa: E402
from starlette.applications import Starlette  # noqa: E402
from starlette.responses import JSONResponse  # noqa: E402
from starlette.routing import Mount, Route  # noqa: E402


def _patch_server_session_auto_init() -> None:
    """Allow Cursor CallMcpTool to skip MCP initialize (hosted HTTP clients)."""
    try:
        from mcp.server.session import InitializationState, ServerSession
        from mcp.types import InitializeRequest as _InitReq

        _orig = ServerSession._received_request

        async def _auto_init(self, responder):  # type: ignore[override]
            if (
                self._initialization_state == InitializationState.NotInitialized
                and not isinstance(responder.request.root, _InitReq)
            ):
                self._initialization_state = InitializationState.Initialized
            await _orig(self, responder)

        ServerSession._received_request = _auto_init  # type: ignore[method-assign]
        print("[Stele MCP] Applied CallMcpTool auto-init patch.", flush=True)
    except Exception as exc:
        print(f"[Stele MCP] Warning: auto-init patch failed: {exc}", flush=True)


_patch_server_session_auto_init()


def build_app():
    """
    Build the combined Starlette app:
      /health          — unauthenticated
      /sse + /messages — FastMCP SSE transport, full tool surface
      /mcp             — FastMCP Streamable HTTP transport, full tool surface
      /core/sse        — FastMCP SSE transport, governed-ledger tools only
      /core/mcp        — FastMCP Streamable HTTP transport, governed-ledger tools only
    Wrapped with SteleAuthMiddleware (/health exempt).
    """
    fastmcp = create_app()
    sse_starlette = fastmcp.sse_app()
    http_starlette = fastmcp.streamable_http_app()

    core_fastmcp = create_core_app()
    core_sse_starlette = core_fastmcp.sse_app(mount_path="/core")
    core_http_starlette = core_fastmcp.streamable_http_app()

    async def health(request):
        return JSONResponse(
            {
                "status": "healthy",
                "server": "stele",
                "version": __version__,
                "transports": [
                    "streamable-http",
                    "sse",
                    "core-streamable-http",
                    "core-sse",
                ],
                "store_mode": store_mode(),
                "resumable": False,
                "tool_counts": {
                    "full": len(fastmcp._tool_manager.list_tools()),
                    "core": len(core_fastmcp._tool_manager.list_tools()),
                },
                "recommended_surface": "core",
                "docs_url": "https://github.com/leocelis/stele/blob/main/docs/QUICKSTART.md",
            }
        )

    def _strip_core_prefix(scope):
        # FastMCP's sse_app(mount_path=...) only prefixes the *advertised*
        # POST endpoint it hands back to clients in the SSE "endpoint" event
        # (via _normalize_path) — the GET route stays registered at the bare
        # settings.sse_path ("/sse") and the message Mount stays at the bare
        # settings.message_path ("/messages/"), regardless of mount_path. So
        # core_sse_starlette/core_http_starlette only ever match unprefixed
        # paths; every /core/* request must be stripped before dispatch, or
        # it 404s even with valid auth (confirmed live on /core/sse).
        path = scope.get("path", "/")
        scope = dict(scope)
        scope["path"] = path[len("/core") :] or "/"
        if isinstance(scope.get("raw_path"), (bytes, bytearray)):
            scope["raw_path"] = scope["path"].encode("utf-8")
        return scope

    class _Dispatcher:
        async def __call__(self, scope, receive, send):
            path = scope.get("path", "/")
            if path == "/core/mcp" or path.startswith("/core/mcp/"):
                await core_http_starlette(_strip_core_prefix(scope), receive, send)
            elif (
                path == "/core/sse"
                or path.startswith("/core/sse")
                or path.startswith("/core/messages")
            ):
                await core_sse_starlette(_strip_core_prefix(scope), receive, send)
            elif path == "/mcp" or path.startswith("/mcp/"):
                await http_starlette(scope, receive, send)
            else:
                await sse_starlette(scope, receive, send)

    @asynccontextmanager
    async def _lifespan(app):
        async with http_starlette.router.lifespan_context(app):
            async with core_http_starlette.router.lifespan_context(app):
                yield

    inner_app = Starlette(
        lifespan=_lifespan,
        routes=[
            Route("/health", health, methods=["GET"]),
            Route("/healthz", health, methods=["GET"]),
            Mount("/", app=_Dispatcher()),
        ],
    )
    return SteleAuthMiddleware(inner_app)


app = build_app()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stele MCP Server (production)")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    print(f"[Stele MCP] Starting production server on {args.host}:{args.port}", flush=True)
    print(f"[Stele MCP] Version: {__version__}", flush=True)
    print(f"[Stele MCP] Store mode: {store_mode()}", flush=True)
    print(
        f"[Stele MCP] Auth: "
        f"{'DISABLED' if os.environ.get('STELE_AUTH_DISABLED') else 'enabled'}",
        flush=True,
    )

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        timeout_keep_alive=600,
        timeout_graceful_shutdown=30,
    )
