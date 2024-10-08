# Stealth Shift Documentation

**Overview**
-----------
Stealth Shift is a powerful network utility tool designed to manage and modify MAC addresses for network interfaces, with enhanced functionality for VPN management and anonymity. The tool provides capabilities for:

- **Changing MAC Address**: Modify the MAC address of network interfaces.
- **Generating Random MAC Addresses**: Create random MAC addresses with the local administered bit set.
- **Saving and Restoring MAC Addresses**: Store the original MAC address and restore it when needed.
- **Managing VPN Connections**: Start, stop, and switch between various VPN solutions (Anonsurf, OpenVPN, WireGuard) at specified intervals.
- **Countdown Timer**: Utilize a countdown timer during MAC and VPN changes for better scheduling.
- **Interface Status**: Check and verify the current status and MAC address of network interfaces.

**How it Works**
---------------
Stealth Shift uses various Python standard libraries and tools to perform its functions:

- **subprocess**: For executing system commands.
- **argparse**: For parsing command-line arguments.
- **logging**: For logging execution details and errors.
- **re**: For regular expressions to validate MAC addresses.
- **random**: For generating random MAC addresses.
- **requests**: For fetching public IP addresses.
- **threading**: For managing concurrent operations, such as the countdown timer.

**Features**
-------------------
1. **Change MAC Address**: 
   Modifies the MAC address of a specified network interface. Supports both `ifconfig` and `ip link` commands.

2. **Generate Random MAC Address**: 
   Creates a random MAC address suitable for use with the local administered bit set.

3. **Save and Restore MAC Address**: 
   Saves the current MAC address to a file and restores it from the file when needed.

4. **Manage VPN Connections**: 
   - **Start and Stop VPN**: Integrate with Anonsurf, OpenVPN, and WireGuard to manage VPN connections.
   - **Switch VPNs**: Change VPNs at specified intervals to enhance anonymity.

5. **Countdown Timer**: 
   Use a countdown timer to schedule MAC address and VPN changes effectively.

6. **Check Interface Status**: 
   Displays the current status and MAC address of the specified network interface.

**Configuration Options**
-------------------------
Stealth Shift does not require additional configuration options. However, you may need to install and configure Anonsurf, OpenVPN, or WireGuard separately if you plan to use their functionality. Ensure you have the necessary permissions (e.g., running with `sudo`) for modifying network settings.

**Troubleshooting Tips**
-------------------------
### Common Issues
- **Permission Errors**: Ensure you have the necessary permissions to execute system commands. Use `sudo` where required.
- **Interface Not Found**: Verify the network interface name is correct and exists on your system.
- **VPN Connection Issues**: Ensure that your VPN configurations are set up correctly and that you have the necessary credentials.
- **Primary MAC Address Issues**: If the primary MAC address file does not exist or cannot be read, ensure that you have previously saved a MAC address.

### Debugging
Utilize verbose logging by adding the `-v` or `--verbose` option to get more detailed output for troubleshooting issues.

**Customization Possibilities**
-----------------------------
Possible customizations include:
- Adding support for more VPN solutions.
- Enhancing the random MAC address generation algorithm.
- Integrating with additional anonymity tools or services.
- Allowing user-defined intervals for VPN changes.
- Expanding the logging system for better diagnostics.

**License and Disclaimer**
-------------------------
Stealth Shift is licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/legalcode).

This software is intended for educational purposes only. You agree to use the software solely for educational, research, or academic purposes, and not for any commercial or malicious activities.

You are free to:
- **Share** — copy and redistribute the material in any medium or format.
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **No additional restrictions** — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

You acknowledge that you are solely responsible for any misuse of the software, including but not limited to using it to target networks or systems without their permission. The authors and copyright holders shall not be liable for any damages or claims arising from such misuse.

**Dependencies**
----------------
Stealth Shift relies on the following Python standard libraries:
- `argparse`
- `logging`
- `os`
- `re`
- `string`
- `subprocess`
- `sys`
- `time`
- `random`
- `threading`
- `requests`
- `socket`
- `struct`
- `fcntl`
- `signal`
- `shutil`

**Author**
---------
**jakk-er**

**Version**
----------
**2.0**
