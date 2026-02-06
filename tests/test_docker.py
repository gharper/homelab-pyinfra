"""
Tests for Docker deployment.
Supports both Docker CE and Podman with docker-compat shim.
"""

import pytest


def _is_podman(docker_host):
    """Return True if the docker binary is actually Podman."""
    result = docker_host.run("docker --version")
    return "podman" in result.stdout.lower()


@pytest.mark.docker
def test_docker_installed(docker_host):
    """Verify Docker (or Podman docker-compat) is installed."""
    result = docker_host.run("which docker")
    assert result.rc == 0


@pytest.mark.docker
def test_docker_service_running(docker_host):
    """Verify Docker service is running, or Podman socket is active."""
    if _is_podman(docker_host):
        # Podman is daemonless; check that the socket unit is active
        result = docker_host.run("systemctl is-active podman.socket")
        assert result.rc == 0, "podman.socket is not active"
    else:
        docker = docker_host.service("docker")
        assert docker.is_running
        assert docker.is_enabled


@pytest.mark.docker
def test_docker_socket_exists(docker_host):
    """Verify Docker socket exists (Docker CE only; skipped for Podman)."""
    if _is_podman(docker_host):
        # Podman is daemonless; socket path varies and is not a reliable check.
        # Connectivity is verified by test_docker_info and test_docker_can_pull_images.
        pytest.skip("Host uses Podman; socket path check not applicable")
    sock = docker_host.file("/var/run/docker.sock")
    assert sock.exists
    assert sock.is_socket


@pytest.mark.docker
def test_docker_compose_installed(docker_host):
    """Verify Docker Compose is installed."""
    result = docker_host.run("docker compose version")
    assert result.rc == 0


@pytest.mark.docker
def test_docker_version(docker_host):
    """Verify docker/podman version is retrievable."""
    result = docker_host.run("docker --version")
    assert result.rc == 0
    # Accept Docker CE or Podman with docker-compat shim
    assert "Docker version" in result.stdout or "podman version" in result.stdout


@pytest.mark.docker
def test_deploy_user_in_docker_group(docker_host):
    """Verify service-deploy user is in docker group."""
    deploy_user = docker_host.user("service-deploy")
    assert "docker" in deploy_user.groups


@pytest.mark.docker
def test_docker_daemon_json_exists(docker_host):
    """Verify Docker daemon configuration exists (Docker CE only; skipped for Podman)."""
    if _is_podman(docker_host):
        pytest.skip("Host uses Podman; daemon.json is not applicable")
    daemon_config = docker_host.file("/etc/docker/daemon.json")
    assert daemon_config.exists
    assert daemon_config.mode == 0o644


@pytest.mark.docker
def test_docker_info(docker_host):
    """Verify docker info command works."""
    result = docker_host.run("docker info")
    assert result.rc == 0


@pytest.mark.docker
def test_docker_can_pull_images(docker_host):
    """Verify Docker can pull a simple test image."""
    # Pull alpine image (very small)
    result = docker_host.run("docker pull alpine:latest")
    assert result.rc == 0

    # Verify image exists
    result = docker_host.run("docker images alpine")
    assert result.rc == 0
    assert "alpine" in result.stdout

    # Clean up
    docker_host.run("docker rmi alpine:latest")
