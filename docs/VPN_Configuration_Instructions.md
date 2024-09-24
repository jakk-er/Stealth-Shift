# VPN Configuration Instructions

Welcome to the VPN Configuration Setup! This document provides guidance on how to properly set up your configuration files to ensure the script runs smoothly.

## Important File Naming Format

To ensure the script operates correctly, it is essential that you follow the specific file naming format for your VPN configuration files. The script expects the following files in their respective directories:

### For OpenVPN Configuration Files
- **Directory**: `OP_VPNS`
- **File Naming Format**: `config-#.ovpn` (where `#` is a number from 1 to 10)
  - Example: `config-1.ovpn`, `config-2.ovpn`, etc.

### For Authentication Files
- **Directory**: `AUTH`
- **File Naming Format**: `auth-#.txt` (where `#` is a number from 1 to 10)
  - Example: `auth-1.txt`, `auth-2.txt`, etc.

### For WireGuard Configuration Files
- **Directory**: `WG_VPNS`
- **File Naming Format**: `config-#.conf` (where `#` is a number from 1 to 10)
  - Example: `config-1.conf`, `config-2.conf`, etc.

## Recommended Steps for Adding Your Own Configuration Content

1. **Open the Existing Template File**: 
   - We strongly recommend that you open one of the existing configuration files (e.g., `config-1.ovpn`, `auth-1.txt`, or `config-1.conf`) in a text editor.

2. **Copy and Paste the Content**:
   - Instead of creating a new file or copying an existing file, copy the content from the template and paste it into a new file. 
   - This helps avoid issues with file naming that could disrupt the script.

3. **Modify the Content**:
   - Adjust the necessary settings in your new file according to your VPN provider's requirements. Make sure to update any lines related to authentication as needed.

4. **Save the File**:
   - Save your new file using the correct naming format. For example, if you are creating a new OpenVPN configuration file, name it `config-2.ovpn` if `config-1.ovpn` already exists.

## Troubleshooting

If you encounter any issues when running the script:
- Ensure all required directories (`OP_VPNS`, `AUTH`, `WG_VPNS`) exist.
- Verify that all expected files are present and named correctly.
- If you receive an error message, check the file paths and names for typos or inconsistencies.

By following these instructions, you can avoid potential issues and ensure a smooth setup of your VPN configuration.

If you have further questions or require assistance, please feel free to reach out!
