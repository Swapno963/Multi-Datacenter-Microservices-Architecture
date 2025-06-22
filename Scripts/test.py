def update_line_and_store(file_path, match_string, new_line, id):
    with open(file_path, "r") as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        if match_string in line:
            updated_lines.append(new_line + "\n")
        elif "VXLAN_ID='X'" in line:
            updated_lines.append(f'VXLAN_ID="{id}" ' + "\n")

        else:
            updated_lines.append(line)

    # Join the updated lines into a single string variable
    result_script = "".join(updated_lines)
    return result_script


vxlan_ids = [200, 300, 400]
private_ip_outputs = ["10.11.0.0", "10.11.0.1", "10.11.0.2"]
instances = [
    {"name": "dc1", "az": "us-west-2a", "cidr": ""},
    {"name": "dc2", "az": "us-west-2b", "cidr": ""},
    {"name": "dc3", "az": "us-west-2c", "cidr": ""},
]
for i, instance in enumerate(instances):
    own_ip_output = private_ip_outputs[i]
    replace_string = (
        "REMOTE_IPS=("
        + " ".join(f'"{ip}"' for ip in private_ip_outputs if ip != own_ip_output)
        + ")"
    )

    print(
        update_line_and_store(
            "../Scripts/advance_setup-vxlan.sh",
            "REMOTE_IPS=('x.x.x.x')",
            replace_string,
            vxlan_ids[i],
        )
    )
