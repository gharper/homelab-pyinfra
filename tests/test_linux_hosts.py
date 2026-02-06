"""
Tests for Linux hosts.
"""


def test_required_packages_installed(linux_host):
    """Verify all required tools are available on PATH."""
    # Use `which` rather than package-name checks so the test works across
    # distros where package names differ (e.g. vim vs vim-enhanced on RHEL).
    required_commands = ["vim", "htop", "curl", "wget", "git"]
    for cmd in required_commands:
        result = linux_host.run(f"which {cmd}")
        assert result.rc == 0, f"{cmd} is not available on PATH"


def test_timezone_configured(linux_host):
    """Verify timezone is configured."""
    result = linux_host.run("timedatectl show -p Timezone --value")
    assert result.rc == 0
    assert len(result.stdout.strip()) > 0


def test_deploy_user_exists(linux_host):
    """Verify service-deploy user exists with proper configuration."""
    deploy_user = linux_host.user("service-deploy")
    assert deploy_user.exists
    assert deploy_user.shell == "/bin/bash"


def test_deploy_ssh_directory(linux_host):
    """Verify service-deploy user has .ssh directory."""
    ssh_dir = linux_host.file("/home/service-deploy/.ssh")
    assert ssh_dir.exists
    assert ssh_dir.is_directory
    assert ssh_dir.mode == 0o700


def test_deploy_authorized_keys(linux_host):
    """Verify service-deploy user has authorized_keys file.

    The .ssh directory is mode 700 (owner-only), so we must use sudo to
    check file existence from the test runner's unprivileged SSH user.
    """
    result = linux_host.run("sudo stat /home/service-deploy/.ssh/authorized_keys")
    assert result.rc == 0, "authorized_keys file does not exist (checked via sudo stat)"


def test_homelab_directory_exists(linux_host):
    """Verify homelab tracking directory exists."""
    homelab_dir = linux_host.file("/etc/homelab")
    assert homelab_dir.exists
    assert homelab_dir.is_directory


def test_deployment_marker_exists(linux_host):
    """Verify deployment marker file exists."""
    marker = linux_host.file("/etc/homelab/.deployed")
    assert marker.exists


def test_unattended_upgrades_installed(linux_host):
    """Verify automatic security updates are configured (distro-aware)."""
    has_apt = linux_host.run("which apt-get").rc == 0
    if has_apt:
        assert linux_host.package("unattended-upgrades").is_installed
    else:
        has_dnf5 = linux_host.run("which dnf5").rc == 0
        if has_dnf5:
            # Fedora 41+: dnf-automatic was replaced by dnf5-plugin-automatic
            assert linux_host.package("dnf5-plugin-automatic").is_installed
        else:
            # Older RHEL/CentOS: dnf-automatic or yum-cron
            auto_update_installed = (
                linux_host.package("dnf-automatic").is_installed
                or linux_host.package("yum-cron").is_installed
            )
            assert auto_update_installed, "No automatic update package (dnf-automatic / yum-cron)"


def test_sudo_installed(linux_host):
    """Verify sudo is installed."""
    assert linux_host.package("sudo").is_installed


def test_syslog_running(linux_host):
    """Verify syslog service is running."""
    # Try different syslog implementations
    syslog_services = ["rsyslog", "syslog"]
    running = False
    for service in syslog_services:
        if linux_host.service(service).is_running:
            running = True
            break
    assert running, "No syslog service is running"


class TestSecurityConfiguration:
    """Test security hardening configuration."""

    def test_firewall_package_installed(self, linux_host):
        """Verify the appropriate firewall package is installed (distro-aware)."""
        has_apt = linux_host.run("which apt-get").rc == 0
        if has_apt:
            assert linux_host.package("ufw").is_installed
        else:
            assert linux_host.package("firewalld").is_installed

    def test_fail2ban_package_installed(self, linux_host):
        """Verify fail2ban is installed."""
        assert linux_host.package("fail2ban").is_installed
