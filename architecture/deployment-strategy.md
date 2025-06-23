# Setup Python environment

sudo apt-get update
apt install python3.8-venv -y

python3 -m venv venv
source venv/bin/activate

1. Create credentials
2. Configure aws by: aws configure
3. 

Clone code

git clone
pulumi login

Create irs key for accessing aws instance through ec2 instance
aws ec2 create-key-pair --key-name MyKeyPair --query 'KeyMaterial' --output text > MyKeyPair.pem

Change permision of it : chmod 400 MyKeyPair.pem

connect to a ec2 instance : ssh -i MyKeyPair.pem ubuntu@<public_ip>

To check what are the containers running : docker ps

to see logs :




to destro all resourcess: pulumi destroy -y
