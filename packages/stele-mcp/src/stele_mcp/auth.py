"""Bearer auth + in-process rate limit for hosted Stele MCP (HTTP only).

Reads API keys from STELE_API_KEYS (comma-separated). Stdio transport never
uses this middleware (process isolation).

Derived tenant keys (TECH_SPEC §12.1): when STELE_TENANT_KEY_SECRET is set, a
bearer key that is not in STELE_API_KEYS is accepted if it has the shape

    stl_<tenant>_<base64url_nopad(HMAC-SHA256(SECRET, "stl:" + VERSION + ":" + tenant))>

for a version in STELE_TENANT_KEY_VERSIONS (default ``v1``) and the tenant is
not listed in STELE_REVOKED_TENANTS. Tenant keys are accepted only under
``/core`` and only when the MySQL store is configured (STELE_STORE_DSN).

Fail-closed: when both STELE_API_KEYS and STELE_TENANT_KEY_SECRET are empty,
every non-exempt request is rejected unless STELE_AUTH_DISABLED=true (local
tests only — never on hosted).

The resolved caller is written to the ASGI scope under ``stele.identity`` so
that each MCP message reads the identity of its own HTTP request (see
``identity_from_scope``), never a value captured when the session started.

Key generation:
    python -c "import secrets; print('stl_deploy_' + secrets.token_urlsafe(24))"
"""

from __future__ import annotations

import base64
import collections
import contextvars
import hashlib
import hmac
import logging
import os
import re
import secrets
import threading
import time
from dataclasses import dataclass
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

current_key_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "stele_current_key_id", default="local"
)
current_key_sha: contextvars.ContextVar[str] = contextvars.ContextVar(
    "stele_current_key_sha", default=""
)

_log = logging.getLogger("stele_mcp.auth")

_raw = os.environ.get("STELE_API_KEYS", "")
VALID_API_KEYS: set[str] = {k.strip() for k in _raw.split(",") if k.strip()}
AUTH_DISABLED: bool = os.environ.get("STELE_AUTH_DISABLED", "false").lower() == "true"
_EXEMPT_PATHS: frozenset[str] = frozenset({"/health", "/healthz"})

TENANT_KEY_SECRET: str = os.environ.get("STELE_TENANT_KEY_SECRET", "")
TENANT_KEY_VERSIONS: tuple[str, ...] = tuple(
    v.strip()
    for v in os.environ.get("STELE_TENANT_KEY_VERSIONS", "v1").split(",")
    if v.strip()
)
REVOKED_TENANTS: set[str] = {
    t.strip() for t in os.environ.get("STELE_REVOKED_TENANTS", "").split(",") if t.strip()
}

TENANT_KEY_PREFIX = "stl_"
_TENANT_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,55}$")
# "_" + 43-character base64url MAC (32 bytes, no padding).
_MAC_TAIL_LEN = 44

SCOPE_IDENTITY_KEY = "stele.identity"
CORE_PATH_PREFIX = "/core"

RATE_LIMIT_PER_MINUTE: float = float(os.environ.get("STELE_RATE_LIMIT_PER_MINUTE", "120"))
RATE_LIMIT_BURST: float = float(os.environ.get("STELE_RATE_LIMIT_BURST", "20"))
_MAX_TRACKED_RATE_LIMIT_KEYS = 1000


class _TokenBucket:
    __slots__ = ("last_refill", "tokens")

    def __init__(self, capacity: float, now: float) -> None:
        self.tokens = capacity
        self.last_refill = now


class RateLimiter:
    """In-process per-key token bucket. Correct for instance_count=1 only."""

    def __init__(
        self,
        rate_per_minute: float = RATE_LIMIT_PER_MINUTE,
        burst: float = RATE_LIMIT_BURST,
        max_tracked_keys: int = _MAX_TRACKED_RATE_LIMIT_KEYS,
    ) -> None:
        self._rate_per_second = rate_per_minute / 60.0
        self._burst = burst
        self._max_tracked = max_tracked_keys
        self._buckets: collections.OrderedDict[str, _TokenBucket] = collections.OrderedDict()
        self._lock = threading.Lock()

    def allow(self, key: str) -> tuple[bool, float]:
        now = time.monotonic()
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                bucket = _TokenBucket(self._burst, now)
                self._buckets[key] = bucket
                if len(self._buckets) > self._max_tracked:
                    self._buckets.popitem(last=False)
            else:
                self._buckets.move_to_end(key)

            elapsed = now - bucket.last_refill
            bucket.tokens = min(self._burst, bucket.tokens + elapsed * self._rate_per_second)
            bucket.last_refill = now

            if bucket.tokens >= 1.0:
                bucket.tokens -= 1.0
                return True, 0.0

            deficit = 1.0 - bucket.tokens
            retry_after = deficit / self._rate_per_second if self._rate_per_second > 0 else 60.0
            return False, retry_after


_rate_limiter = RateLimiter()


@dataclass(frozen=True)
class Identity:
    """Who a request runs as: an operator key, a derived tenant key, or local."""

    kind: str  # "operator" | "tenant" | "local"
    key_id: str
    tenant: str | None = None

    @property
    def principal(self) -> str:
        if self.kind == "tenant":
            return f"tenant:{self.tenant}"
        return f"{self.kind}:{self.key_id}"

    @property
    def is_tenant(self) -> bool:
        return self.kind == "tenant"


LOCAL_IDENTITY = Identity(kind="local", key_id="local")


def is_valid_tenant_name(tenant: str) -> bool:
    return bool(_TENANT_RE.fullmatch(tenant))


def derive_tenant_key(secret: str, tenant: str, version: str = "v1") -> str:
    """Return the tenant key for (secret, version, tenant) — TECH_SPEC §12.1."""
    if not is_valid_tenant_name(tenant):
        raise ValueError(f"invalid tenant name: {tenant!r}")
    mac = hmac.new(
        secret.encode("utf-8"),
        f"stl:{version}:{tenant}".encode(),
        hashlib.sha256,
    ).digest()
    encoded = base64.urlsafe_b64encode(mac).rstrip(b"=").decode("ascii")
    return f"{TENANT_KEY_PREFIX}{tenant}_{encoded}"


def tenant_from_key(candidate: str) -> str | None:
    """Return the tenant a derived key belongs to, or None when it does not verify.

    The tenant is the text between the prefix and the last 44 characters —
    never found by splitting on "_" (the MAC itself may contain "_").
    """
    if not TENANT_KEY_SECRET:
        return None
    if not candidate.startswith(TENANT_KEY_PREFIX):
        return None
    if len(candidate) <= len(TENANT_KEY_PREFIX) + _MAC_TAIL_LEN:
        return None
    if candidate[-_MAC_TAIL_LEN] != "_":
        return None
    tenant = candidate[len(TENANT_KEY_PREFIX) : -_MAC_TAIL_LEN]
    if not is_valid_tenant_name(tenant):
        return None
    matched = False
    for version in TENANT_KEY_VERSIONS:
        expected = derive_tenant_key(TENANT_KEY_SECRET, tenant, version)
        if hmac.compare_digest(candidate.encode("utf-8"), expected.encode("utf-8")):
            matched = True
    if not matched:
        return None
    if tenant in REVOKED_TENANTS:
        return None
    return tenant


def _is_core_path(path: str) -> bool:
    return path == CORE_PATH_PREFIX or path.startswith(CORE_PATH_PREFIX + "/")


def _tenant_store_available() -> bool:
    return bool(os.environ.get("STELE_STORE_DSN"))


def identity_from_scope(scope: Any) -> Identity | None:
    """Read the identity the auth middleware wrote into an ASGI scope."""
    if not isinstance(scope, dict):
        return None
    ident = scope.get(SCOPE_IDENTITY_KEY)
    return ident if isinstance(ident, Identity) else None


class SteleAuthMiddleware:
    """ASGI middleware: Bearer tokens for all non-exempt HTTP paths."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path: str = scope.get("path", "")

        if path in _EXEMPT_PATHS or AUTH_DISABLED:
            await self.app(scope, receive, send)
            return

        err, identity, key_sha = _authenticate(scope)
        if err is not None or identity is None:
            response = JSONResponse(err or {"error": "Unauthorized"}, status_code=401)
            await response(scope, receive, send)
            return
        key_id = identity.key_id

        allowed, retry_after = _rate_limiter.allow(key_id)
        if not allowed:
            _log.warning(
                "AUTH  rate_limited  key=%s  path=%s  retry_after=%.1fs", key_id, path, retry_after
            )
            response = JSONResponse(
                {"error": "Rate limit exceeded", "retry_after_seconds": round(retry_after, 1)},
                status_code=429,
                headers={
                    "Retry-After": str(int(retry_after) + 1),
                    "RateLimit-Policy": f'"default";q={int(RATE_LIMIT_PER_MINUTE)};w=60',
                    "RateLimit": '"default";r=0',
                },
            )
            await response(scope, receive, send)
            return

        _log.info("AUTH  ok  key=%s  kind=%s  path=%s", key_id, identity.kind, path)
        # Per-request identity on the scope: the MCP transports build each
        # message's Request from this scope, so tools read the caller of the
        # message itself (TECH_SPEC §12.1 "identity per message").
        scope[SCOPE_IDENTITY_KEY] = identity
        token = current_key_id.set(key_id)
        sha_token = current_key_sha.set(key_sha)
        try:
            await self.app(scope, receive, send)
        finally:
            current_key_sha.reset(sha_token)
            current_key_id.reset(token)


def _authenticate(scope: Scope) -> tuple[dict[str, Any] | None, Identity | None, str]:
    path = scope.get("path", "")

    if not VALID_API_KEYS and not TENANT_KEY_SECRET and not AUTH_DISABLED:
        _log.warning("AUTH  no_keys_configured  path=%s  — rejecting (fail-closed)", path)
        return {
            "error": (
                "Server has no API keys configured (STELE_API_KEYS and "
                "STELE_TENANT_KEY_SECRET are unset). Refusing all requests. Set "
                "STELE_API_KEYS, or STELE_AUTH_DISABLED=true for local dev only."
            )
        }, None, ""

    headers: dict[bytes, bytes] = dict(scope.get("headers", []))
    raw_auth: str = headers.get(b"authorization", b"").decode("utf-8", errors="replace")

    if not raw_auth:
        _log.warning("AUTH  missing_header  path=%s", path)
        return {"error": "Missing Authorization header"}, None, ""

    if not raw_auth.startswith("Bearer "):
        _log.warning("AUTH  bad_format  path=%s", path)
        return {"error": "Invalid Authorization header. Expected: Bearer <token>"}, None, ""

    api_key = raw_auth[7:].strip()

    if not api_key:
        _log.warning("AUTH  empty_key  path=%s", path)
        return {"error": "Empty API key"}, None, ""

    if AUTH_DISABLED and not VALID_API_KEYS:
        _log.warning(
            "AUTH  no_keys_configured  path=%s  — allowed (STELE_AUTH_DISABLED=true)", path
        )
        return None, Identity(kind="local", key_id="unconfigured"), ""

    key_sha = hashlib.sha256(api_key.encode()).hexdigest()

    if VALID_API_KEYS and _key_matches(api_key):
        return None, Identity(kind="operator", key_id=_key_id(api_key)), key_sha

    tenant = tenant_from_key(api_key)
    if tenant is None:
        _log.warning("AUTH  invalid_key  key_prefix=%s  path=%s", api_key[:8], path)
        return {"error": "Invalid API key"}, None, ""

    if not _is_core_path(path):
        _log.warning("AUTH  tenant_off_core  tenant=%s  path=%s", tenant, path)
        return {"error": "Tenant keys are accepted only under /core"}, None, ""

    if not _tenant_store_available():
        _log.warning("AUTH  tenant_needs_mysql  tenant=%s  path=%s", tenant, path)
        return {
            "error": "Tenant keys need the MySQL store (STELE_STORE_DSN); refused on a file store"
        }, None, ""

    return None, Identity(kind="tenant", key_id=_key_id(api_key), tenant=tenant), key_sha


def _extract_and_validate(scope: Scope) -> tuple[dict[str, Any] | None, str, str]:
    err, identity, key_sha = _authenticate(scope)
    if err is not None or identity is None:
        return err or {"error": "Unauthorized"}, "", ""
    return None, identity.key_id, key_sha


def _key_matches(candidate: str) -> bool:
    matched = False
    for valid_key in VALID_API_KEYS:
        if hmac.compare_digest(candidate, valid_key):
            matched = True
    return matched


def _key_id(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()[:8]


async def validate_api_key(request: Request) -> tuple[JSONResponse | None, str | None]:
    if AUTH_DISABLED:
        return None, None

    path = request.url.path
    if path in _EXEMPT_PATHS:
        return None, None

    err, key_id, _sha = _extract_and_validate({"headers": list(request.headers.raw), "path": path})
    if err is not None:
        return JSONResponse(err, status_code=401), None
    return None, key_id


def generate_api_key(username: str = "user") -> str:
    token = secrets.token_urlsafe(24)
    return f"stl_{username}_{token}"


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()
