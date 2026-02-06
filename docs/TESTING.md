# Testing

Tests run against live infrastructure via SSH using pytest-testinfra. They are not unit tests.

## Test Files

| File | Validates | Before Deploy | After Deploy |
|------|-----------|---------------|--------------|
| `test_common.py` | SSH connectivity, DNS, system basics | Pass | Pass |
| `test_linux_hosts.py` | Packages, users, security config | Fail | Pass |
| `test_docker.py` | Podman/Docker, compose, docker group | Fail | Pass |
| `test_synology.py` | Synology accessibility | Pass | Pass |
| `test_unifi.py` | UniFi accessibility | Pass | Pass |

Pre-deployment failures in `test_linux_hosts.py` and `test_docker.py` are expected -- those tests verify deployment results.

## Running Tests

```bash
# All tests
make test

# Specific file
pytest tests/test_common.py -v

# Filter by host or class
pytest tests/test_common.py::TestLinuxCommon -v -k "linux1"

# Docker tests only
pytest -m docker -v

# With coverage
pytest tests/ --cov=deploy --cov-report=html --cov-report=term
```

## Test Development

1. Write a test for the expected state
2. Run it (should fail)
3. Implement the deploy operation
4. `make deploy-dry` then `make deploy-linux`
5. Run test again (should pass)

## CI

The CI pipeline (`.github/workflows/ci.yml`) runs linting, syntax validation, and security scanning. It does not run testinfra tests -- those require SSH access to live hosts.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Permission denied (publickey)` | Verify SSH key-based auth is configured for the host |
| `Connection refused` | Verify host is reachable |
| `Package not installed` / `File not found` | Run deployment first |
| `Wrong user` | Check `ssh_user` in `inventory/inventory.py` |
