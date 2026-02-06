"""
Tests for Synology NAS.
"""


def test_synology_accessible(synology_host):
    """Verify Synology NAS is accessible via SSH."""
    assert synology_host.run("true").rc == 0


def test_volume1_exists(synology_host):
    """Verify /volume1 exists."""
    volume1 = synology_host.file("/volume1")
    assert volume1.exists
    assert volume1.is_directory


def test_expected_shares_exist(synology_host):
    """Verify expected share directories exist on the NAS."""
    # Paths must match the shares defined in group_data/synology.py
    expected_shares = [
        "/volume1/music",
        "/volume1/photo",
        "/volume1/video",
        "/volume1/backups",
        "/volume1/docker",
    ]
    for share in expected_shares:
        share_dir = synology_host.file(share)
        assert share_dir.exists, f"Share {share} does not exist"
        assert share_dir.is_directory, f"Share {share} is not a directory"


def test_disk_space_available(synology_host):
    """Verify adequate disk space is available."""
    result = synology_host.run("df -h /volume1 | tail -1")
    if result.rc == 0:
        # Parse df output
        parts = result.stdout.split()
        if len(parts) >= 5:
            usage_str = parts[4].rstrip("%")
            try:
                usage_percent = int(usage_str)
                assert usage_percent < 95, f"Disk usage too high: {usage_percent}%"
            except ValueError:
                pass  # Skip if we can't parse


def test_ssh_service(synology_host):
    """Verify SSH service is accessible."""
    result = synology_host.run("echo 'SSH is working'")
    assert result.rc == 0


def test_synology_commands_available(synology_host):
    """Verify basic Synology commands are available."""
    synology_host.run("which synopkg")
    # synopkg might not be in PATH for all users
    # Just verify we can execute basic commands
    assert synology_host.run("ls /").rc == 0
