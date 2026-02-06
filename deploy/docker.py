"""
Docker deployment operations.
Installs and configures Docker on Linux hosts.

On Fedora 41+ (dnf5 systems), Podman with the docker-compat shim is installed
instead of Docker CE, as Docker CE does not publish Fedora packages.
"""

from pyinfra.context import host
from pyinfra.facts.server import Which
from pyinfra.operations import files, server

from deploy.utils import get_package_manager, install_packages, log_deployment, update_package_cache


def deploy():
    """Deploy Docker (or Podman with docker-compat) on Linux hosts.

    Note: Caller is responsible for checking host.data.docker_enabled
    before calling this function.
    """
    pkg_manager = get_package_manager()
    docker_installed = host.get_fact(Which, command="docker")
    has_podman = host.get_fact(Which, command="podman")
    has_dnf5 = host.get_fact(Which, command="dnf5")

    # Determine whether this host uses Podman as the Docker runtime.
    # True if:
    #   - Already has both docker (compat shim) and podman binaries, OR
    #   - Is Fedora 41+ (dnf5 present) running dnf/yum — will install Podman
    will_use_podman = bool(
        (docker_installed and has_podman)
        or (not docker_installed and pkg_manager in ["dnf", "yum"] and has_dnf5)
    )

    if not docker_installed:
        if pkg_manager == "apt":
            # Install dependencies
            install_packages(
                [
                    "apt-transport-https",
                    "ca-certificates",
                    "curl",
                    "gnupg",
                    "lsb-release",
                ],
                pkg_manager,
            )

            # Add Docker GPG key
            server.shell(
                name="Add Docker GPG key",
                commands=[
                    "mkdir -p /etc/apt/keyrings",
                    "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | "
                    "gpg --dearmor -o /etc/apt/keyrings/docker.gpg",
                    "chmod a+r /etc/apt/keyrings/docker.gpg",
                ],
                _sudo=True,
            )

            # Add Docker repository
            server.shell(
                name="Add Docker repository",
                commands=[
                    'echo "deb [arch=$(dpkg --print-architecture) '
                    "signed-by=/etc/apt/keyrings/docker.gpg] "
                    "https://download.docker.com/linux/ubuntu "
                    '$(lsb_release -cs) stable" | '
                    "tee /etc/apt/sources.list.d/docker.list > /dev/null"
                ],
                _sudo=True,
            )

            # Update apt cache
            update_package_cache(pkg_manager)

            # Install Docker CE
            install_packages(
                [
                    "docker-ce",
                    "docker-ce-cli",
                    "containerd.io",
                    "docker-buildx-plugin",
                    "docker-compose-plugin",
                ],
                pkg_manager,
            )

        elif pkg_manager in ["dnf", "yum"] and has_dnf5:
            # Fedora 41+: Docker CE does not publish Fedora packages.
            # Install Podman with the docker-compat shim instead.
            install_packages(
                ["podman", "podman-docker"],
                pkg_manager,
            )

        elif pkg_manager in ["dnf", "yum"]:
            # Older RHEL/CentOS (dnf4/yum): install Docker CE from official repo.
            # Download the repo file directly (avoids config-manager syntax differences).
            server.shell(
                name="Add Docker repository",
                commands=[
                    "curl -fsSL https://download.docker.com/linux/centos/docker-ce.repo"
                    " -o /etc/yum.repos.d/docker-ce.repo",
                ],
                _sudo=True,
            )

            # Install Docker CE
            install_packages(
                [
                    "docker-ce",
                    "docker-ce-cli",
                    "containerd.io",
                    "docker-buildx-plugin",
                    "docker-compose-plugin",
                ],
                pkg_manager,
            )

    if will_use_podman:
        # Podman is daemonless; activate the socket unit for docker-compat API access
        server.service(
            name="Enable Podman socket",
            service="podman.socket",
            running=True,
            enabled=True,
            _sudo=True,
        )
    else:
        # Ensure Docker service is running and enabled
        server.service(
            name="Ensure Docker service is running",
            service="docker",
            running=True,
            enabled=True,
            _sudo=True,
        )

        # Configure Docker daemon (settings defined in templates/docker-daemon.json.j2)
        files.template(
            name="Configure Docker daemon",
            src="templates/docker-daemon.json.j2",
            dest="/etc/docker/daemon.json",
            mode="644",
            create_remote_dir=True,
            _sudo=True,
        )

        # Restart Docker to apply configuration
        server.service(
            name="Restart Docker service",
            service="docker",
            restarted=True,
            _sudo=True,
        )

    # Add users to docker group.
    # Docker CE creates this group automatically; on Podman hosts it may not exist.
    # Ensure the group exists before adding members.
    docker_users = host.data.get("docker_users", [])
    if docker_users:
        server.shell(
            name="Ensure docker group exists",
            commands=["getent group docker || groupadd docker"],
            _sudo=True,
        )
    for username in docker_users:
        server.shell(
            name=f"Add {username} to docker group",
            commands=[f"usermod -aG docker {username}"],
            _sudo=True,
        )

    # Log deployment
    log_deployment("Docker")
