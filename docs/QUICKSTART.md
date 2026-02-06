# Quick Start

## Prerequisites

- Python 3.14+ and [uv](https://docs.astral.sh/uv/)
- SSH key-based access to your hosts (passwordless, with sudo on Linux hosts)

## Install and Deploy

```bash
git clone <repo-url>
cd homelab-pyinfra
make install      # deps + pre-commit hooks
make check        # verify SSH connectivity
make deploy-dry   # preview changes
make deploy-linux # deploy
make test         # validate infrastructure
```

## What Gets Deployed

Each Linux host receives:

| Module | What it does |
|--------|-------------|
| **common** | Package updates, timezone, deploy user (`service-deploy`), auto-updates |
| **security** | firewalld, fail2ban, hardened sshd_config, filesystem lockdown |
| **docker** | Podman + docker-compat shim, podman.socket, docker group |
| **backup** | rsync, borgbackup, backup script, cron schedule |

Modules are controlled by feature flags in `inventory/inventory.py` (`docker_enabled`, `backup_enabled`, `monitoring_enabled`).

## Key Files

| File | Purpose |
|------|---------|
| `deploy.py` | Entry point, orchestrates modules per host |
| `deploy/utils.py` | Cross-distro helpers (package manager detection, install, groups) |
| `inventory/inventory.py` | Host definitions and per-host feature flags |
| `group_data/linux.py` | Shared config for all Linux hosts |
| `tests/conftest.py` | SSH fixtures for testinfra |

## Further Reading

- [Deployment Options](DEPLOYMENT_OPTIONS.md) -- verbosity levels, dry-run modes, pyinfra flags
- [Testing](TESTING.md) -- test organization and development workflow
