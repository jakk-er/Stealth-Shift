# Changelog

## [2.0] - 2024-09-24
### Major Update
- **VPN Support**: Added support for OpenVPN and WireGuard VPN solutions.
- **Improved User Interface**: Enhanced the user interface for selecting VPN types.
- **VPN Change Option**: Introduced a new option to change the VPN at specified intervals.
- **Enhanced Logging**: Improved logging and error handling mechanisms for better troubleshooting.
- **Interface Wait Functionality**: Added a function to wait for the network interface to come up before proceeding.
- **Permissions Management**: Improved permissions settings for configuration files.
- **Stability Improvements**: Fixed several bugs to enhance overall stability.
- **New Scripts**:
  - **force_stop_vpn.py**: A script to force stop VPN connections.
  - **vpn_manager.py**: A script to manage VPN connections.
  - **config_manager.py**: A script to ensure configuration and authentication files are present and properly set up for VPN usage.
- **New Command-Line Options**:
  - `-rc` or `--random-change`: Changes both MAC address and selected VPN every specified interval.
  - `-vc` or `--vpn-change`: Changes selected VPN every specified interval (VPN only option).

## [1.0] - 2024-08-27
### Initial Release
- **Change MAC Address**: Implemented functionality to modify the MAC address of network interfaces using both `ifconfig` and `ip link` commands.
- **Generate Random MAC Address**: Added support for generating random MAC addresses with local administered bit set.
- **Save and Restore MAC Address**: Implemented saving and restoring of original MAC addresses to/from a file.
- **Start and Stop Anonsurf**: Integrated with Anonsurf to provide anonymity features.
- **Check Interface Status**: Added functionality to check and display the current status and MAC address of network interfaces.
- **Logging**: Added basic logging for actions and errors.
- **Command-Line Interface**: Implemented argument parsing for different functionalities.
