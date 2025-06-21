#!/bin/bash

#Update and install docker 
sudo apt update
sudo apt install -y docker.io

# Create custom bridge network
sudo docker network create --subnet 172.18.0.0/16 vxlan-net

# View networks
sudo docker network ls

# Check bridge interface created by Docker
ip addr show


# Runs this command in the background and telling docker to attach the container to a custom user-defined network called ""vxlan-net" with a specific IP address(172.18.0.11) to the contaienr.
# We are keeping the container alive/running for 5 hour / 18000 seconds with the command "sleep 3000"
sudo docker run -d --net vxlan-net --ip 172.18.0.11 ubuntu sleep 18000
