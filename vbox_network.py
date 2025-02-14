import subprocess
import re

def list_vms():
    """List all VirtualBox VMs."""
    try:
        # Run the VBoxManage command to list all VMs
        result = subprocess.run(['VBoxManage', 'list', 'vms'], capture_output=True, text=True, check=True)
        vms = result.stdout.strip().split('\n')
        return [re.search(r'"(.*)"', vm).group(1) for vm in vms]
    except subprocess.CalledProcessError as e:
        print(f"Error listing VMs: {e}")
        return []

def get_vm_status(vm_name):
    """Get the status of a specific VM (e.g., running, powered off)."""
    try:
        result = subprocess.run(['VBoxManage', 'showvminfo', vm_name], capture_output=True, text=True, check=True)
        info = result.stdout
        status_match = re.search(r'State:\s+(\w+)', info)
        if status_match:
            return status_match.group(1)
        return "Unknown"
    except subprocess.CalledProcessError as e:
        print(f"Error getting status for VM {vm_name}: {e}")
        return "Unknown"

def get_vm_network_config(vm_name):
    """Get detailed network configuration for a specific VM."""
    try:
        # Run the VBoxManage command to show VM info
        result = subprocess.run(['VBoxManage', 'showvminfo', vm_name], capture_output=True, text=True, check=True)
        info = result.stdout

        # Extract network configuration
        network_config = {}
        for line in info.split('\n'):
            if 'NIC' in line and 'Attachment' in line:
                nic_match = re.search(r'NIC (\d+):', line)
                attachment_match = re.search(r'Attachment: (\w+)', line)
                if nic_match and attachment_match:
                    nic_number = nic_match.group(1)
                    attachment = attachment_match.group(1)
                    network_config[f'NIC {nic_number}'] = {'Attachment': attachment}

            if 'MAC:' in line:
                mac_match = re.search(r'MAC: ([\dA-Fa-f:]+)', line)
                if mac_match:
                    mac_address = mac_match.group(1)
                    network_config[f'NIC {nic_number}']['MAC Address'] = mac_address

            if 'Cable connected:' in line:
                cable_connected_match = re.search(r'Cable connected: (\w+)', line)
                if cable_connected_match:
                    cable_connected = cable_connected_match.group(1)
                    network_config[f'NIC {nic_number}']['Cable Connected'] = cable_connected

        return network_config
    except subprocess.CalledProcessError as e:
        print(f"Error getting network config for VM {vm_name}: {e}")
        return {}

def get_vm_port_forwarding_rules(vm_name):
    """Get port forwarding rules for a specific VM."""
    try:
        result = subprocess.run(['VBoxManage', 'showvminfo', vm_name, '--machinereadable'], capture_output=True, text=True, check=True)
        info = result.stdout

        # Extract port forwarding rules
        port_forwarding_rules = []
        for line in info.split('\n'):
            if 'Forwarding(' in line:
                # Example line: 'Forwarding(0)="ssh,tcp,,2222,,22"'
                rule_match = re.search(r'Forwarding\((\d+)\)="([^,]+),([^,]+),([^,]*),([^,]*),([^,]*),([^"]*)"', line)
                if rule_match:
                    rule_index = rule_match.group(1)
                    rule_name = rule_match.group(2)
                    protocol = rule_match.group(3)
                    host_ip = rule_match.group(4)
                    host_port = rule_match.group(5)
                    guest_ip = rule_match.group(6)
                    guest_port = rule_match.group(7)
                    port_forwarding_rules.append({
                        'Rule Index': rule_index,
                        'Rule Name': rule_name,
                        'Protocol': protocol,
                        'Host IP': host_ip or '0.0.0.0',  # Default to 0.0.0.0 if empty
                        'Host Port': host_port,
                        'Guest IP': guest_ip or '',  # Guest IP is optional
                        'Guest Port': guest_port
                    })
        return port_forwarding_rules
    except subprocess.CalledProcessError as e:
        print(f"Error getting port forwarding rules for VM {vm_name}: {e}")
        return []

def main():
    vms = list_vms()
    if not vms:
        print("No VMs found.")
        return

    for vm in vms:
        print(f"VM: {vm}")
        status = get_vm_status(vm)
        print(f"  Status: {status}")

        network_config = get_vm_network_config(vm)
        if network_config:
            print("  Network Configuration:")
            for nic, config in network_config.items():
                print(f"    {nic}:")
                for key, value in config.items():
                    print(f"      {key}: {value}")
        else:
            print("  No network configuration found.")

        port_forwarding_rules = get_vm_port_forwarding_rules(vm)
        if port_forwarding_rules:
            print("  Port Forwarding Rules:")
            for rule in port_forwarding_rules:
                print(f"    Rule {rule['Rule Index']}:")
                print(f"      Name: {rule['Rule Name']}")
                print(f"      Protocol: {rule['Protocol']}")
                print(f"      Host IP: {rule['Host IP']}")
                print(f"      Host Port: {rule['Host Port']}")
                print(f"      Guest IP: {rule['Guest IP']}")
                print(f"      Guest Port: {rule['Guest Port']}")
        else:
            print("  No port forwarding rules found.")
        print()

if __name__ == "__main__":
    main()
