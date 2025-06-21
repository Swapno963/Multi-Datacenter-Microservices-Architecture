private_ip_outputs = ["34.201.55.123", "34.201.55.120"]


def update_line_and_store(file_path, match_string, new_line):
    with open(file_path, "r") as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        if match_string in line:
            updated_lines.append(new_line + "\n")
        else:
            updated_lines.append(line)

    # Join the updated lines into a single string variable
    result_script = "".join(updated_lines)
    return result_script


replace_string = "REMOTE_IPS=(" + " ".join(f'"{ip}"' for ip in private_ip_outputs) + ")"
dynamic_user_data = update_line_and_store(
    "../Scripts/advance_setup-vxlan.sh", "REMOTE_IPS=('x.x.x.x'", replace_string
)

print(dynamic_user_data)  # Output the modified script for verification
