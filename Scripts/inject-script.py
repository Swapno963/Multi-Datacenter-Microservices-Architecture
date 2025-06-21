import pulumi
import pulumi_aws as aws

# Define the number of instances you want to create
NUM_INSTANCES = 3

# Replace with your actual AMI ID and Subnet ID
# You can find AMIs in the AWS EC2 console, e.g., for Amazon Linux 2 or Ubuntu
# For example, a common Amazon Linux 2 AMI for us-east-1 might be 'ami-0abcdef1234567890'
# Ensure this AMI is valid for your region.
MY_AMI = "ami-0abcdef1234567890"  # <<< IMPORTANT: Replace with a valid AMI ID for your region!
MY_SUBNET_ID = "subnet-xxxxxxx"  # <<< IMPORTANT: Replace with a valid Subnet ID!

# Create a security group that allows SSH and all outbound traffic
# You might want to restrict inbound SSH to your IP for production environments
security_group = aws.ec2.SecurityGroup(
    "web-sg",
    description="Allow SSH access",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=[
                "0.0.0.0/0"
            ],  # WARNING: Open to the world. Restrict in production!
            description="Allow SSH from anywhere",
        )
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",  # All protocols
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],  # Allow all outbound traffic
        )
    ],
)

instances = []
private_ip_outputs = []

for i in range(NUM_INSTANCES):
    # Create the instance with a placeholder user_data for now
    # The actual user_data will be set dynamically later
    instance = aws.ec2.Instance(
        f"vxlan-ec2-{i}",
        ami=MY_AMI,
        instance_type="t2.micro",
        subnet_id=MY_SUBNET_ID,
        associate_public_ip_address=True,
        # We'll set the user_data dynamically below using .apply()
        user_data="placeholder",
        vpc_security_group_ids=[security_group.id],  # Attach the security group
        tags={"Name": f"vxlan-ec2-instance-{i}"},
    )
    instances.append(instance)
    private_ip_outputs.append(
        instance.private_ip
    )  # Store the Output[str] for private_ip

# Now, use pulumi.Output.all to get all private IPs once they are known
all_private_ips_output = pulumi.Output.all(*private_ip_outputs)

# Use .apply() to construct the user_data script using the resolved private IPs
dynamic_user_data = all_private_ips_output.apply(
    lambda ips: f"""#!/bin/bash
echo "All instance private IPs:" > /tmp/all_ips.txt
{"\n".join([f"echo {ip} >> /tmp/all_ips.txt" for ip in ips])}

# Example of using the IPs in a custom script
# For instance, you might want to configure VXLAN peers or update a host file
echo "Configuring network based on discovered IPs..."

# You can iterate through the IPs and perform actions
# For example, add entries to /etc/hosts for all instances
# IMPORTANT: This script runs on EACH instance, so each instance will have a
# /tmp/all_ips.txt with ALL IPs, and similarly, it will update its OWN /etc/hosts
# with ALL IPs.
{
    '''
for ip in ''' + ' '.join(ips) + '''; do
    echo "$ip    instance-$(echo $ip | tr "." "-")" >> /etc/hosts
done
    '''
}

# Add more custom commands here based on your VXLAN setup
# For example, installing packages, configuring network interfaces, etc.
# sudo apt update
# sudo apt install -y bridge-utils # For Debian/Ubuntu
# sudo yum update -y
# sudo yum install -y bridge-utils # For RHEL/CentOS/Amazon Linux

echo "User data script finished."
"""
)

# Loop again to update each instance's user_data with the dynamically generated script
# This is an important step. Because user_data depends on all IPs, it can only be
# set after all instances have been defined and their IPs gathered.
for i, instance in enumerate(instances):
    # Update the instance's user_data property.
    # When you use set_resource_property, Pulumi will track this as a dependency.
    pulumi.set_resource_property(instance, "user_data", dynamic_user_data)


# Export the public IPs and private IPs of the instances
# This will show up in your `pulumi up` output
for i, instance in enumerate(instances):
    pulumi.export(f"instance_{i}_public_ip", instance.public_ip)
    pulumi.export(f"instance_{i}_private_ip", instance.private_ip)
