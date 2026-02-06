# homelab-pyinfra

Infrastructure as Code for a personal homelab using [PyInfra](https://pyinfra.com/) and [pytest-testinfra](https://testinfra.readthedocs.io/).

## What It Does

Manages configuration and deployment for:
- **Linux servers** (Fedora) — packages, users, security hardening, Podman, backups
- **Synology NAS** — (planned)
- **UniFi network controller** — (planned)

## Quick Start

```bash
git clone <repo-url>
cd homelab-pyinfra
make install      # install deps + pre-commit hooks
make check        # verify SSH connectivity
make deploy-dry   # preview changes
make deploy-linux # deploy
make test         # validate infrastructure
```

See the [Quick Start Guide](docs/QUICKSTART.md) for full setup instructions.

## Project Structure

```
deploy.py              Main entry point
deploy/                Deployment modules (common, security, docker, backup, monitoring)
inventory/             Host definitions and per-host feature flags
group_data/            Shared config per host group
templates/             Jinja2 templates for config files
tests/                 pytest-testinfra post-deployment validation
```

## Documentation

| Guide | Description |
|-------|-------------|
| [Quick Start](docs/QUICKSTART.md) | Installation, first deploy, key files |
| [Deployment Options](docs/DEPLOYMENT_OPTIONS.md) | Dry-run modes, verbosity levels, targeting hosts |
| [Testing](docs/TESTING.md) | Test organization, pre/post-deployment expectations, development workflow |

## Development

```bash
make format    # auto-format (black + ruff)
make lint      # ruff + black + mypy
make test      # run infrastructure tests
make help      # list all available commands
```

## License

MIT
