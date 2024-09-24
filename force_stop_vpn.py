import subprocess
import sys
import os
from banner import display_banner

def prompt_user_for_sudo():
    if os.geteuid() != 0:
        print("This script requires elevated privileges to run. Please run it with sudo.\n\n Eg:'sudo python force_stop_vpn.py'\n\n\t\t or\n\n    'sudo python3 force_stop_vpn.py'")
        exit(1)

def stop_wireguard():
    try:
        interface = subprocess.run(['sudo', 'wg', 'show'], capture_output=True, text=True, check=True)
        lines = interface.stdout.strip().split('\n')

        # Check if lines is empty or contains only an empty string
        if not lines or (len(lines) == 1 and lines[0] == ""):
            print("No WireGuard service found.")
            return

        stopped_interfaces = []  # List to keep track of stopped interfaces
        current_interface = None

        for line in lines:
            line = line.strip()  # Remove leading and trailing whitespace
            # Look for interface lines
            if line.startswith('interface: '):
                if current_interface:
                    # Stop the previous interface before moving to the next
                    subprocess.run(['sudo', 'wg-quick', 'down', f'WG_VPNS/{current_interface}.conf'], 
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    stopped_interfaces.append(current_interface)

                # Update the current interface
                current_interface = line.split(': ')[1]  # Get the interface name

        # Stop the last interface if there is one
        if current_interface:
            subprocess.run(['sudo', 'wg-quick', 'down', f'WG_VPNS/{current_interface}.conf'], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            stopped_interfaces.append(current_interface)

        if stopped_interfaces:
            print(f"Stopped WireGuard Successfully.")
        else:
            print("No active WireGuard interfaces found.")

    except subprocess.CalledProcessError:
        print("No WireGuard active service found.")


def stop_openvpn():
    try:
        openvpn_pids = subprocess.check_output(['pgrep', 'openvpn']).decode('utf-8').strip().split('\n')
        if openvpn_pids:
            subprocess.run(['sudo', 'kill'] + openvpn_pids, check=True)
            print("Stopped OpenVPN Successfully.")
        else:
            print("No OpenVPN active service found.")
    except subprocess.CalledProcessError:
        print("No OpenVPN service found.")

def stop_anonsurf():
    try:
        # Check if AnonSurf is active
        result = subprocess.run(['sudo', 'anonsurf', 'status'], capture_output=True, text=True, check=True)

        # Check the status output for "active"
        if "active" in result.stdout and "inactive" not in result.stdout:
            # If active, stop AnonSurf
            subprocess.run(['sudo', 'anonsurf', 'stop'], capture_output=True, text=True, check=True)
            print("Stopped AnonSurf Successfully.")
        else:
            print("No AnonSurf active service found.")
    except subprocess.CalledProcessError:
        print("No AnonSurf active service found.")

if __name__ == "__main__":
    display_banner()
    prompt_user_for_sudo()
    stop_wireguard()
    stop_openvpn()
    stop_anonsurf()
