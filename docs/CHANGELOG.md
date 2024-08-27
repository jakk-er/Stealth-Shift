# Changelog

## [1.0] - 2024-08-27
### Initial Release
- **Change MAC Address**: Implemented functionality to modify the MAC address of network interfaces using both `ifconfig` and `ip link` commands.
- **Generate Random MAC Address**: Added support for generating random MAC addresses with local administered bit set.
- **Save and Restore MAC Address**: Implemented saving and restoring of original MAC addresses to/from a file.
- **Start and Stop Anonsurf**: Integrated with Anonsurf to provide anonymity features.
- **Check Interface Status**: Added functionality to check and display the current status and MAC address of network interfaces.
- **Logging**: Added basic logging for actions and errors.
- **Command-Line Interface**: Implemented argument parsing for different functionalities.
