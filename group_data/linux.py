"""
Group data for Linux hosts.
Configuration variables shared across all Linux servers.
"""

# Common packages to install on all Linux hosts
packages = [
    "vim",
    "htop",
    "curl",
    "wget",
    "git",
    "tmux",
    "net-tools",
    "iotop",
    "ncdu",
    "tree",
    "jq",
    "rsync",
    "unzip",
]

# System configuration
timezone = "UTC"

# User management
users = {
    "service-deploy": {
        "shell": "/bin/bash",
        "home": "/home/service-deploy",
        "groups": ["wheel"],
        "comment": "Deployment user for automation",
    },
}

# SSH configuration
ssh_port = 22
ssh_permit_root_login = "no"
ssh_password_authentication = "yes"
ssh_pubkey_authentication = "yes"

# Security settings
ufw_enabled = True
fail2ban_enabled = True

# Docker configuration (for hosts with docker_enabled=True)
docker_users = ["service-deploy"]

# Backup configuration
backup_enabled = True
backup_retention_days = 30
