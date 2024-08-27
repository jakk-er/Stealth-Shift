import argparse
import logging
import os
import re
import string
import subprocess
import sys
import time
import random
from banner import display_banner

def is_valid_interface(interface):
    """Check if the interface name is valid."""
    valid_prefixes = ['eth', 'wlan']
    return any(interface.startswith(prefix) for prefix in valid_prefixes) and all(c in string.ascii_letters + string.digits + ':-.' for c in interface)

def configure_logging(verbose):
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

def interface_exists(interface, logger):
    """Check if the network interface exists."""
    try:
        logger.debug(f"Checking if interface {interface} exists using 'ifconfig'")
        subprocess.check_output(["ifconfig", interface], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        logger.debug(f"Interface {interface} does not exist.")
        return False

def generate_mac_address(logger):
    """Generate a new MAC address with a local administered bit set."""
    mac = [random.randint(0x02, 0x02)] + [random.randint(0x00, 0xff) for _ in range(5)]
    mac_hex = [f"{x:02x}" for x in mac]
    random_mac = ':'.join(mac_hex)
    logger.debug(f"Generated MAC address: {random_mac}")
    return random_mac

def is_valid_mac(mac_address, logger):
    """Validate the MAC address format."""
    valid = bool(re.fullmatch(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", mac_address))
    if not valid:
        logger.debug(f"Invalid MAC address format: {mac_address}. Expected format: XX:XX:XX:XX:XX:XX")
    return valid

def get_current_mac(interface, logger):
    """Retrieve the current MAC address of the specified interface."""
    try:
        logger.debug(f"Getting current MAC address for {interface} using 'ifconfig'")
        ifconfig_result = subprocess.check_output(["ifconfig", interface]).decode('utf-8')
        mac_address_search_result = re.search(r"(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)", ifconfig_result)
    except subprocess.CalledProcessError:
        logger.error(f"Could not retrieve MAC address for {interface}")
        return None

    if mac_address_search_result:
        current_mac = mac_address_search_result.group(0)
        logger.debug(f"Current MAC address: {current_mac}")
        return current_mac
    else:
        logger.error("Could not read MAC address")
        return None

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

def bring_interface_down_and_up(interface, new_mac, logger):
    """Bring the interface down, change MAC address, and bring it up."""
    commands = [
        ["sudo", "ifconfig", interface, "down"],
        ["sudo", "ifconfig", interface, "hw", "ether", new_mac],
        ["sudo", "ifconfig", interface, "up"]
    ]
    execute_commands(commands, logger)

def bring_interface_down_and_up_ip(interface, new_mac, logger):
    """Bring the interface down, change MAC address, and bring it up using 'ip link'."""
    commands = [
        ["sudo", "ip", "link", "set", "dev", interface, "down"],
        ["sudo", "ip", "link", "set", "dev", interface, "address", new_mac],
        ["sudo", "ip", "link", "set", "dev", interface, "up"]
    ]
    execute_commands(commands, logger)

def change_mac(interface, new_mac, logger):
    """Change the MAC address of the specified interface."""
    try:
        logger.debug(f"Attempting to change MAC address for {interface} to {new_mac} using 'ifconfig'")
        bring_interface_down_and_up(interface, new_mac, logger)
        logger.info(f"MAC address successfully changed to {new_mac} using 'ifconfig'")
        return True
    except Exception:
        logger.warning(f"Failed to change MAC address using 'ifconfig'. Trying 'ip link'...")
        try:
            bring_interface_down_and_up_ip(interface, new_mac, logger)
            logger.info(f"MAC address successfully changed to {new_mac} using 'ip link'")
            return True
        except Exception as e:
            logger.error(f"Error changing MAC address using 'ip link': {e}")
            return False

def save_primary_mac_to_file(interface, primary_mac, logger):
    """Save the primary MAC address to a file."""
    filename = f"{interface}_primary_mac.txt"
    try:
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
        logger.info(f"Primary MAC address read from file for {interface}")
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
            logger.info(f"MAC address successfully set to {primary_mac} for {interface}")
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

def cleanup(interface, primary_mac, anonsurf_started, mac_changed, verbose, logger):
    """Cleanup actions including restoring primary MAC address and stopping Anonsurf."""
    logger.debug("Cleaning up...")

    # Bring the interface back up if it was down
    try:
        logger.debug(f"Checking if interface {interface} is up.")
        ifconfig_result = subprocess.check_output(["ifconfig", interface]).decode('utf-8')
        if "UP" not in ifconfig_result:
            logger.info(f"Interface {interface} is down. Bringing it back up.")
            subprocess.run(["sudo", "ifconfig", interface, "up"], check=True)

        # Compare the current MAC address with the primary MAC address
        current_mac = get_current_mac(interface, logger)
        if current_mac != primary_mac:
            logger.info(f"Current MAC address ({current_mac}) does not match primary MAC address ({primary_mac}). Restoring primary MAC address.")
            if not set_primary_mac(interface, primary_mac, logger):
                logger.error("Failed to restore the primary MAC address.")
        else:
            logger.debug(f"Current MAC address matches the primary MAC address ({primary_mac}).")

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to check or bring up interface {interface}: {e}")

    # Stop Anonsurf if it was started
    if anonsurf_started:
        stop_anonsurf(verbose, logger)

def prompt_user_for_sudo():
    """Prompt the user to enter their password for sudo operations."""
    print("This script requires elevated privileges to change the MAC address.")
    try:
        input("Press Enter to continue...")
    except KeyboardInterrupt:
        print("\nOperation cancelled by the user. Exiting...")
        sys.exit(1)

def prompt_user_for_anonsurf():
    """Prompt user to start Anonsurf with a maximum of 3 attempts."""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            start_anonsurf_prompt = input("Do you want to start Anonsurf? (yes/y/no/n): ").strip().lower()
            if start_anonsurf_prompt in ['yes', 'y']:
                return True
            elif start_anonsurf_prompt in ['no', 'n']:
                return False
            else:
                print("Invalid input. Please enter 'yes', 'y', 'no', or 'n'.")
        except (KeyboardInterrupt, EOFError):
            print("\nInput interrupted. Exiting...")
            sys.exit(1)
    
    print("Maximum attempts reached. Exiting...")
    sys.exit(1)

def get_arguments():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        usage="python %(prog)s -i <interface> [options]",
        description=(
            "Change MAC addresses and enhance anonymity with Anonsurf.\n"
            "Manage your network interface’s MAC address and anonymize your traffic."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Anonsurf Options:\n"
            "  When using -r/--random or -m/--mac options, you will be prompted to use Anonsurf.\n"
            "  Anonsurf is a tool to anonymize your network traffic by routing it through the Tor network.\n"
            "  Choose 'yes' to start Anonsurf, and 'no' to proceed without it.\n"
        )
    )
    parser.add_argument("-i", "--interface", required=True, help="The network interface to change MAC address")
    parser.add_argument("-m", "--mac", help="Set the MAC address to this value")
    parser.add_argument("-r", "--random", action="store_true", help="Set a random MAC address")
    parser.add_argument("-p", "--primary", action="store_true", help="Set the MAC address to primary (from file)")
    parser.add_argument("-s", "--status", action="store_true", help="Show current status of the interface")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    return parser.parse_args()

def main():
    """Main function to handle arguments and execute the script logic."""
    args = get_arguments()
    logger = configure_logging(args.verbose)
    interface = args.interface

    display_banner()

    # Prompt for sudo access before performing any privileged operations
    prompt_user_for_sudo()

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

    if primary_mac is None:
        primary_mac = get_current_mac(interface, logger)
        if primary_mac:
            save_primary_mac_to_file(interface, primary_mac, logger)
        else:
            logger.error("Failed to retrieve current MAC address to save as primary.")
            sys.exit(1)

    mac_changed = False
    anonsurf_started = False
    try:
        mac_changed = change_mac(interface, new_mac, logger)
        if prompt_user_for_anonsurf():
            anonsurf_started = start_anonsurf(args.verbose, logger)
        
        logger.debug("Script is running. Press CTRL+C to exit.")
        print("Press CTRL+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Exiting...")
    finally:
        if os.path.isfile(f"{interface}_primary_mac.txt"):
            cleanup(interface, primary_mac, anonsurf_started, mac_changed, args.verbose, logger)

if __name__ == "__main__":
    main()
