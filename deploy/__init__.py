"""
Deploy module for homelab infrastructure.
Contains deployment operations organized by functionality.

Modules:
    common - Base Linux configuration (packages, users, timezone)
    security - SSH hardening, firewall, fail2ban
    monitoring - Monitoring and diagnostic tools (sysstat, iotop, htop)
    docker - Docker CE installation and configuration
    backup - Backup scripts and cron scheduling
    utils - Cross-distro package manager utilities
"""
