# Stealth Shift

## Description
Stealth Shift is a script designed to change the MAC address of a network interface, manage MAC address changes, and integrate with Anonsurf for enhanced anonymity. This tool provides the following functionalities:

- Validate network interfaces
- Generate and validate MAC addresses
- Change the MAC address using `ifconfig` or `ip link`
- Save and restore the primary MAC address
- Start and stop Anonsurf for traffic anonymization
- Display the current status of the network interface

## Installation

To use Stealth Shift, follow these steps:

1. **Clone the Repository**  
   Clone the repository to your local machine:
   ```bash
   git clone https://github.com/jakk-er/stealth-shift.git
   ```

2. **Install Dependencies**  
   This script does not require external Python dependencies. Ensure you have Python installed on your system and that you have `ifconfig` and `ip` utilities available.

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

### Example Usage

- To change the MAC address of `eth0` to a specific value:
  ```bash
  python stealth_shift.py -i eth0 -m 00:11:22:33:44:55
  ```

- To generate and set a random MAC address for `wlan0`:
  ```bash
  python stealth_shift.py -i wlan0 -r
  ```

- To set the MAC address to the primary address saved in a file for `eth0`:
  ```bash
  python stealth_shift.py -i eth0 -p
  ```

- To display the current MAC address and status of `eth0`:
  ```bash
  python stealth_shift.py -i eth0 -s
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
You are permitted to modify the software for your own educational purposes, but you agree not to modify the software in a way that would compromise its integrity or security. You also agree not to remove or alter any copyright notices, trademarks, or other proprietary rights notices from the software.

When redistributing or sharing modified versions of the software, you must provide appropriate attribution, indicate if changes were made, and include a link to the original license.

## Author

jakk-er

## Version

1.0
