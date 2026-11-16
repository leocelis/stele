# Host apps: one Stele server, a store per tenant

A **host app** is an application that serves many of its own customers
(tenants) and wants each one to have its own Stele store. The host and the
server share one secret. From it the host derives a key per tenant; the server
checks the key, opens that tenant's store on first use, and limits the key to
five tools. Nothing is provisioned per tenant, and neither side stores the
keys. Specification: [`TECH_SPEC.md` §12](../TECH_SPEC.md).

## Server configuration

| Variable | Meaning | Default |
|---|---|---|
| `STELE_TENANT_KEY_SECRET` | Shared secret. Not set → tenant keys are off | not set |
| `STELE_TENANT_KEY_VERSIONS` | Comma-separated key versions the server accepts | `v1` |
| `STELE_REVOKED_TENANTS` | Comma-separated tenants whose keys are refused | empty |
| `STELE_STORE_DSN` | MySQL store. **Required**: tenant keys are refused on the file store | not set |
| `STELE_TENANT_STORE_CACHE` | How many tenant stores stay open (least recently used closed first) | `64` |

Keys in `STELE_API_KEYS` keep working exactly as before and keep the process
store (`STELE_STORE_ID`). The server rejects every request only when both
`STELE_API_KEYS` and `STELE_TENANT_KEY_SECRET` are empty.

## Deriving a key

```
key = "stl_" + tenant + "_" + base64url_nopad( HMAC-SHA256(SECRET, "stl:" + VERSION + ":" + tenant) )
```

- `tenant` matches `^[a-z0-9][a-z0-9-]{0,55}$` (lowercase, at most 56 characters).
- The MAC part is always 43 characters and may itself contain `_`. To read the
  tenant back, take the text between `stl_` and the last 44 characters; never
  split on `_`.

```python
import base64, hashlib, hmac

def stele_tenant_key(secret: str, tenant: str, version: str = "v1") -> str:
    mac = hmac.new(secret.encode(), f"stl:{version}:{tenant}".encode(), hashlib.sha256).digest()
    return f"stl_{tenant}_" + base64.urlsafe_b64encode(mac).rstrip(b"=").decode()
```

Test vector (check your implementation against it):

| Secret | Version | Tenant | Key |
|---|---|---|---|
| `test-secret-do-not-use` | `v1` | `acme` | `stl_acme_0p59V8dV554TE_3lmyXhrfNERv2GlWUS1dYdLIYS9fg` |

**Rotation.** Add the new version to `STELE_TENANT_KEY_VERSIONS` (for example
`v1,v2`), move the host to `v2`, then drop `v1`. **Revocation.** Add the tenant
to `STELE_REVOKED_TENANTS`.

## What a tenant key can do

- **Path.** Only the core surface: `/core/sse` and `/core/mcp`. The same key on
  `/sse`, `/messages` or `/mcp` is refused.
- **Store.** Its own store `t-<tenant>`, with its own scratch folder. Two tenants
  never find, list or delete each other's entries.
- **Tools.** `tools/list` returns five tools and only these can be called:

| Tool | Use |
|---|---|
| `stele_add` | Write an entry into quarantine |
| `stele_promote` | Promote an entry with evidence from someone other than the writer |
| `stele_search` | Search promoted entries |
| `stele_delete` | Erase one entry (`entry_id`) or a subject (`subject_id`) |
| `stele_list` | Page through the store: `id`, `layer`, `title`, `state`, `written_at` |

`stele_list(state, limit, cursor)`: `state` is `"quarantine"`, `"promoted"` or
omitted (all live entries); `limit` defaults to 50, at most 200; pass the
returned `next_cursor` as `cursor` for the next page. It returns

```json
{"entries": [{"id": "...", "layer": "...", "title": "...", "state": "...", "written_at": "..."}],
 "next_cursor": "..." }
```

`next_cursor` is `null` on the last page.

- **Sessions.** An MCP session belongs to the key that opened it. Open one
  session per tenant; a message on that session signed with another tenant's
  key, or an operator key, is refused.

## What the host must do itself

- **Fill the entry's provenance, scope and temporal block.** Let a model write
  only `layer`, `title` and `body`. Who wrote it, where, for which subject and
  from when it holds is the host's knowledge; the temporal block is required by
  the schema.
- **Build the promotion evidence.** Promotion needs evidence from someone other
  than the writer, and `human_signoff` is accepted with any issuer string. So
  the host, never the model, writes the evidence: an independent judge's
  verdict on that entry's text, or the signed-in person's own approval.
- **Decide where the store may be used.** The server knows tenants, not the
  host's private spaces inside a tenant. Use `scope` and `subject_id` for that,
  and filter on the host side.
- **Keep the secret on the server side of the host.** Anyone holding it can
  derive every tenant's key.
