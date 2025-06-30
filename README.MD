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


Create rsa key

cd ~/.ssh/


aws ec2 create-key-pair --key-name MyKeyPair --query 'KeyMaterial' --output text > MyKeyPair.pem


chmod 400 MyKeyPair.pem

Run

pulumi up







After completing we need to connect to the ec2 instance
cd Multi-Datacenter-Microservices-Architecture/cluster-infra
ssh -i MyKeyPair.pem ubuntu@<PUBLIC IP>


Go to this directory: /home/ubuntu/Multi-Datacenter-Microservices-Architecture/Configs/network
make the script executable: sudo chmod +x vxlan-config.sh 
run it with privet ip: ./vxlan-config.sh <PRIVET IP> <PRIVET IP> 42

to see a container ip address : sudo docker inspect <CONTAINER ID> | grep IPAddress
