Microservice vxlan project

git clone https://github.com/Swapno963/Multi-Datacenter-Microservices-Architecture.git
cd [Multi-Datacenter-Microservices-Architecture](https://github.com/Swapno963/Multi-Datacenter-Microservices-Architecture)

# Setup Python environment

sudo apt-get update
apt install python3.8-venv

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Login to Pulumi backend (usually)

pulumi login

# Configure stack if not already present

pulumi stack init dev
pulumi config set aws:region us-east-1

# Run

pulumi up
