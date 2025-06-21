#!/bin/bash

# Install necessary tools
apt update -y
apt install -y iproute2 docker.io

# Configure VXLAN
ip link add vxlan100 type vxlan id 100 group 239.1.1.1 dev eth0 dstport 4789
ip addr add 10.0.100.1/24 dev vxlan100
ip link set up dev vxlan100

# Run NGINX container
docker run -d -p 8080:80 --network host nginx
