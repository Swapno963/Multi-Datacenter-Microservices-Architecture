#!/bin/bash
set -e  # stop on first error


exec > /var/log/user-data.log 2>&1
set -xe

# Set variables
NETWORK_NAME="vxlan-net"
SUBNET="172.18.0.0/16"
STATIC_IP='172.18.0.11'
IMAGE_NAME="ubuntu"
CONTAINER_NAME="ubuntu-static-ip"

#Update and install docker 
sudo apt update
sudo apt install -y iproute2 docker.io git




# Clone repo if not exists
REPO_DIR="/home/ubuntu/Multi-Datacenter-Microservices-Architecture"
if [ ! -d "$REPO_DIR" ]; then
    git clone https://github.com/Swapno963/Multi-Datacenter-Microservices-Architecture.git "$REPO_DIR"
fi



# Create network if not exists
if ! docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
    echo "Creating Docker network: $NETWORK_NAME"
    sudo docker network create --subnet="$SUBNET" "$NETWORK_NAME"
else
    echo "Docker network $NETWORK_NAME already exists."
fi



# Remove existing container if exists
if sudo docker ps -a --format '{{.Names}}' | grep -qw "$CONTAINER_NAME"; then
    echo "Removing existing container: $CONTAINER_NAME"
    sudo docker rm -f "$CONTAINER_NAME"
fi


# Run container with static IP
echo "Launching container $CONTAINER_NAME with IP $STATIC_IP"
sudo docker run -d \
  --net "$NETWORK_NAME" \
  --ip "$STATIC_IP" \
  --name "$CONTAINER_NAME" \
  "$IMAGE_NAME" \
  sleep 18000




# Show container status
echo "Container launched. Verifying..."
sudo docker ps --filter "name=$CONTAINER_NAME"

# Print assigned IP
echo "Assigned IP:"
sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$CONTAINER_NAME"





if [ ! -f "$REPO_DIR/Scripts/run_dockerfile.sh" ]; then
    echo "Script not found!"
    exit 1
fi

chmod +x "$REPO_DIR/Scripts/run_dockerfile.sh"
"$REPO_DIR/Scripts/run_dockerfile.sh"
