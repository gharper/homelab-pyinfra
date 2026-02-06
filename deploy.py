"""
Main deployment entry point for homelab infrastructure.

Usage:
    pyinfra inventory/inventory.py deploy.py
    pyinfra inventory/inventory.py deploy.py --limit linux
    pyinfra inventory/inventory.py deploy.py --dry
"""

from pyinfra.context import host

from deploy import backup, common, docker, monitoring, security


def main():
    """Main deployment orchestration."""

    print(f"\n=== Deploying to {host.name} ===\n")

    # Deploy to Linux hosts
    if "linux" in host.groups:
        print("Deploying common configuration...")
        common.deploy()

        print("Deploying security hardening...")
        security.deploy()

        # Deploy monitoring if enabled
        if host.data.get("monitoring_enabled", False):
            print("Deploying monitoring...")
            monitoring.deploy()

        # Deploy Docker if enabled for this host
        if host.data.get("docker_enabled", False):
            print("Deploying Docker...")
            docker.deploy()

        # Deploy backup if enabled
        if host.data.get("backup_enabled", False):
            print("Deploying backup configuration...")
            backup.deploy()

    # Deploy to Synology NAS
    elif "synology" in host.groups:
        print("Synology-specific deployment...")
        # NOTE: monitoring.deploy() and backup.deploy() use standard Linux
        # package managers (apt/dnf/yum) which are not available on Synology DSM.
        # TODO: Implement Synology-specific monitoring and backup modules.

    # Deploy to UniFi controller
    elif "unifi" in host.groups:
        print("UniFi-specific deployment...")
        # NOTE: monitoring.deploy() and backup.deploy() use standard Linux
        # package managers (apt/dnf/yum) which are not available on UniFi OS.
        # TODO: Implement UniFi-specific monitoring and backup modules.

    print(f"\n=== Deployment to {host.name} completed ===\n")


# Call main at module level (pyinfra loads this as a module, not __main__)
main()
