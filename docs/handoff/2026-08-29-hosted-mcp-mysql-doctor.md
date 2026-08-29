# Handoff — Stele hosted MCP + MySQL doctor fix

**Date:** 2026-08-29  
**Tip:** v18.16.1 (`a4358dc` on `main`, GitHub `leocelis/stele`, **PRIVATE**)  
**Status:** green — hosted live, doctor fixed, fully validated  
**Audience:** next operator/agent continuing Stele hosted MCP

Session distillate only. Product contract = `stele_system_intent.yaml` + PRD + TECH_SPEC. Operator plan (DO IDs, firewall sacred) = `limitless/docs/ventures/stele/STELE_HOSTED_MCP_TECH_SPEC.md`.

---

## What shipped this session

1. **Hosted MCP** on DO App Platform (Horizon-shaped shell): Bearer auth, SSE + streamable HTTP, MySQL durable SoT on `ada-cluster` DB `stele`.
2. **Custom domain:** `https://stele.leocelis.com` (fallback ingress: `https://stele-mcp-2vlrd.ondigitalocean.app`).
3. **Client docs:** `docs/integrations/{README,CURSOR,CLAUDE_CODE,CLAUDE_DESKTOP}.md` + `docs/cursor-rules/stele-hosted-mcp.mdc`.
4. **Doctor bugfix (v18.16.1):** `stele_doctor` crashed on MySQL with `'MySQLSteleStore' object has no attribute 'manifest_path'`. Integrity checks are now backend-agnostic (`verify_store` / `journal_digest` use `store_id` + `iter_*`, not file paths).
5. **Regression:** `packages/stele-core/tests/test_store_backend_parity.py` (CI, no DSN required). MySQL parity test also asserts doctor when DSN+CA set.

---

## Live tip (verified 2026-08-29)

| Gate | Result |
|---|---|
| Git tip | `a4358dc` — `__version__` 18.16.1; prior `eb11c40` = doctor fix |
| DO app | `stele-mcp` ACTIVE on `a4358dc` |
| `GET /health` | `healthy`, `store_mode=mysql`, `version=18.16.1` |
| MCP tools listed | **2003** |
| `stele_doctor` (hosted) | `ok=true`, no `manifest_path` error |
| Critical smoke (12 tools) | all pass |
| Full hosted sweep | **2003/2003** — zero `AttributeError` / `manifest_path` / HTTP 5xx |
| DB firewall Trusted Sources | **empty** (must stay empty unless Leo approves a full allowlist) |

---

## How clients connect

```json
{
  "mcpServers": {
    "stele": {
      "url": "https://stele.leocelis.com/sse",
      "headers": { "Authorization": "Bearer YOUR_KEY_HERE" }
    }
  }
}
```

- Hosted = Bearer required (except `/health`).
- Local stdio `stele-mcp` = no Bearer.
- Leo’s personal key was issued and merged into DO `STELE_API_KEYS` (also under `/tmp/stele-hosted-secrets/` on the desk — **never commit**).
- Cursor: `~/.cursor/mcp.json` · Claude Code: `claude mcp add …` · see integration docs.

Stele is **explicit memory I/O** — do not call on every chat turn.

---

## Sacred / do not repeat

- **Rule #31:** Never `doctl databases firewalls append` when Trusted Sources is empty. First rule flips DO to allowlist-only and killed ADA/etc. (2026-08-29). Leave firewalls alone unless Leo signs a **full** allowlist plan.
- Never commit live keys, DSN passwords, or PEMs. `deploy/do_app_spec.yaml` = SECRET **names** only.
- Do not put Limitless / Cosmic Rewind / portfolio / CE / ADA narrative in the Stele tree.
- Tip scrubbed of sibling-product **Horizon** name; older **commit messages/blobs** still contain it — rewrite+force-push only if making the repo public.

---

## Repo layout (hosted)

| Path | Role |
|---|---|
| `deploy/wsgi.py` | HTTP shell + `/health` |
| `deploy/build.sh` | App Platform build |
| `deploy/do_app_spec.yaml` | Spec template (secret names) |
| `packages/stele-mcp/src/stele_mcp/auth.py` | Bearer middleware |
| `packages/stele-core/src/stele_core/mysql_store.py` | MySQL SoT (`backend="mysql"`) |
| `packages/stele-core/src/stele_core/integrity.py` | Backend-agnostic verify/doctor path |

---

## Still open (not blocking)

- History rewrite to purge “Horizon twin” from old commits (only before public).
- `examples/proof_run.py` still uses actor string `ivd-oracle` (rename to generic if scrubbing sibling names).
- File-only `snapshot` correctly refuses MySQL (`SchemaError`); no MySQL cold-copy yet.
- Health/version already match 18.16.1 after `a4358dc`.

---

## Next operator: resume checklist

1. Confirm `curl -sS https://stele.leocelis.com/health` → `18.16.1` + `mysql`.
2. Call `stele_doctor` via hosted MCP with Bearer — expect `ok: true`.
3. Do **not** touch `ada-cluster` firewalls.
4. New work: start from tip `main`; run `make test` (parity tests must stay green).
5. Operator secrets/DSN/CA: desk `/tmp/stele-hosted-secrets/` or DO console — never git.

**Stop here.** Hosted Stele MCP is usable; doctor bug closed.
