"""
Utility functions for deployment operations.
Provides package manager detection and cross-distribution support.
"""

from pyinfra.context import host
from pyinfra.facts.server import LinuxDistribution, Which
from pyinfra.operations import apt, dnf, server, yum


def get_package_manager():
    """
    Detect and return the appropriate package manager for the host.

    Returns:
        str: 'apt', 'dnf', or 'yum'

    Examples:
        >>> pkg_mgr = get_package_manager()
        >>> if pkg_mgr == 'apt':
        ...     install_with_apt()
    """
    # Check which package managers are available
    has_apt = host.get_fact(Which, command="apt-get")
    has_dnf = host.get_fact(Which, command="dnf")
    has_yum = host.get_fact(Which, command="yum")

    # Determine package manager based on availability
    if has_apt:
        return "apt"
    elif has_dnf:
        return "dnf"
    elif has_yum:
        return "yum"
    else:
        # Fallback: try to detect from distribution
        distro = host.get_fact(LinuxDistribution)
        if distro:
            # LinuxDistribution returns a dict, get the name
            distro_name = distro.get("name", "") if isinstance(distro, dict) else str(distro)
            if distro_name:
                distro_lower = distro_name.lower()
                if any(x in distro_lower for x in ["debian", "ubuntu", "mint"]):
                    return "apt"
                elif any(x in distro_lower for x in ["fedora", "rhel", "centos", "rocky", "alma"]):
                    # In this branch none of apt/dnf/yum were found via Which,
                    # so default to yum (more likely to exist on older systems).
                    return "yum"

        # Default fallback
        return "apt"


def update_package_cache(pkg_manager=None):
    """
    Update package cache/metadata.

    Args:
        pkg_manager: Package manager to use. If None, auto-detect.
    """
    if pkg_manager is None:
        pkg_manager = get_package_manager()

    if pkg_manager == "apt":
        apt.update(
            name="Update apt cache",
            cache_time=3600,
            _sudo=True,
        )
    elif pkg_manager == "dnf":
        server.shell(
            name="Update dnf cache",
            commands=["dnf makecache"],
            _sudo=True,
        )
    elif pkg_manager == "yum":
        server.shell(
            name="Update yum cache",
            commands=["yum makecache"],
            _sudo=True,
        )


def upgrade_all_packages(pkg_manager=None):
    """
    Upgrade all installed packages.

    Args:
        pkg_manager: Package manager to use. If None, auto-detect.
    """
    if pkg_manager is None:
        pkg_manager = get_package_manager()

    if pkg_manager == "apt":
        apt.upgrade(
            name="Upgrade all packages",
            auto_remove=True,
            _sudo=True,
        )
    elif pkg_manager == "dnf":
        server.shell(
            name="Upgrade all packages with dnf",
            commands=["dnf upgrade -y"],
            _sudo=True,
        )
    elif pkg_manager == "yum":
        server.shell(
            name="Upgrade all packages with yum",
            commands=["yum update -y"],
            _sudo=True,
        )


def install_packages(packages, pkg_manager=None, update=False):
    """
    Install packages using the appropriate package manager.

    Args:
        packages: List of package names to install
        pkg_manager: Package manager to use. If None, auto-detect.
        update: Whether to update cache before installing

    Examples:
        >>> install_packages(["vim", "htop", "curl"])
        >>> install_packages(["nginx"], update=True)
    """
    if not packages:
        return

    if pkg_manager is None:
        pkg_manager = get_package_manager()

    if pkg_manager == "apt":
        apt.packages(
            name="Install packages",
            packages=packages,
            update=update,
            _sudo=True,
        )
    elif pkg_manager == "dnf":
        dnf.packages(
            name="Install packages",
            packages=packages,
            _sudo=True,
        )
    elif pkg_manager == "yum":
        yum.packages(
            name="Install packages",
            packages=packages,
            _sudo=True,
        )


def install_auto_updates(pkg_manager=None):
    """
    Install and enable automatic security updates.

    - Debian/Ubuntu: unattended-upgrades
    - Fedora/RHEL 8+: dnf-automatic
    - RHEL 7/CentOS 7: yum-cron

    Args:
        pkg_manager: Package manager to use. If None, auto-detect.
    """
    if pkg_manager is None:
        pkg_manager = get_package_manager()

    if pkg_manager == "apt":
        apt.packages(
            name="Install unattended-upgrades",
            packages=["unattended-upgrades", "apt-listchanges"],
            _sudo=True,
        )
    elif pkg_manager == "dnf":
        # Fedora 41+ replaced dnf-automatic with dnf5-plugin-automatic.
        has_dnf5 = host.get_fact(Which, command="dnf5")
        pkg = "dnf5-plugin-automatic" if has_dnf5 else "dnf-automatic"
        timer = "dnf5-automatic.timer" if has_dnf5 else "dnf-automatic.timer"
        dnf.packages(
            name=f"Install {pkg}",
            packages=[pkg],
            _sudo=True,
        )
        server.service(
            name=f"Enable {timer}",
            service=timer,
            enabled=True,
            running=True,
            _sudo=True,
        )
    elif pkg_manager == "yum":
        yum.packages(
            name="Install yum-cron",
            packages=["yum-cron"],
            _sudo=True,
        )
        server.service(
            name="Enable yum-cron",
            service="yum-cron",
            enabled=True,
            running=True,
            _sudo=True,
        )


def normalize_groups(groups, pkg_manager=None):
    """
    Translate group names to be distro-appropriate.

    Replaces 'sudo' with 'wheel' on RHEL-family systems and vice versa,
    so group_data can use a single canonical name.

    Args:
        groups: List of group names.
        pkg_manager: Package manager to use for detection. If None, auto-detect.

    Returns:
        List of group names with the correct sudo/wheel group for the host.
    """
    if pkg_manager is None:
        pkg_manager = get_package_manager()

    # Debian/Ubuntu use 'sudo', RHEL-family uses 'wheel'
    sudo_group = "sudo" if pkg_manager == "apt" else "wheel"
    return [sudo_group if g in ("sudo", "wheel") else g for g in groups]


def log_deployment(module_name):
    """
    Log a deployment step to /var/log/homelab/deploys.log with a timestamp.

    Args:
        module_name: Name of the module that completed deployment (e.g. "Common", "Docker").
    """
    server.shell(
        name=f"Log {module_name} deployment",
        commands=[
            "mkdir -p /var/log/homelab",
            f'echo "$(date -Iseconds): {module_name} deployment completed"'
            " >> /var/log/homelab/deploys.log",
        ],
        _sudo=True,
    )
