import pulumi
import pulumi_aws as aws
import os

instance_type = "t2.micro"
ami = "ami-01811d4912b4ccb26"
key_name = "cluster-key"

# Create a VPC
vpc = aws.ec2.Vpc(
    "cluster-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={"Name": "cluster-vpc"},
)


# Create an Internet Gateway
internet_gateway = aws.ec2.InternetGateway(
    "cluster-internet-gateway", vpc_id=vpc.id, tags={"Name": "cluster-internet-gateway"}
)

# Create a Route Table
route_table = aws.ec2.RouteTable(
    "cluster-route-table",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=internet_gateway.id,
        )
    ],
    tags={"Name": "cluster-route-table"},
)


# Create a security group with egress and ingress rules
security_group = aws.ec2.SecurityGroup(
    "cluster-security-group",
    vpc_id=vpc.id,
    description="Cluster security group",
    ingress=[
        # SSH access from anywhere
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            self=True,
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
    tags={"Name": "cluster-security-group"},
)


# --- 4. Define DCs/Subnets ---
# dc_configs = [
#     {
#         "name": "dc1-na",
#         "cidr": "10.0.1.0/24",
#         "az": "ap-southeast-1a",
#     },
#     {
#         "name": "dc2-eu",
#         "cidr": "10.0.2.0/24",
#         "az": "ap-southeast-1a",
#     },
#     {
#         "name": "dc3-ap",
#         "cidr": "10.0.3.0/24",
#         "az": "ap-southeast-1a",
#     },
# ]

# --- 4. Define DCs/Subnets ---
dc_configs = [
    {
        "name": "dc1-primary-na",
        "cidr": "10.0.1.0/24",
        "az": "ap-southeast-1a",  # North America region (e.g., N. Virginia)
        "role": "Primary",
        "region": "North America",
    },
    {
        "name": "dc2-secondary-eu",
        "cidr": "10.0.2.0/24",
        "az": "ap-southeast-1a",  # Europe region (e.g., Frankfurt)
        "role": "Secondary",
        "region": "Europe",
    },
    {
        "name": "dc3-dr-ap",
        "cidr": "10.0.3.0/24",
        "az": "ap-southeast-1a",  # Asia-Pacific region (e.g., Singapore)
        "role": "Disaster Recovery",
        "region": "Asia-Pacific",
    },
]


instances = []
private_ip_outputs = []


def update_line_and_store(file_path, match_string, new_line, id, docker_unique_id):
    with open(file_path, "r") as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        if match_string in line:
            updated_lines.append(new_line + "\n")
        elif "VXLAN_ID='X'" in line:
            updated_lines.append(f'VXLAN_ID="{id}" ' + "\n")
        elif "STATIC_IP='172.18.0.11'" in line:
            updated_lines.append(f'STATIC_IP="{docker_unique_id}" ' + "\n")

        else:

            updated_lines.append(line)

    # Join the updated lines into a single string variable
    result_script = "".join(updated_lines)
    return result_script


# --- 5. Create subnets, associate route table, and launch instances ---
for dc in dc_configs:
    # Create a subnet
    subnet = aws.ec2.Subnet(
        f"{dc['name']}-subnet",
        vpc_id=vpc.id,
        cidr_block=dc["cidr"],
        availability_zone=dc["az"],
        map_public_ip_on_launch=True,
        tags={"Name": f"{dc['name']}-subnet"},
    )

    # Associate the route table with the subnet
    route_table_association = aws.ec2.RouteTableAssociation(
        f"{dc['name']}-rta", subnet_id=subnet.id, route_table_id=route_table.id
    )

    # The actual user_data will be set dynamically later
    instance = aws.ec2.Instance(
        f"{dc['name']}-ec2",
        instance_type=instance_type,
        ami=ami,
        subnet_id=subnet.id,
        key_name=key_name,
        associate_public_ip_address=True,
        vpc_security_group_ids=[security_group.id],  # Attach the security group
        tags={"Name": f"{dc['name']}-ec2"},
    )
    instances.append(instance)
    private_ip_outputs.append(
        instance.private_ip
    )  # Store the Output[str] for private_ip

# Now, use pulumi.Output.all to get all private IPs once they are known
# all_private_ips_output = pulumi.Output.all(*private_ip_outputs)

vxlan_ids = [200, 200, 200]
docker_unique_ids = ["172.18.0.3", "172.18.0.4", "172.18.0.5"]
for i, instance in enumerate(instances):
    own_ip_output = instance.private_ip
    all_ips = pulumi.Output.all(*private_ip_outputs)

    replace_string = (
        "REMOTE_IPS=("
        + " ".join(f'"{ip}"' for ip in all_ips if ip != own_ip_output)
        + ")"
    )

    user_data_output = pulumi.Output.all(own_ip_output, all_ips).apply(
        lambda args: update_line_and_store(
            "../Scripts/advance_setup-vxlan.sh",
            "REMOTE_IPS=('x.x.x.x')",
            replace_string,
            vxlan_ids[i],
            docker_unique_ids[i],
        )
    )

    final_instance = aws.ec2.Instance(
        f"{dc_configs[i]['name']}-ec2",
        ami=ami,
        instance_type=instance_type,
        subnet_id=instance.subnet_id,
        key_name=key_name,
        vpc_security_group_ids=[security_group.id],
        associate_public_ip_address=True,
        user_data=user_data_output,
        tags={"Name": f"{dc_configs[i]['name']}-ec2"},
        # opts=pulumi.ResourceOptions(replace_on_changes=["user_data"]),
    )

    instances[i] = final_instance

    # user_data_output = pulumi.Output.all(own_ip_output, all_ips_output).apply(
    #     lambda args: make_script(args[0], args[1])
    # )

    # Update the instance's user_data property.
    # When you use set_resource_property, Pulumi will track this as a dependency.
    # pulumi.set_resource_property(instance, "user_data", dynamic_user_data)


# Export the public IPs and private IPs of the instances
# This will show up in your `pulumi up` output
for i, instance in enumerate(instances):
    pulumi.export(f"instance_{i}_public_ip", instance.public_ip)
    pulumi.export(f"instance_{i}_private_ip", instance.private_ip)
