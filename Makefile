.PHONY: install test lint type check demo proof clean

PY := .venv/bin

install:
	python3.11 -m venv .venv
	$(PY)/pip install -q -U pip
	$(PY)/pip install -q -r requirements-dev.txt
	$(PY)/pip install -q -e packages/stele-core -e packages/stele-mcp

test:
	$(PY)/pytest -q

lint:
	$(PY)/ruff check packages/ examples/

type:
	$(PY)/mypy packages/stele-core/src/stele_core packages/stele-mcp/src/stele_mcp

check: lint type test

demo:
	$(PY)/python examples/lifecycle_demo.py

proof:
	$(PY)/python examples/proof_run.py

verify-oss:
	bash scripts/verify_oss_public.sh

sync-docs:
	$(PY)/python scripts/sync_doc_versions.py
	$(PY)/python scripts/gen_mcp_core_tools_md.py

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} +
