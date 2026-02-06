.PHONY: help install test lint format deploy deploy-linux deploy-dry check clean

help:
	@echo "Usage:"
	@echo "  make install       Install dependencies and pre-commit hooks"
	@echo "  make test          Run all infrastructure tests"
	@echo "  make lint          Run linters (ruff, black, mypy)"
	@echo "  make format        Auto-format code (black, ruff)"
	@echo "  make deploy        Deploy to all hosts"
	@echo "  make deploy-linux  Deploy to Linux hosts"
	@echo "  make deploy-dry    Dry run (all hosts, no changes)"
	@echo "  make check         Check SSH connectivity to all hosts"
	@echo "  make clean         Remove build artifacts"
	@echo ""
	@echo "For targeting specific hosts, verbosity, diffs, etc.:"
	@echo "  pyinfra inventory/inventory.py deploy.py [options]"
	@echo "  pytest tests/ [options]"

install:
	uv sync --all-extras
	pre-commit install

test:
	pytest tests/ -v

lint:
	ruff check .
	black --check .
	mypy deploy/ --ignore-missing-imports || true

format:
	black .
	ruff check --fix .

deploy:
	pyinfra inventory/inventory.py deploy.py

deploy-linux:
	pyinfra inventory/inventory.py deploy.py --limit linux --yes

deploy-dry:
	pyinfra inventory/inventory.py deploy.py --dry -vv

check:
	@pyinfra inventory/inventory.py fact server.Hostname server.Os --yes || true

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage .mypy_cache .ruff_cache
