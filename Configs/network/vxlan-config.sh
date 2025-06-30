
sudo ip link add vxlan-demo type vxlan \
  id 100 \
  remote "$1" \
  dstport 4789 \
  dev eth0
sudo ip link set vxlan-demo up

sudo ip link set vxlan-demo master vxlan-net

