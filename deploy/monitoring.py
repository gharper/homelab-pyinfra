"""
Monitoring deployment operations.
Installs standard monitoring and diagnostic tools.
"""

from pyinfra.operations import server

from deploy.utils import install_packages, log_deployment


def deploy():
    """Deploy monitoring tools on hosts.

    Note: Caller is responsible for checking host.data.monitoring_enabled
    before calling this function.
    """
    # Install monitoring and diagnostic tools
    install_packages(
        [
            "sysstat",
            "iotop",
            "htop",
        ]
    )

    # Enable sysstat data collection
    server.service(
        name="Enable sysstat service",
        service="sysstat",
        running=True,
        enabled=True,
        _sudo=True,
    )

    # Log deployment
    log_deployment("Monitoring")
