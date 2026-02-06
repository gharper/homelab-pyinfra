"""
Group data for Synology NAS.
Configuration variables specific to Synology DSM.
"""

# Synology-specific SSH configuration
# Note: ssh_user is set per-host in inventory/inventory.py
ssh_port = 22

# Backup configuration
backup_schedule = "0 2 * * *"  # Daily at 2 AM
backup_retention_days = 30

# Shared folders/volumes
shares = {
    "music": "/volume1/music",
    "photo": "/volume1/photo",
    "video": "/volume1/video",
    "backups": "/volume1/backups",
    "docker": "/volume1/docker",
}
