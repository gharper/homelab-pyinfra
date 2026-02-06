"""
Security hardening deployment operations.
Configures SSH, firewall, and fail2ban.
"""

from io import StringIO

from pyinfra.context import host
from pyinfra.operations import files, server

from deploy.utils import get_package_manager, install_packages, log_deployment


def deploy():
    """Deploy security hardening configuration."""

    pkg_manager = get_package_manager()

    # Install appropriate firewall package and fail2ban
    if pkg_manager == "apt":
        install_packages(["ufw", "fail2ban"], pkg_manager)
    else:
        # RHEL-family: ufw is not available; firewalld is the standard firewall
        install_packages(["firewalld", "fail2ban"], pkg_manager)

    # Configure firewall if enabled
    if host.data.get("ufw_enabled", False):
        ssh_port = host.data.get("ssh_port", 22)

        if pkg_manager == "apt":
            # UFW (Debian/Ubuntu)
            server.shell(
                name="Configure UFW default policies",
                commands=[
                    "ufw --force default deny incoming",
                    "ufw --force default allow outgoing",
                ],
                _sudo=True,
            )
            server.shell(
                name=f"Allow SSH on port {ssh_port}",
                commands=[f"ufw allow {ssh_port}/tcp"],
                _sudo=True,
            )
            server.shell(
                name="Enable UFW",
                commands=["ufw --force enable"],
                _sudo=True,
            )
        else:
            # firewalld (RHEL/Fedora/CentOS)
            server.service(
                name="Enable firewalld",
                service="firewalld",
                running=True,
                enabled=True,
                _sudo=True,
            )
            server.shell(
                name=f"Allow SSH on port {ssh_port} via firewalld",
                commands=[
                    f"firewall-cmd --permanent --add-port={ssh_port}/tcp",
                    "firewall-cmd --reload",
                ],
                _sudo=True,
            )

    # Configure fail2ban if enabled
    if host.data.get("fail2ban_enabled", False):
        # Create custom fail2ban configuration
        jail_local = """[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
"""
        files.put(
            name="Configure fail2ban",
            src=StringIO(jail_local),
            dest="/etc/fail2ban/jail.local",
            mode="644",
            add_deploy_dir=False,
            _sudo=True,
        )

        # Enable and start fail2ban
        server.service(
            name="Enable and start fail2ban",
            service="fail2ban",
            running=True,
            enabled=True,
            _sudo=True,
        )

    # Deploy hardened SSH configuration
    # sftp-server lives at different paths on Debian vs RHEL-family
    sftp_server_path = (
        "/usr/lib/openssh/sftp-server"
        if pkg_manager == "apt"
        else "/usr/libexec/openssh/sftp-server"
    )
    files.template(
        name="Deploy hardened sshd_config",
        src="templates/sshd_config.j2",
        dest="/etc/ssh/sshd_config",
        mode="644",
        user="root",
        group="root",
        sftp_server_path=sftp_server_path,
        _sudo=True,
    )

    # Restart SSH to apply configuration
    server.service(
        name="Restart SSH service",
        service="sshd",
        restarted=True,
        _sudo=True,
    )

    # Secure shared memory
    server.shell(
        name="Secure shared memory",
        commands=[
            "grep -q 'tmpfs /run/shm' /etc/fstab || "
            "echo 'tmpfs /run/shm tmpfs defaults,noexec,nosuid 0 0' >> /etc/fstab"
        ],
        _sudo=True,
    )

    # Disable unused filesystems
    modules_to_disable = ["cramfs", "freevxfs", "jffs2", "hfs", "hfsplus", "udf"]
    for module in modules_to_disable:
        server.shell(
            name=f"Disable {module} filesystem",
            commands=[f"echo 'install {module} /bin/true' > /etc/modprobe.d/{module}.conf"],
            _sudo=True,
        )

    # Log deployment
    log_deployment("Security")
