"""
Common infrastructure tests that apply to all hosts.
These tests use the specific host fixtures that match PyInfra inventory authentication.

Each test class runs the same set of common checks against its host type.
The verify_* helpers are used by all classes to avoid duplication.
"""

import time


def verify_ssh_accessible(host):
    """Verify SSH is accessible by running a simple command."""
    result = host.run("echo 'connection test'")
    assert result.rc == 0
    assert "connection test" in result.stdout


def verify_hostname_resolves(host):
    """Verify hostname is set correctly."""
    hostname = host.check_output("hostname")
    assert len(hostname) > 0


def verify_etc_hosts_exists(host):
    """Verify /etc/hosts file exists."""
    assert host.file("/etc/hosts").exists


def verify_dns_resolution(host):
    """Verify DNS resolution works."""
    result = host.run("getent hosts google.com || nslookup google.com")
    assert result.rc == 0


def verify_system_time_sync(host):
    """Verify system time is within reasonable range."""
    remote_time = int(host.check_output("date +%s"))
    local_time = int(time.time())
    time_diff = abs(remote_time - local_time)
    # Allow 5 minutes of drift
    assert time_diff < 300, f"Time drift too large: {time_diff} seconds"


def verify_root_user_exists(host):
    """Verify root user exists."""
    assert host.user("root").exists


def verify_tmp_directory_writable(host):
    """Verify /tmp is writable."""
    result = host.run("touch /tmp/test_write && rm /tmp/test_write")
    assert result.rc == 0


# --- Shared tests run against all host types ---


# Tests for Linux hosts (uses default SSH user, parametrized over 3 hosts)
class TestLinuxCommon:
    """Common tests for Linux hosts."""

    def test_ssh_accessible(self, linux_host):
        verify_ssh_accessible(linux_host)

    def test_hostname_resolves(self, linux_host):
        verify_hostname_resolves(linux_host)

    def test_etc_hosts_exists(self, linux_host):
        verify_etc_hosts_exists(linux_host)

    def test_dns_resolution(self, linux_host):
        verify_dns_resolution(linux_host)

    def test_system_time_sync(self, linux_host):
        verify_system_time_sync(linux_host)

    def test_root_user_exists(self, linux_host):
        verify_root_user_exists(linux_host)

    def test_tmp_directory_writable(self, linux_host):
        verify_tmp_directory_writable(linux_host)


# Tests for Synology NAS (uses ssh_user=geromyh)
class TestSynologyCommon:
    """Common tests for Synology NAS."""

    def test_ssh_accessible(self, synology_host):
        verify_ssh_accessible(synology_host)

    def test_hostname_resolves(self, synology_host):
        verify_hostname_resolves(synology_host)

    def test_dns_resolution(self, synology_host):
        verify_dns_resolution(synology_host)

    def test_system_time_sync(self, synology_host):
        verify_system_time_sync(synology_host)

    def test_tmp_directory_writable(self, synology_host):
        verify_tmp_directory_writable(synology_host)


# Tests for UniFi controller (uses ssh_user=root)
class TestUnifiCommon:
    """Common tests for UniFi controller."""

    def test_ssh_accessible(self, unifi_host):
        verify_ssh_accessible(unifi_host)

    def test_hostname_resolves(self, unifi_host):
        verify_hostname_resolves(unifi_host)

    def test_dns_resolution(self, unifi_host):
        verify_dns_resolution(unifi_host)

    def test_system_time_sync(self, unifi_host):
        verify_system_time_sync(unifi_host)

    def test_root_user_exists(self, unifi_host):
        verify_root_user_exists(unifi_host)

    def test_tmp_directory_writable(self, unifi_host):
        verify_tmp_directory_writable(unifi_host)
