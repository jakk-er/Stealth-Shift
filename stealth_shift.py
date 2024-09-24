import argparse
import logging
import os
import re
import string
import subprocess
import sys
import time
import random
import threading
import requests
import socket
import struct
import fcntl
import signal
from config_manager import ensure_config_files_and_auth
from banner import display_banner

def get_arguments():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        usage="python %(prog)s -i <interface> [options]",
        description=(
            "Change MAC addresses and enhance anonymity with Anonsurf, OpenVPN, and WireGuard.\n"
            "Manage your network interface’s MAC address and anonymize your traffic with these VPN solutions."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "VPN Options:\n"
            "\n"
            "  When using -r/--random, -rc/--random-change, or -m/--mac options, you will be prompted to use either Anonsurf, OpenVPN, or WireGuard.\n"
            "\n"
            "  Each tool enhances your anonymity by routing traffic through secure VPN connections.\n"
            "  Choose 'yes' to start a VPN session, and 'no' to proceed without it.\n"
            "  This script supports up to 10 different VPN configurations for OpenVPN and WireGuard, stored in the VPNS directory.\n"
            "  Each configuration requires a corresponding authentication file in the AUTH directory."
        )
    )
    parser.add_argument("-i", "--interface", required=True, help="The network interface to change MAC address")
    parser.add_argument("-m", "--mac", help="Set the MAC address to this value")
    parser.add_argument("-r", "--random", action="store_true", help="Set a random MAC address")
    parser.add_argument("-rc", "--random-change", action="store_true", help="Change MAC address/VPN every specified interval")
    parser.add_argument("-vc", "--vpn-change", action="store_true", help="Change VPN every specified interval")
    parser.add_argument("-p", "--primary", action="store_true", help="Set the MAC address to primary (from file)")
    parser.add_argument("-s", "--status", action="store_true", help="Show current status of the interface")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    return parser.parse_args()

def configure_logging(verbose):
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(levelname)s - %(message)s' if verbose else '%(message)s'
    
    logging.basicConfig(level=level, format=format_str, handlers=[logging.StreamHandler()])
    
    return logging.getLogger(__name__)

def prompt_user_for_sudo():
    """Prompt the user to enter their password for sudo operations."""
    if os.geteuid() != 0:
        print("This script requires elevated privileges to run. Please run it with sudo.\n\n Eg:'sudo python stealthshift.py'\n\n\t\t or\n\n    'sudo python3 stealthshift.py'")
        exit(1)

stop_event = threading.Event()

def check_dependencies(logger):
    """Check for all the repositories and tools (softwares) required to run this script."""
    dependencies = {
        "curl": "curl",
        "pgrep": "pgrep",
        "kill": "kill",
        "sudo": "sudo",
        "wg": "wireguard-tools",
        "wg-quick": "wireguard-tools",
        "resolvconf": "resolvconf",
    }

    # Check for either python or python3
    python_or_python3 = False
    try:
        subprocess.check_output(["which", "python"], stderr=subprocess.STDOUT)
        python_or_python3 = True
    except subprocess.CalledProcessError:
        try:
            subprocess.check_output(["which", "python3"], stderr=subprocess.STDOUT)
            python_or_python3 = True
        except subprocess.CalledProcessError:
            pass

    if not python_or_python3:
        dependencies["python"] = "python"

    # Check for either ip or ifconfig
    ifconfig_or_ip = False
    try:
        subprocess.check_output(["which", "ifconfig"], stderr=subprocess.STDOUT)
        ifconfig_or_ip = True
    except subprocess.CalledProcessError:
        try:
            subprocess.check_output(["which", "ip"], stderr=subprocess.STDOUT)
            ifconfig_or_ip = True
        except subprocess.CalledProcessError:
            pass

    if not ifconfig_or_ip:
        dependencies["ifconfig"] = "ifconfig"

    missing_dependencies = []

    for dependency, package in dependencies.items():
        try:
            subprocess.check_output(["which", dependency], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            missing_dependencies.append(package)

    # Check for Python libraries
    python_libraries = {
        "requests": "requests"  # Only external library needs to be checked
    }

    for library, package_name in python_libraries.items():
        try:
            __import__(library)
        except ImportError:
            logger.error(f"{package_name} library in Python not found. Please install {package_name} library using 'pip install {package_name}' and run the script again.")
            sys.exit(1)  # Exit the script if a required library is missing

    # If we get here, all dependencies are satisfied
    if missing_dependencies:
        logger.error("Missing system dependencies:")
        for dependency in missing_dependencies:
            logger.error(f"{dependency} not found. Please install {dependency} and run the script again.")
        sys.exit(1)

    logger.debug("All dependencies are satisfied.")

def is_valid_interface(interface):
    """Check if the interface name is valid based on known naming conventions."""
    valid_prefixes = [
        'eth', 'wlan', 'ens', 'wlp', 'wlx',  # Traditional Linux and newer Linux naming
        'em', 're', 'ath', 'wi',  # BSD systems
        'en', 'lo',  # macOS and loopback
        'e1000g', 'bge',  # Solaris
        'veth', 'br', 'docker',  # Virtual and Docker interfaces
    ]
    
    # Match common patterns for interface names
    valid_patterns = [
        r'^eth\d+$',         # eth0, eth1, etc.
        r'^wlan\d+$',        # wlan0, wlan1, etc.
        r'^ens\d+$',         # ens33, ens160, etc.
        r'^wlp\d+s\d+$',     # wlp2s0, etc.
        r'^wlx[a-fA-F0-9]{12}$',  # wlx0024e8b6d3a, etc.
        r'^em\d+$',          # em0, em1, etc.
        r'^re\d+$',          # re0, re1, etc.
        r'^ath\d+$',         # ath0, ath1, etc.
        r'^wi\d+$',          # wi0, wi1, etc.
        r'^e1000g\d+$',      # e1000g0, e1000g1, etc.
        r'^bge\d+$',         # bge0, bge1, etc.
        r'^en\d+$',          # en0, en1, etc. (macOS)
        r'^lo$',             # loopback
        r'^veth\d+$',        # veth0, veth1, etc.
        r'^br-\w+$',         # br-<id> for bridge interfaces
        r'^docker0$',       # Docker bridge
    ]

    # Check if the interface name matches any of the valid patterns
    return any(re.match(pattern, interface) for pattern in valid_patterns)


def interface_exists(interface, logger):
    """Check if the network interface exists using ifconfig or ip."""
    ifconfig_command = ["ifconfig", interface]
    ip_command = ["ip", "link", "show", interface]
    
    try:
        # Check if ifconfig is available
        logger.debug(f"Checking if interface {interface} exists using 'ifconfig'")
        subprocess.check_output(ifconfig_command, stderr=subprocess.STDOUT)
        return True
    except FileNotFoundError:
        logger.debug("'ifconfig' command not found, falling back to 'ip'")
        # If ifconfig is not available, check with ip
        try:
            logger.debug(f"Checking if interface {interface} exists using 'ip link'")
            subprocess.check_output(ip_command, stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError:
            logger.debug(f"Interface {interface} does not exist.")
            return False
    except subprocess.CalledProcessError:
        logger.debug(f"Interface {interface} does not exist.")
        return False

def generate_mac_address(logger):
    """Generate a new MAC address with a local administered bit set."""
    # Locally administered address prefixes
    locally_administered_prefixes = [0x02, 0x06, 0x0A, 0x0E]

    # Select a random prefix from the valid ones
    first_byte = random.choice(locally_administered_prefixes)
    
    # Generate the rest of the MAC address
    mac = [first_byte] + [random.randint(0x00, 0xff) for _ in range(5)]
    
    # Format each byte as a two-digit hexadecimal number
    mac_hex = [f"{x:02x}" for x in mac]
    
    # Join the bytes with ':' to form the MAC address string
    random_mac = ':'.join(mac_hex)
    
    # Log the generated MAC address
    logger.debug(f"Generated MAC address: {random_mac}")
    
    return random_mac

def is_valid_mac(mac_address, logger):
    """Validate the MAC address format."""
    valid = bool(re.fullmatch(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", mac_address))
    if not valid:
        logger.debug(f"Invalid MAC address format: {mac_address}. Expected format: XX:XX:XX:XX:XX:XX")
    return valid

def is_valid_ip(ip):
    """Check if the given IP address is valid using regex."""
    pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
    return re.match(pattern, ip) is not None

def get_current_mac(interface, logger):
    """Retrieve the current MAC address of the specified interface."""
    ifconfig_command = ["ifconfig", interface]
    ip_command = ["ip", "link", "show", interface]

    try:
        # Try to get MAC address using ifconfig
        logger.debug(f"Getting current MAC address for {interface} using 'ifconfig'")
        ifconfig_result = subprocess.check_output(ifconfig_command).decode('utf-8')
        mac_address_search_result = re.search(r"([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}", ifconfig_result)
    except FileNotFoundError:
        logger.debug("'ifconfig' command not found, falling back to 'ip link'")
        try:
            # If ifconfig is not available, use ip link
            logger.debug(f"Getting current MAC address for {interface} using 'ip link'")
            ip_result = subprocess.check_output(ip_command).decode('utf-8')
            mac_address_search_result = re.search(r"link/ether ([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}", ip_result)
        except subprocess.CalledProcessError as e:
            logger.error(f"Could not retrieve MAC address using 'ip link': {e}")
            return None
    except subprocess.CalledProcessError:
        logger.error(f"Could not retrieve MAC address using 'ifconfig'")
        return None

    if mac_address_search_result:
        current_mac = mac_address_search_result.group(0)
        logger.debug(f"Current MAC address: {current_mac}")
        return current_mac
    else:
        logger.error("Could not read MAC address")
        return None

def change_mac_interface_ioctl(interface, new_mac, logger):
    """Change the MAC address of the specified interface using ioctl."""
    try:
        # Open a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Ensure interface name is 16 bytes long (pad if necessary)
        interface_padded = interface.ljust(16, '\0').encode('utf-8')
        
        # Convert MAC address to bytes
        new_mac_bytes = bytes.fromhex(new_mac.replace(':', ''))
        
        # Prepare the ifreq structure
        ifr = struct.pack('16sH6s', interface_padded, socket.AF_UNIX, new_mac_bytes)
        
        # Define the SIOCSIFHWADDR constant (for Linux, it's 0x8924)
        SIOCSIFHWADDR = 0x8924
        
        # Perform the ioctl call to change the MAC address
        fcntl.ioctl(s.fileno(), SIOCSIFHWADDR, ifr)
        
        # Close the socket
        s.close()
        
        logger.info(f"MAC address successfully changed to {new_mac}")
        return True
    except Exception as e:
        logger.error(f"Error changing MAC address using ioctl: {e}")
        return False

def execute_commands(commands, logger):
    """Execute a list of commands with error handling and logging."""
    for cmd in commands:
        try:
            logger.debug(f"Executing command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            time.sleep(1)  # Delay between commands
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with error: {e}")
            raise  # Re-raise the exception to stop execution if a command fails

def bring_interface_down_and_up(interface, new_mac, logger, use_ip=False):
    """Bring the interface down, change MAC address, and bring it up using either 'ifconfig' or 'ip link'."""
    if use_ip:
        commands = [
            ["sudo", "ip", "link", "set", "dev", interface, "down"],
            ["sudo", "ip", "link", "set", "dev", interface, "address", new_mac],
            ["sudo", "ip", "link", "set", "dev", interface, "up"]
        ]
    else:
        commands = [
            ["sudo", "ifconfig", interface, "down"],
            ["sudo", "ifconfig", interface, "hw", "ether", new_mac],
            ["sudo", "ifconfig", interface, "up"]
        ]
    
    execute_commands(commands, logger)

def change_mac(interface, new_mac, logger):
    """Change the MAC address of the specified interface."""
    try:
        logger.debug(f"Attempting to change MAC address for {interface} to {new_mac} using ioctl")
        if change_mac_interface_ioctl(interface, new_mac, logger):
            return True
        else:
            logger.debug("Failed to change MAC address using ioctl. Trying 'ifconfig'...")
            if subprocess.call(["which", "ifconfig"], stdout=subprocess.DEVNULL) == 0:
                bring_interface_down_and_up(interface, new_mac, logger, use_ip=False)
                logger.info(f"MAC address successfully changed to {new_mac}")
                return True
            else:
                raise FileNotFoundError("ifconfig not found")
    except FileNotFoundError:
        logger.debug(f"Failed to change MAC address using 'ifconfig'. Trying 'ip link'...")
        try:
            bring_interface_down_and_up(interface, new_mac, logger, use_ip=True)
            logger.info(f"MAC address successfully changed to {new_mac}")
            return True
        except Exception as e:
            logger.error(f"Error changing MAC address using 'ip link': {e}")
            return False

def save_primary_mac_to_file(interface, primary_mac, logger):
    """Save the primary MAC address to a file."""
    filename = f"{interface}_primary_mac.txt"
    try:
        # Remove any prefix like 'link/ether' if present
        primary_mac = primary_mac.split()[-1] if ' ' in primary_mac else primary_mac
        with open(filename, 'w') as file:
            file.write(primary_mac)
        logger.info(f"Primary MAC address saved to file for {interface}: {primary_mac}")
        return True
    except Exception as e:
        logger.error(f"Failed to save primary MAC address to file: {e}")
        return False

def read_primary_mac_from_file(interface, logger):
    """Read the primary MAC address from a file."""
    filename = f"{interface}_primary_mac.txt"
    logger.debug(f"Reading primary MAC address from file: {filename}")
    try:
        with open(filename, 'r') as file:
            primary_mac = file.read().strip()
            # Ensure no prefix like 'link/ether' is present
            primary_mac = primary_mac.split()[-1] if ' ' in primary_mac else primary_mac
        logger.debug(f"Primary MAC address read from file for {interface}")
        return primary_mac
    except FileNotFoundError:
        logger.warning(f"No primary MAC address file found for {interface}")
        return None
    except IOError as e:
        logger.error(f"IOError while reading primary MAC address from file: {e}")
        return None

def set_primary_mac(interface, primary_mac, logger):
    """Set the MAC address to the primary MAC address."""
    primary_mac_file = f"{interface}_primary_mac.txt"
    
    if primary_mac:
        logger.debug(f"Setting MAC address to primary MAC for {interface}")
        if change_mac(interface, primary_mac, logger):
            return True
        else:
            logger.error(f"Failed to set MAC address to {primary_mac} for {interface}")
            return False
    else:
        if os.path.isfile(primary_mac_file):
            logger.error(f"Primary MAC address file exists but no MAC address is available to set for {interface}. Please check if the file contains a valid MAC address.")
        else:
            logger.error(f"Primary MAC address file not found for {interface}. The MAC address could not be set.")
        return False

def get_interface_status(interface, primary_mac, logger):
    """Get the current status of the interface."""
    logger.debug(f"Getting status for {interface}")
    current_mac = get_current_mac(interface, logger)
    if current_mac:
        if current_mac == primary_mac:
            logger.info(f"Current MAC address for {interface}: {current_mac} (Primary MAC)")
        else:
            logger.info(f"Current MAC address for {interface}: {current_mac}")
    else:
        logger.error(f"Could not retrieve current MAC address for {interface}")

def wait_for_interface_up(interface, logger):
    """Wait for the interface to come up."""
    logger.debug(f"Waiting for interface {interface} to come up...")
    while True:
        ip_command = ["ip", "link", "show", interface]
        try:
            ip_result = subprocess.check_output(ip_command).decode('utf-8')
            if "state UP" in ip_result:
                logger.debug(f"Interface {interface} is up.")
                break
        except subprocess.CalledProcessError as e:
            logger.error(f"Error checking interface status: {e}")
        time.sleep(1)

def set_file_permissions(directory, logger):
    """Set file permissions for all .conf files in the given directory."""
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".conf"):
                file_path = os.path.join(directory, filename)
                # Set read and write permissions for the owner only
                subprocess.run(['sudo', 'chmod', '600', file_path], check=True)
                logger.debug(f"Permissions set for file: {file_path}")
    except Exception as e:
        logger.error(f"Error setting file permissions: {e}")

def start_wireguard(verbose, logger, interface):
    """Start WireGuard."""
    logger.debug("Attempting to start WireGuard")
    try:
        # Generate a random number between 1 and 10
        random_number = random.randint(1, 10)
        
        # Construct the filename using the random number
        filename = f"WG_VPNS/config-{random_number}.conf"
        
        # Start the WireGuard interface
        subprocess.run(['sudo', 'wg-quick', 'up', filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # Wait for the interface to come up
        wait_for_interface_up(interface, logger)

        if verbose:
            print("Started WireGuard interface: {running_interface}")
        else:
            logger.info("WireGuard started successfully.")
        return True
    except subprocess.CalledProcessError as e:
        if verbose:
            print(e.output)
        logger.error(f"Failed to start WireGuard: {e}")
        return False


def stop_wireguard(verbose, logger):
    """Stop WireGuard."""
    logger.debug("Attempting to stop WireGuard")
    try:
        # Get the currently running interface
        interface = subprocess.run(['sudo', 'wg', 'show'], capture_output=True, text=True, check=True)
        # Extract the interface name from the output
        lines = interface.stdout.strip().split('\n')
        if lines:
            running_interface = lines[0].split(': ')[1]  # Get the interface name from the first line
            logger.debug(f"Running WireGuard interface found: {running_interface}")

            # Stop the WireGuard interface
            subprocess.run(['sudo', 'wg-quick', 'down', f'WG_VPNS/{running_interface}.conf'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            if verbose:
                print(f"Stopped WireGuard interface: {running_interface}")
            else:
                logger.info("WireGuard stopped.")
        else:
            logger.debug("No running WireGuard interfaces found.")
    except subprocess.CalledProcessError as e:
        if verbose:
            print(e.output)
        logger.error(f"Error stopping WireGuard: {e}")

def start_openvpn(verbose, logger, interface):
    """Start OpenVPN."""
    logger.debug("Attempting to start OpenVPN")
    try:
        random_number = random.randint(1, 10)
        filename = f"OP_VPNS/config-{random_number}.ovpn"
        wait_for_interface_up(interface, logger)
        subprocess.run(['sudo', 'openvpn', '--config', filename, '--daemon'], check=True)
        if verbose:
            print(f"Started OpenVPN with config: {filename}")
        logger.info("OpenVPN started successfully.")
        return True
    except subprocess.CalledProcessError as e:
        if verbose:
            print(e.output)
        logger.error(f"Failed to start OpenVPN: {e}")
        return False

def stop_openvpn(verbose, logger):
    """Stop OpenVPN."""
    logger.debug("Attempting to stop OpenVPN")
    try:
        openvpn_pids = subprocess.check_output(['pgrep', 'openvpn']).decode('utf-8').strip().split('\n')
        if openvpn_pids:
            subprocess.run(['sudo', 'kill'] + openvpn_pids, check=True)
            if verbose:
                print(f"Stopped OpenVPN processes: {', '.join(openvpn_pids)}")
            logger.info("OpenVPN stopped.")
        else:
            logger.debug("No OpenVPN processes found.")
    except subprocess.CalledProcessError as e:
        if verbose:
            print(e.output)
        logger.error(f"Error stopping OpenVPN: {e}")

def start_anonsurf(verbose, logger):
    """Start Anonsurf."""
    logger.debug("Attempting to start Anonsurf")
    try:
        result = subprocess.run(['sudo', 'anonsurf', 'start'], capture_output=True, text=True, check=True)
        if verbose:
            print(result.stdout)
        logger.info("Anonsurf started successfully.")
        return True
    except subprocess.CalledProcessError as e:
        if verbose:
            print(e.output)
        logger.error(f"Failed to start Anonsurf: {e}")
        return False

def stop_anonsurf(verbose, logger):
    """Stop Anonsurf."""
    logger.debug("Attempting to stop Anonsurf")
    try:
        result = subprocess.run(['sudo', 'anonsurf', 'stop'], capture_output=True, text=True, check=True)
        if verbose:
            print(result.stdout)
        logger.info("Anonsurf stopped.")
    except subprocess.CalledProcessError as e:
        if verbose:
            print(e.output)
        logger.error(f"Error stopping Anonsurf: {e}")

def start_VPN(vpn_type, verbose, logger, interface, config_file=None):
    """Start the specified VPN type."""
    logger.debug(f"Attempting to start {vpn_type} VPN")
    try:
        if vpn_type == "wireguard":
            start_wireguard(verbose, logger, interface, config_file)
        elif vpn_type == "openvpn":
            start_openvpn(verbose, logger, interface)
        elif vpn_type == "anonsurf":
            start_anonsurf(verbose, logger)
        else:
            logger.error(f"Unsupported VPN type: {vpn_type}")
            return False
        return True
    except Exception as e:
        logger.error(f"Failed to start {vpn_type}: {e}")
        return False

def stop_VPN(vpn_type, verbose, logger):
    """Stop the specified VPN type."""
    logger.debug(f"Attempting to stop {vpn_type} VPN")
    try:
        if vpn_type == "wireguard":
            stop_wireguard(verbose, logger)
        elif vpn_type == "openvpn":
            stop_openvpn(verbose, logger)
        elif vpn_type == "anonsurf":
            stop_anonsurf(verbose, logger)
        else:
            logger.error(f"Unsupported VPN type: {vpn_type}")
    except Exception as e:
        logger.error(f"Failed to stop {vpn_type}: {e}")

def cleanup(interface, primary_mac, wireguard_started, openvpn_started, anonsurf_started, mac_changed, verbose, logger):
    """Cleanup actions including restoring primary MAC address and stopping WireGuard."""
    logger.debug("Cleaning up...")

    # Bring the interface back up if it was down
    try:
        logger.debug(f"Checking if interface {interface} is up.")
        ip_command = ["ip", "link", "show", interface]
        ifconfig_command = ["ifconfig", interface]

        try:
            ifconfig_result = subprocess.check_output(ifconfig_command).decode('utf-8')
            if "UP" not in ifconfig_result:
                logger.debug(f"Interface {interface} is down. Bringing it back up.")
                subprocess.run(["sudo", "ifconfig", interface, "up"], check=True)
        except FileNotFoundError:
            logger.debug("'ifconfig' command not found, falling back to 'ip link'")
            ip_result = subprocess.check_output(ip_command).decode('utf-8')
            if "state UP" not in ip_result:
                logger.debug(f"Interface {interface} is down. Bringing it back up.")
                subprocess.run(["sudo", "ip", "link", "set", "dev", interface, "up"], check=True)

        # Recheck if the primary MAC address file exists
        primary_mac_file = f"{interface}_primary_mac.txt"
        if os.path.isfile(primary_mac_file):
            logger.debug("Primary MAC address file found. Attempting to restore MAC address.")
            
            # Read the primary MAC address from the file
            with open(primary_mac_file, 'r') as f:
                primary_mac = f.read().strip()

            # Compare the current MAC address with the primary MAC address
            current_mac = get_current_mac(interface, logger)
            if current_mac and current_mac != primary_mac:
                logger.debug(f"Current MAC address ({current_mac}) does not match primary MAC address ({primary_mac}). Restoring primary MAC address.")
                if not set_primary_mac(interface, primary_mac, logger):
                    logger.error("Failed to restore the primary MAC address.")
            else:
                logger.debug("Current MAC address matches the primary MAC address or MAC address is not changed.")
        else:
            logger.error(f"Primary MAC address file not found for {interface}. Cannot restore the MAC address.")
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to check or bring up interface {interface}: {e}")

    # Stop WireGuard if it was started
    if wireguard_started:
        stop_wireguard(verbose, logger)
    if openvpn_started:
        stop_openvpn(verbose, logger)
    if anonsurf_started:
        stop_anonsurf(verbose, logger)

def prompt_user_for_VPN(vpn_change=False):
    """Prompt user to start VPN and choose the VPN type."""
    max_attempts = 3

    if vpn_change:
        # Directly prompt for VPN choice if -vc or --vpn-change is provided
        return ask_vpn_choice()

    for attempt in range(max_attempts):
        try:
            print("\n")
            start_vpn_prompt = input("Do you want to start VPN? (yes/y/no/n): ").strip().lower()
            if start_vpn_prompt in ['yes', 'y']:
                return ask_vpn_choice()
            elif start_vpn_prompt in ['no', 'n']:
                return None
            else:
                print("Invalid input. Please enter 'yes', 'y', 'no', or 'n'.")
        except (KeyboardInterrupt, EOFError):
            print("\nInput interrupted. Exiting...")
            sys.exit(1)

    print("Maximum attempts reached. Exiting...")
    sys.exit(1)

def ask_vpn_choice():
    """Ask user to choose the VPN type."""
    try:    
        vpn_choice = input("""\n\n1. Anonsurf (Quickstart)\n\n2. OpenVPN (Customizable)\n\n3. Wireguard (Customizable)\n\nPlease choose your VPN:""")
        if vpn_choice == '1':
            print("\nYou have chosen Anonsurf.\n")
            return "anonsurf"
        elif vpn_choice == '2':
            print("\nYou have chosen OpenVPN.\n")
            return "openvpn"
        elif vpn_choice == '3':
            print("\nYou have chosen Wireguard.\n")
            return "wireguard"
        else:
            print("Invalid choice. Please choose a valid VPN option.")
            return ask_vpn_choice()
    except (KeyboardInterrupt):
        print("\nInput interrupted. Exiting...")
        sys.exit(1)
        
def change_mac_periodically(interface, logger, interval):
    """Periodically change the MAC address of the specified interface."""
    try:
        while not stop_event.is_set():
            new_mac = generate_mac_address(logger)
            if change_mac(interface, new_mac, logger):
                clear_line() 
                sys.stdout.write("\033[K")  # Clear the current line
                print(f"New MAC address is {new_mac}.")
            else:
                logger.warning("Failed to change MAC address.")
            stop_event.wait(interval)  # Wait for the user-defined interval or until stop_event is set
    except KeyboardInterrupt:
        logger.debug("Periodic MAC address change interrupted by user.")

def change_vpn_periodically(vpn_type, interface, logger, interval, initial_ip):
    """Periodically restart the specified VPN connection every specified interval."""
    try:
        while not stop_event.is_set():
            logger.debug(f"Restarting {vpn_type}")
            try:
                # Stop the VPN interface if it exists
                if vpn_type == "wireguard":
                    stop_wireguard(False, logger)
                elif vpn_type == "openvpn":
                    stop_openvpn(False, logger)

                # Wait for the interface to come up
                wait_for_interface_up(interface, logger)

                # Attempt to start the VPN with retries
                start_success = False
                for attempt in range(5):  # Retry up to 5 times
                    try:
                        if vpn_type == "wireguard":
                            # Randomly select a WireGuard configuration
                            random_number = random.randint(1, 10)
                            filename = f"WG_VPNS/config-{random_number}.conf"
                            logger.debug(f"Starting WireGuard with config: {filename} (Attempt {attempt + 1})")
                            subprocess.run(['sudo', 'wg-quick', 'up', filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                            wireguard_running = subprocess.run(['pgrep', 'wg'], stdout=subprocess.DEVNULL, check=True)
                            if wireguard_running.returncode == 0:
                                clear_line()
                                sys.stdout.write("\033[K") 
                                print("WireGuard: New connection established.")
                                start_success = True
                                break
                        elif vpn_type == "openvpn":
                            # Start OpenVPN with the configuration file
                            random_number = random.randint(1, 10)
                            filename = f"OP_VPNS/config-{random_number}.ovpn"
                            logger.debug(f"Starting OpenVPN with config: {filename} (Attempt {attempt + 1})")
                            subprocess.run(['sudo', 'openvpn', '--config', filename, '--daemon'], check=True)
                            openvpn_running = subprocess.run(['pgrep', 'openvpn'], stdout=subprocess.DEVNULL, check=True)
                            if openvpn_running.returncode == 0:
                                clear_line()
                                sys.stdout.write("\033[K") 
                                print("OpenVPN: New connection established.")
                                start_success = True
                                break
                        elif vpn_type == "anonsurf":
                            logger.debug("Changing Anonsurf...")
                            subprocess.run(["sudo", "anonsurf", "change"], capture_output=True, text=True, check=True)
                            clear_line()
                            sys.stdout.write("\033[K") 
                            print("AnonSurf: New connection established.")
                            start_success = True
                            break

                    except subprocess.CalledProcessError as e:
                        logger.error(f"Failed to start {vpn_type}: {e}. Retrying... ({attempt + 1}/5)")
                        time.sleep(5)  # Wait before retrying

                if not start_success:
                    logger.error(f"Failed to start {vpn_type} after multiple attempts.")
                    continue  # Skip to the next interval if VPN fails to start

                # Check if the IP address has changed from the initial
                for _ in range(10):  # Retry up to 10 times
                    new_public_ip = get_public_ip(logger)
                    if new_public_ip and new_public_ip != initial_ip and is_valid_ip(new_public_ip):
                        clear_line()
                        sys.stdout.write("\033[K") 
                        print(f"New public IP address: {new_public_ip}")
                        break  # Exit loop if the IP has changed successfully
                    else:
                        logger.debug(f"Current public IP is still the same as initial: {initial_ip}")
                    time.sleep(5)  # Wait and retry

                # After the loop, check if IP did not change
                if new_public_ip == initial_ip:
                    print(f"Your public IP did not change: {initial_ip}")
                    logger.debug("IP address did not change after starting VPN.")

            except subprocess.CalledProcessError as e:
                logger.error(f"Error executing {vpn_type} commands: {e}")

            stop_event.wait(interval)  # Wait for the user-defined interval or until stop_event is set

    except KeyboardInterrupt:
        logger.debug(f"Periodic {vpn_type} shift interrupted by user.")

def fetch_initial_public_ip(logger):
    """Fetch and return the initial public IP address before any VPN is started."""
    try:
        initial_ip = subprocess.check_output(['curl', '-s', 'ifconfig.me']).decode('utf-8').strip()
        logger.info(f"Primary public IP address: {initial_ip}")
        return initial_ip
    except subprocess.CalledProcessError as e:
        logger.error(f"Error fetching initial public IP address: {e}")
        sys.exit(1)  # Exit if the initial IP fetch fails since it's critical

def get_public_ip(logger):
    """Get the current public IP address."""
    try:
        response = subprocess.check_output(['curl', '-s', 'ifconfig.me'])
        public_ip = response.decode('utf-8').strip()
        logger.debug(f"Public IP address retrieved: {public_ip}")
        return public_ip
    except subprocess.CalledProcessError as e:
        logger.error(f"Error retrieving public IP address: {e}")
        return None

def prompt_for_interval_time(default=300):
    """Prompt the user to specify the interval time."""
    print(f"Default interval time is {default} seconds.")
    while True:
        try:
            interval = input(f"Enter the interval time in seconds (10 to 3600) or press Enter to use default ({default}): ").strip()
            if interval == "":
                return default
            interval = int(interval)
            if 10 <= interval <= 3600:
                return interval
            else:
                print("Invalid input. Please enter a value between 10 and 3600 seconds.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def countdown(interval):
    """Countdown timer."""
    original_interval = interval  # Store the original interval value
    while not stop_event.is_set():
        while interval > 0:
            mins, secs = divmod(interval, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
            clear_line()
            sys.stdout.write(f"\rRemaining time: {timer} | Press Ctrl+C to Exit")
            sys.stdout.flush()
            time.sleep(1)
            interval -= 1
            if stop_event.is_set():
                break
        interval = original_interval  # Reset the interval to the original value
        if stop_event.is_set():
            break

def clear_line():
    """Clear the current line in the console."""
    sys.stdout.write('\r')
    sys.stdout.flush()

def signal_handler(sig, frame):
    """Handle signal interrupts."""
    stop_event.set()  # Signal threads to stop

def main():
    """Main function to handle arguments and execute the script logic."""
    global stop_event
    args = get_arguments()
    logger = configure_logging(args.verbose)
    interface = args.interface

    display_banner()

    signal.signal(signal.SIGINT, signal_handler)

    # Check dependencies
    check_dependencies(logger)

    # Prompt for sudo access before performing any privileged operations
    prompt_user_for_sudo()
    
    #check config files and folders
    ensure_config_files_and_auth('OP_VPNS', 'AUTH', 'WG_VPNS')

    # Fetch and store the initial public IP
    initial_ip = fetch_initial_public_ip(logger)

    if not is_valid_interface(interface):
        logger.error(f"Invalid interface name: {interface}")
        sys.exit(1)

    if args.mac and not is_valid_mac(args.mac, logger):
        logger.error(f"Invalid MAC address format: {args.mac}")
        sys.exit(1)

    if not interface_exists(interface, logger):
        logger.error(f"Interface {interface} does not exist.")
        sys.exit(1)

    primary_mac = read_primary_mac_from_file(interface, logger)

    if args.primary:
        if primary_mac:
            set_primary_mac(interface, primary_mac, logger)
        else:
            logger.warning("Primary MAC address file does not exist. Creating a new primary MAC address file.")
            current_mac = get_current_mac(interface, logger)
            if current_mac:
                save_primary_mac_to_file(interface, current_mac, logger)
                logger.info(f"Primary MAC address ({current_mac}) was successfully saved to file.")
                set_primary_mac(interface, current_mac, logger)
            else:
                logger.error("Failed to retrieve current MAC address to save as primary.")
                sys.exit(1)
        sys.exit(0)

    if args.status:
        get_interface_status(interface, primary_mac, logger)
        sys.exit(0)

    # Handle MAC address changes
    mac_changed = False
    try:
        if args.random_change:
            # Prompt for interval time if -rc is used
            interval_time = prompt_for_interval_time(default=300)

            # Ensure primary MAC is saved before starting periodic changes
            if primary_mac is None:
                primary_mac = get_current_mac(interface, logger)
                if primary_mac:
                    save_primary_mac_to_file(interface, primary_mac, logger)
                else:
                    logger.error("Failed to retrieve current MAC address to save as primary.")
                    sys.exit(1)

            # Set logging level to WARNING or higher when -rc is selected
            logging.getLogger().setLevel(logging.WARNING)

            # Start the MAC address change thread
            mac_thread = threading.Thread(target=change_mac_periodically, args=(interface, logger, interval_time))
            mac_thread.start()

            time.sleep(1)

            anonsurf_started = False
            openvpn_started = False
            wireguard_started = False
            vpn_thread = None

            # Prompt for starting WireGuard
            vpn_type = prompt_user_for_VPN()
            if vpn_type:
                if vpn_type == "anonsurf":
                    anonsurf_started = start_anonsurf(args.verbose, logger)
                elif vpn_type == "openvpn":
                    openvpn_started = start_openvpn(args.verbose, logger, interface)
                elif vpn_type == "wireguard":
                    wireguard_started = start_wireguard(args.verbose, logger, interface)

                # Start the WireGuard periodic change task if WireGuard was started
                vpn_thread = threading.Thread(target=change_vpn_periodically, args=(vpn_type, interface, logger, interval_time, initial_ip))
                vpn_thread.start()
            else:
                # Handle the case when WireGuard is not started
                logger.debug("Skipping WireGuard periodic change task.")

            # Start the countdown timer
            countdown_thread = threading.Thread(target=countdown, args=(interval_time,))
            countdown_thread.start()

            # Wait for both threads to complete
            mac_thread.join()
            if vpn_thread is not None and vpn_thread.is_alive():
                vpn_thread.join()
            countdown_thread.join()

        elif args.vpn_change:
            anonsurf_started = False
            openvpn_started = False
            wireguard_started = False
            vpn_thread = None
            vpn_type = ask_vpn_choice()
            if vpn_type:
                if vpn_type == "anonsurf":
                    anonsurf_started = start_anonsurf(args.verbose, logger)
                elif vpn_type == "openvpn":
                    openvpn_started = start_openvpn(args.verbose, logger, interface)
                elif vpn_type == "wireguard":
                    wireguard_started = start_wireguard(args.verbose, logger, interface)

            # Set logging level to WARNING or higher when -vc is selected
            logging.getLogger().setLevel(logging.WARNING)

            # Prompt for interval time if -vc is used
            interval_time = prompt_for_interval_time(default=300)
            vpn_thread = threading.Thread(target=change_vpn_periodically, args=(vpn_type, interface, logger, interval_time, initial_ip))
            vpn_thread.start()
            countdown_thread = threading.Thread(target=countdown, args=(interval_time,))
            countdown_thread.start()
            vpn_thread.join()
            countdown_thread.join()

        else:
            if args.random:
                new_mac = generate_mac_address(logger)
            elif args.mac:
                new_mac = args.mac
            else:
                logger.error("No MAC address specified. Use -r for random or -m to specify a MAC address.")
                sys.exit(1)

            if not is_valid_mac(new_mac, logger):
                logger.error(f"Invalid MAC address format: {new_mac}")
                sys.exit(1)

            # Ensure primary MAC is saved before changing MAC address
            if primary_mac is None:
                primary_mac = get_current_mac(interface, logger)
                if primary_mac:
                    save_primary_mac_to_file(interface, primary_mac, logger)
                else:
                    logger.error("Failed to retrieve current MAC address to save as primary.")
                    sys.exit(1)

            mac_changed = change_mac(interface, new_mac, logger)

            time.sleep(1)

            # Prompt for starting WireGuard
            anonsurf_started = False
            openvpn_started = False
            wireguard_started = False
            
            vpn_type = prompt_user_for_VPN()
            if vpn_type:
                if vpn_type == "anonsurf":
                    anonsurf_started = start_anonsurf(args.verbose, logger)
                elif vpn_type == "openvpn":
                    openvpn_started = start_openvpn(args.verbose, logger, interface)
                elif vpn_type == "wireguard":
                    wireguard_started = start_wireguard(args.verbose, logger, interface)

                # Check if the IP address has changed from the initial
                for _ in range(10):  # Retry up to 10 times
                    new_public_ip = get_public_ip(logger)
                    if new_public_ip and new_public_ip != initial_ip and is_valid_ip(new_public_ip):
                        try:
                            clear_line()
                            sys.stdout.write("\033[K") 
                            print(f"New public IP address: {new_public_ip}")
                            break  # Exit loop if the IP has changed successfully
                        except Exception as e:
                            logger.error(f"Error while printing new public IP: {e}")
                    else:
                        logger.debug(f"Current public IP is still the same as initial: {initial_ip}")
                    time.sleep(5)  # Wait and retry

                # After the loop, check if IP did not change
                if new_public_ip == initial_ip:
                    print(f"Your public IP did not change: {initial_ip}")
                    logger.debug("IP address did not change after starting WireGuard restart required.")

        if args.random or args.mac:
            print("Press CTRL+C to exit.", flush=True)  # Prevent new line after printing

        # Improved responsiveness loop
        while not stop_event.is_set():
            time.sleep(1)  # Keeps the script alive but responds to stop_event

    except KeyboardInterrupt:
        clear_line()
        logger.info("Keyboard interrupt received. Exiting...")
        sys.exit(1)
    finally:
        stop_event.set()  # Signal threads to stop
        print('\n')
        cleanup(interface, primary_mac, wireguard_started, openvpn_started, anonsurf_started, mac_changed, args.verbose, logger)
        print("\nAll settings have been restored to their default state.", flush=True)  # Prevent new line after printing

if __name__ == "__main__":
    main()
