#!/bin/bash
set -e  # Optional: stop on first error

# Set variables
NETWORK_NAME="vxlan-net"
SUBNET="172.18.0.0/16"
STATIC_IP="172.18.0.11"
IMAGE_NAME="ubuntu"
CONTAINER_NAME="ubuntu-static-ip"

#Update and install docker 
sudo apt update
sudo apt install -y iproute2 docker.io git



# Clone git repository 
git clone https://github.com/Swapno963/Multi-Datacenter-Microservices-Architecture.git
cd Multi-Datacenter-Microservices-Architecture


if [ ! -f ./Scripts/run_dockerfile.sh ]; then
    echo "Script not found!"
    exit 1
fi
chmod +x ./Scripts/run_dockerfile.sh
./Scripts/run_dockerfile.sh


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




VXLAN_IF="vxlan0"
VXLAN_ID='X' # Replace with your desired VXLAN ID
REMOTE_IPS=('x.x.x.x')  # Dynamically replace with the IPs of other remote hosts

# Create vxlan0 linked to the remote hosts
sudo ip link add $VXLAN_IF type vxlan id $VXLAN_ID dev eth0 dstport 4789

# Add FDB entries to know where to forward packets
for ip in "${REMOTE_IPS[@]}"; do
  sudo bridge fdb append to 00:00:00:00:00:00 dst $ip dev $VXLAN_IF
done

# Bring up vxlan0
sudo ip link set $VXLAN_IF up

# Attach vxlan0 to the docker bridge
sudo brctl addif br-vxlan $VXLAN_IF
