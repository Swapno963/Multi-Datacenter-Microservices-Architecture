#!/bin/bash
set -e  # stop on first error



# Check if exactly two IPs are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <IP1> <IP2>"
    exit 1
fi


VXLAN_IF="vxlan-net"
REMOTE_IPS=("$1" "$2")  # Dynamically replace with the IPs of other remote hosts
VXLAN_ID="$3" # Replace with your desired VXLAN ID

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