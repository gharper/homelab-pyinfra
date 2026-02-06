"""
Backup deployment operations.
Configures backup scripts and schedules.
"""

from pyinfra.context import host
from pyinfra.operations import files, server

from deploy.utils import install_packages, log_deployment


def deploy():
    """Deploy backup configuration.

    Note: Caller is responsible for checking host.data.backup_enabled
    before calling this function.
    """
    # Install backup tools
    install_packages(
        [
            "rsync",
            "borgbackup",
        ]
    )

    # Create backup directories
    files.directory(
        name="Create backup configuration directory",
        path="/etc/homelab/backup",
        mode="755",
        _sudo=True,
    )

    files.directory(
        name="Create backup logs directory",
        path="/var/log/homelab/backup",
        mode="755",
        _sudo=True,
    )

    # Create backup script from template
    files.template(
        name="Create backup script from template",
        src="templates/homelab-backup.sh.j2",
        dest="/usr/local/bin/homelab-backup",
        mode="755",
        _sudo=True,
    )

    # Create cron job for scheduled backups
    # Parse cron expression: minute hour day_of_month month day_of_week
    backup_schedule = host.data.get("backup_schedule", "0 2 * * *")
    cron_parts = str(backup_schedule).split()
    server.crontab(
        name="Schedule automatic backups",
        command="/usr/local/bin/homelab-backup",
        minute=cron_parts[0] if len(cron_parts) > 0 else "0",
        hour=cron_parts[1] if len(cron_parts) > 1 else "2",
        day_of_month=cron_parts[2] if len(cron_parts) > 2 else "*",
        month=cron_parts[3] if len(cron_parts) > 3 else "*",
        day_of_week=cron_parts[4] if len(cron_parts) > 4 else "*",
        _sudo=True,
    )

    # Log deployment
    log_deployment("Backup")
