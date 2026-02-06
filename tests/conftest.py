"""
pytest-testinfra configuration and fixtures.
Uses the same SSH configuration as PyInfra inventory.

SSH Authentication:
------------------
Tests connect to hosts using the same SSH authentication as PyInfra:
- Linux hosts: Uses default SSH user (from SSH config or current user)
- Synology NAS: Uses 'geromyh' user (as specified in inventory)
- UniFi Controller: Uses 'root' user (as specified in inventory)

SSH Key Configuration:
---------------------
1. Set SSH_PRIVATE_KEY_PATH environment variable, OR
2. Configure ~/.ssh/config with Host entries, OR
3. Tests will use ~/.ssh/id_rsa by default

See docs/SSH_SETUP.md for detailed setup instructions.
"""

import os

import pytest
import testinfra


def _get_ssh_config():
    """
    Get SSH configuration matching PyInfra defaults.

    Priority:
    1. SSH_PRIVATE_KEY_PATH environment variable
    2. System SSH config (~/.ssh/config)
    3. Default key (~/.ssh/id_rsa)
    """
    ssh_key = os.environ.get("SSH_PRIVATE_KEY_PATH", "~/.ssh/id_rsa")
    return {
        "ssh_config": None,
        "ssh_identity_file": os.path.expanduser(ssh_key),
    }


def _make_host(connection_string):
    """Create a testinfra host with standard SSH config."""
    return testinfra.get_host(connection_string, **_get_ssh_config())


@pytest.fixture(scope="module")
def host(request):
    """Return a testinfra host (generic, parametrized by caller)."""
    return _make_host(f"ssh://{request.param}")


@pytest.fixture(
    scope="module",
    params=[
        "skully.mental404.com",
        "node1.mental404.com",
        "node2.mental404.com",
    ],
)
def linux_host(request):
    """Return a testinfra host for Linux servers (parametrized over all 3)."""
    return _make_host(f"ssh://{request.param}")


@pytest.fixture(scope="module")
def synology_host():
    """Return testinfra host for Synology NAS (ssh_user='geromyh')."""
    return _make_host("ssh://geromyh@synology.mental404.com")


@pytest.fixture(scope="module")
def unifi_host():
    """Return testinfra host for UniFi controller (ssh_user='root')."""
    return _make_host("ssh://root@unifi.mental404.com")


@pytest.fixture(scope="module")
def docker_host():
    """Return testinfra host for Docker-enabled server (skully)."""
    return _make_host("ssh://skully.mental404.com")
