# Tenancy

Stele hosted MCP maps **one API key → one store tenant** (operator configuration).

- `store_id` inside entries scopes lessons (`project:…`, `subject:…`).
- API keys must not be shared across unrelated teams.
- Multi-tenant SaaS requires separate keys or separate deployments per tenant.

BYO deploy: one deployment per tenant is the simplest isolation model.
