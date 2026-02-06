"""
Inventory configuration for homelab infrastructure.
Defines all hosts with their metadata and connection details.

Note: In pyinfra v3, host data must be flat top-level keys alongside connection
parameters. Using a nested "data" key creates host.data.data, not host.data.
"""

# UniFi Controller
unifi = [
    (
        "unifi.mental404.com",
        {
            "ssh_user": "root",
            "environment": "production",
            "role": "network_controller",
            "monitoring_enabled": False,
        },
    ),
]

# Linux servers with specific roles
linux = [
    (
        "skully.mental404.com",
        {
            "role": "control_plane",
            "environment": "production",
            "docker_enabled": True,
            "monitoring_enabled": False,
        },
    ),
    (
        "node1.mental404.com",
        {
            "role": "compute",
            "environment": "production",
            "docker_enabled": True,
            "monitoring_enabled": False,
        },
    ),
    (
        "node2.mental404.com",
        {
            "role": "compute",
            "environment": "production",
            "docker_enabled": True,
            "monitoring_enabled": False,
        },
    ),
]

# Synology NAS
synology = [
    (
        "synology.mental404.com",
        {
            "ssh_user": "geromyh",
            "ssh_port": 22,
            "role": "storage",
            "environment": "production",
            "monitoring_enabled": False,
        },
    ),
]
