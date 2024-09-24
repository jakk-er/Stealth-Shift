# Stealth Shift

## Description
Stealth Shift is a Python script designed to change the MAC address of a network interface, manage MAC address changes, and interact with various VPN solutions, including Anonsurf, OpenVPN, and WireGuard, for enhanced anonymity. This tool provides the following functionalities:

- **Network Interface Validation**: Check the status and validity of network interfaces.
- **MAC Address Management**: Generate, validate, and change MAC addresses using `ioctl`, `ifconfig` or `ip link`.
- **Primary MAC Address Management**: Save and restore the primary MAC address.
- **VPN Control**: Start and stop VPN connections for traffic anonymization.
- **Status Display**: View the current status of network interfaces.

## Installation

### Prerequisites
Ensure you have Python installed on your system.

To use Stealth Shift, follow these steps:

1. **Clone the Repository**  
   Clone the repository to your local machine:
   ```bash
   git clone https://github.com/jakk-er/stealth-shift.git
   ```

2. **Install Dependencies**  
   Install the required libraries using:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Script**  
   Navigate to the directory where the script is located and execute it:
   ```bash
   python stealth_shift.py -i <interface> [options]
   ```

   Replace `<interface>` with the name of your network interface.

## Usage

### Command-Line Options
- `-i, --interface`: Specify the network interface to change the MAC address.
- `-m, --mac`: Set the MAC address to this value.
- `-r, --random`: Generate and set a random MAC address.
- `-p, --primary`: Set the MAC address to the primary MAC address stored in a file.
- `-s, --status`: Show the current status of the interface.
- `-v, --verbose`: Enable verbose output.
- `rc, --random-change`: Change both MAC address and selected VPN every specified interval.
- `vc, --vpn-change`: Change selected VPN every specified interval (VPN only option).

### Example Usage

- To change the MAC address of eth0 to a specific value:
   ```bash
   python stealth_shift.py -i eth0 -m 00:11:22:33:44:55
   ```
- To generate and set a random MAC address for wlan0:
   ```bash
   python stealth_shift.py -i wlan0 -r
   ```
- To set the MAC address to the primary address saved in a file for eth0:
   ```bash
   python stealth_shift.py -i eth0 -p
   ```
- To display the current MAC address and status of eth0:
   ```bash
   python stealth_shift.py -i eth0 -s
   ```
- To change both MAC address and selected VPN every specified interval:
   ```bash
   python stealth_shift.py -i eth0 -rc
   ```
- To change the selected VPN every specified interval (VPN only option):
   ```bash
   python stealth_shift.py -i eth0 -vc
   ```
## Data Storage
- The script saves the primary MAC address to a file named `<interface>_primary_mac.txt`.

## License

This work is licensed under a Creative Commons Attribution 4.0 International License. You must give appropriate credit, provide a link to the license, and indicate if changes were made. Details: [Creative Commons License](https://creativecommons.org/licenses/by/4.0/)

## Educational Use Only
This software is intended for educational purposes only. You agree to use the software solely for educational, research, or academic purposes, and not for any commercial or malicious activities.

## No Liability for Misuse
You acknowledge that you are solely responsible for any misuse of the software, including but not limited to using it to target websites or systems without their permission. The authors and copyright holders shall not be liable for any damages or claims arising from such misuse.

## Modification Restrictions
You may modify the software for your own educational purposes, but you agree not to compromise its integrity or security. Attribution must be maintained when redistributing or sharing modified versions.

## Author

jakk-er

## Version

2.0
