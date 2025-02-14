import subprocess

def get_vms():
    result = subprocess.run(["VBoxManage", "list", "vms", "--long"], capture_output=True, text=True)
    vms = result.stdout.split("\n\n")
    return [vm.strip() for vm in vms if vm.strip()]

def get_vm_network_info(vm_name):
    result = subprocess.run(["VBoxManage", "showvminfo", vm_name, "--machinereadable"], capture_output=True, text=True)
    info = result.stdout.split("\n")
    network_info = {}
    for line in info:
        if "=" in line:
            key, value = line.split("=", 1)
            network_info[key] = value.strip('"')
    return network_info

def get_port_forwarding(vm_name):
    result = subprocess.run(["VBoxManage", "showvminfo", vm_name, "--machinereadable"], capture_output=True, text=True)
    info = result.stdout.split("\n")
    port_forwarding = []
    for line in info:
        if line.startswith("Forwarding"):
            _, rule = line.split("=")
            rule = rule.strip('"').split(',')
            port_forwarding.append({
                "name": rule[0],
                "protocol": rule[1],
                "host_ip": rule[2],
                "host_port": rule[3],
                "guest_ip": rule[4],
                "guest_port": rule[5]
            })
    return port_forwarding

def main():
    vms = get_vms()
    for vm in vms:
        vm_name = vm.split('"')[1]
        print(f"\nVM Name: {vm_name}")
        network_info = get_vm_network_info(vm_name)
        
        for i in range(1, 9):  # VirtualBox supports up to 8 network adapters
            nic_key = f"nic{i}"
            if nic_key in network_info and network_info[nic_key] != "none":
                print(f"  Network Adapter {i}:")
                print(f"    Mode: {network_info[nic_key]}")
                
                if network_info[nic_key] == "nat":
                    port_forwarding = get_port_forwarding(vm_name)
                    if port_forwarding:
                        print("    Port Forwarding Rules:")
                        for rule in port_forwarding:
                            print(f"      Rule: {rule['name']}")
                            print(f"        Protocol: {rule['protocol']}")
                            print(f"        Host IP: {rule['host_ip']}")
                            print(f"        Host Port: {rule['host_port']}")
                            print(f"        Guest IP: {rule['guest_ip']}")
                            print(f"        Guest Port: {rule['guest_port']}")
                    else:
                        print("    No port forwarding rules found.")
                
                elif network_info[nic_key] == "bridged":
                    bridgeadapter = network_info.get(f"bridgeadapter{i}", "N/A")
                    macaddress = network_info.get(f"macaddress{i}", "N/A")
                    print(f"    Bridge Adapter: {bridgeadapter}")
                    print(f"    MAC Address: {macaddress}")

if __name__ == "__main__":
    main()
