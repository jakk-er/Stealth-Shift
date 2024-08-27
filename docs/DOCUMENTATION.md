# Stealth Shift Documentation

**Overview**
-----------
Stealth Shift is a powerful network utility tool designed to manage and modify MAC addresses for network interfaces, with additional functionality for anonymity and interface status checks. The tool provides capabilities for:

- **Changing MAC Address**: Modify the MAC address of network interfaces.
- **Generating Random MAC Addresses**: Create random MAC addresses with local administered bit set.
- **Saving and Restoring MAC Addresses**: Store the original MAC address and restore it when needed.
- **Starting and Stopping Anonsurf**: Integrate with Anonsurf for enhanced anonymity.
- **Interface Status**: Check and verify the current status and MAC address of network interfaces.

**How it Works**
---------------
Stealth Shift uses various Python standard libraries and tools to perform its functions:
- **subprocess**: For executing system commands.
- **argparse**: For parsing command-line arguments.
- **logging**: For logging execution details and errors.
- **re**: For regular expressions to validate MAC addresses.
- **random**: For generating random MAC addresses.

**Features**
-------------------

### 1. **Change MAC Address**
Modifies the MAC address of a specified network interface. Supports both `ifconfig` and `ip link` commands.

### 2. **Generate Random MAC Address**
Creates a random MAC address suitable for use with the local administered bit set.

### 3. **Save and Restore MAC Address**
Saves the current MAC address to a file and restores it from the file when needed.

### 4. **Start and Stop Anonsurf**
Integrates with Anonsurf to start or stop the service for enhanced anonymity.

### 5. **Check Interface Status**
Displays the current status and MAC address of the specified network interface.

**Configuration Options**
-------------------------
Stealth Shift does not require additional configuration options. However, you may need to install and configure Anonsurf separately if you plan to use its functionality.

**Troubleshooting Tips**
-------------------------
### **Common Issues**
* **Permission Errors**: Ensure you have the necessary permissions to execute system commands. Use `sudo` where required.
* **Interface Not Found**: Verify the network interface name is correct and exists on your system.

### **Debugging**
Utilize verbose logging by adding the `-v` or `--verbose` option to get more detailed output for troubleshooting issues.

**Customization Possibilities**
-----------------------------
Possible customizations include:
* Adding support for more network interface commands.
* Enhancing the random MAC address generation algorithm.
* Integrating with additional anonymity tools or services.

**License and Disclaimer**
-------------------------
## License and Disclaimer

Stealth Shift is licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/legalcode).

This software is intended for educational purposes only. You agree to use the software solely for educational, research, or academic purposes, and not for any commercial or malicious activities.

You are free to:
- **Share** — copy and redistribute the material in any medium or format.
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
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

**Author**
---------
jakk-er

**Version**
----------
1.0
