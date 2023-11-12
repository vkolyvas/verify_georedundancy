import paramiko
import re

# Function to establish an SSH connection to the router
def ssh_connect(host, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password)
    return client

# Function to execute a command on the router via SSH
def execute_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    return stdout.read().decode('utf-8')

# Function to parse georedundancy information from the command output
def parse_georedundancy_info(output):
    state_pattern = re.compile(r"Current state: (.+)")
    active_match = state_pattern.search(output)
    if active_match:
        active_state = active_match.group(1)
        return active_state
    else:
        return "Unable to determine active state"

# Function to parse ICCP group information from the command output
def parse_iccp_group_info(output):
    iccp_pattern = re.compile(r"Bundle-Ether(.+): ICCP Group (.+)")
    matches = iccp_pattern.findall(output)
    if matches:
        result = []
        for match in matches:
            interface = match[0]
            iccp_group = match[1]
            result.append(f"Interface {interface} belongs to ICCP Group {iccp_group}")
        return result
    else:
        return ["No ICCP group information found"]

# Function to verify georedundancy and ICCP group information on a router
def verify_georedundancy(router_ip, username, password):
    try:
        # Establish SSH connection to the router
        ssh_client = ssh_connect(router_ip, username, password)

        # Execute commands to retrieve georedundancy and ICCP group information
        command1 = "show redundancy"
        command2 = "show bundle-ethernet iccp-group"
        output1 = execute_command(ssh_client, command1)
        output2 = execute_command(ssh_client, command2)

        # Parse and print georedundancy information
        active_state = parse_georedundancy_info(output1)
        print(f"Router {router_ip}: Active state - {active_state}")

        # Parse and print ICCP group information
        iccp_group_info = parse_iccp_group_info(output2)
        for info in iccp_group_info:
            print(f"Router {router_ip}: {info}")

    except Exception as e:
        print(f"Error connecting to {router_ip}: {str(e)}")
    finally:
        # Close the SSH connection
        ssh_client.close()

# Example usage for ampe-asr9ka & ampe-asr9kb
router_ips = ["79.128.219.27", "79.128.219.102"]
username = "vkolyvas"
password = "password"

# Iterate through router IPs and check georedundancy information
for router_ip in router_ips:
    verify_georedundancy(router_ip, username, password)
