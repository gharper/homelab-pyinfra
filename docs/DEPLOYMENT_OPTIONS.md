# Deployment Options

## Make Targets

| Command | Description |
|---------|-------------|
| `make deploy` | Deploy to all hosts |
| `make deploy-linux` | Deploy to Linux hosts only |
| `make deploy-dry` | Dry run, all hosts (`--dry -vv`) |
| `make check` | Check SSH connectivity |

For anything else, use `pyinfra` directly.

## PyInfra Usage

```bash
# Dry run
pyinfra inventory/inventory.py deploy.py --dry -vv

# Dry run with file diffs
pyinfra inventory/inventory.py deploy.py --dry --diff -v

# Target a host group
pyinfra inventory/inventory.py deploy.py --limit linux --dry -vv

# Target a single host
pyinfra inventory/inventory.py deploy.py --limit linux1.example.com --dry -vv

# Debug mode (stack traces, internals)
pyinfra inventory/inventory.py deploy.py --debug
```

## PyInfra Flags

| Flag | Effect |
|------|--------|
| `--dry` | Preview without executing |
| `-v` | Show operation details |
| `-vv` | Show exact commands |
| `-vvv` | Show command output, return codes, timing |
| `--diff` | Show file content diffs |
| `--debug` | Stack traces, pyinfra internals |
| `--limit <group\|host>` | Target a group or single host |
| `--yes` | Skip confirmation prompts |
| `-p N` | Run on N hosts in parallel |

## Output Indicators

| Symbol | Meaning |
|--------|---------|
| `~` | Will make / made changes |
| `-` | Already in desired state |

Deployment logs are written to `/var/log/homelab/deploys.log` on each host.
