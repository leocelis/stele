# Releasing Stele

1. Bump `version` in `packages/stele-core/pyproject.toml` and `packages/stele-mcp/pyproject.toml` (keep equal).
2. `python scripts/sync_doc_versions.py`
3. Slice user-facing notes into `CHANGELOG.md` (core + MCP core only).
4. `make check && make verify-oss`
5. `cd packages/stele-core && python -m build`
6. `cd packages/stele-mcp && python -m build`
7. Publish wheels to PyPI (`twine upload`).
8. `git tag vX.Y.Z && git push origin vX.Y.Z`
9. Create GitHub release with wheel artifacts.
10. Hosted deploy: push to `main` (App Platform auto-build) or manual deploy.
11. Smoke: `curl -s https://YOUR_HOST/health`
