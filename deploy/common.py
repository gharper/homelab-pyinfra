"""
Common deployment operations for all Linux hosts.
Base configuration applied to all servers.
Supports multiple package managers: apt, dnf, yum.
"""

from pyinfra.context import host
from pyinfra.operations import files, server

from deploy.utils import (
    get_package_manager,
    install_auto_updates,
    install_packages,
    log_deployment,
    normalize_groups,
    update_package_cache,
    upgrade_all_packages,
)


def deploy():
    """Deploy common configuration to Linux hosts."""

    # Detect package manager
    pkg_manager = get_package_manager()
    print(f"Detected package manager: {pkg_manager}")

    # Update package cache
    update_package_cache(pkg_manager)

    # Upgrade all packages
    upgrade_all_packages(pkg_manager)

    # Install common packages
    packages = host.data.get("packages", [])
    install_packages(packages, pkg_manager)

    # Configure timezone
    timezone = host.data.get("timezone", "UTC")
    server.shell(
        name=f"Set timezone to {timezone}",
        commands=[
            f"timedatectl set-timezone {timezone}",
        ],
        _sudo=True,
    )

    # Enable automatic security updates
    install_auto_updates(pkg_manager)

    # Create deploy user if defined
    users = host.data.get("users", {})
    for username, user_config in users.items():
        # Translate group names for the target distro (e.g. sudo -> wheel on RHEL)
        raw_groups = user_config.get("groups", [])
        resolved_groups = normalize_groups(raw_groups, pkg_manager)

        server.user(
            name=f"Create user {username}",
            user=username,
            shell=user_config.get("shell", "/bin/bash"),
            home=user_config.get("home", f"/home/{username}"),
            groups=resolved_groups,
            _sudo=True,
        )

        # Create .ssh directory
        files.directory(
            name=f"Create .ssh directory for {username}",
            path=f"{user_config.get('home', f'/home/{username}')}/.ssh",
            user=username,
            group=username,
            mode="700",
            _sudo=True,
        )

        # Create authorized_keys file if it doesn't exist
        files.file(
            name=f"Create authorized_keys for {username}",
            path=f"{user_config.get('home', f'/home/{username}')}/.ssh/authorized_keys",
            user=username,
            group=username,
            mode="600",
            touch=True,
            _sudo=True,
        )

    # Create deployment tracking directory
    files.directory(
        name="Create homelab tracking directory",
        path="/etc/homelab",
        mode="755",
        _sudo=True,
    )

    # Write deployment marker
    server.shell(
        name="Write deployment marker",
        commands=[
            'echo "$(date -Iseconds)" > /etc/homelab/.deployed',
            f'echo "{host.name}" > /etc/homelab/hostname',
        ],
        _sudo=True,
    )

    # Log deployment
    log_deployment("Common")
