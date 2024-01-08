Raspberry Pi 5 (192.168.0.200, raspberrypi5-k8s)
- Kubernetes master

Raspberry Pi 5 (192.168.0.201, raspberrypi5-services)
- Kubernetes worker [Optional: cordon]
- nginx (Docker)
- registry (Docker)
- PostgreSQL / pgAdmin (Docker)
- Redis / RedisInsight (Docker)

Raspberry Pi 4 (192.168.0.202, raspberrypi4-ha)
- Kubernetes worker [Optional: cordon]
- HomeAssistent
- RaspBee (Zigbee hub)

