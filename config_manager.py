import os
import shutil
import sys
from banner import display_banner

def log_message(message, verbose):
    """Function to log messages. Modify this to change logging behavior."""
    if verbose:
        print(message)

def get_next_available_file(directory, prefix, extension):
    """Find the next available file in the specified directory."""
    for i in range(1, 11):
        filename = f"{prefix}-{i}{extension}"
        if os.path.isfile(os.path.join(directory, filename)):
            return os.path.join(directory, filename)
    return None

def ensure_config_files_and_auth(directory, auth_directory, wg_directory, verbose=False):
    try:
        # Ensure the directories exist
        os.makedirs(directory, exist_ok=True)
        os.makedirs(auth_directory, exist_ok=True)
        os.makedirs(wg_directory, exist_ok=True)

        # Get all config files in the OpenVPN directory
        existing_configs = [f for f in os.listdir(directory) if f.endswith('.ovpn')]
        existing_auths = [f for f in os.listdir(auth_directory) if f.endswith('.txt')]
        existing_wg_configs = [f for f in os.listdir(wg_directory) if f.endswith('.conf')]

        # Create sets of expected filenames
        expected_configs = {f"config-{i}.ovpn" for i in range(1, 11)}
        expected_auths = {f"auth-{i}.txt" for i in range(1, 11)}
        expected_wg_configs = {f"config-{i}.conf" for i in range(1, 11)}

        # Identify missing files
        missing_configs = expected_configs - set(existing_configs)
        missing_auths = expected_auths - set(existing_auths)
        missing_wg_configs = expected_wg_configs - set(existing_wg_configs)

        processed_auths = set()  # Track processed authentication files

        # Handle missing VPN config files
        if missing_configs:
            for missing_config in missing_configs:
                missing_config_path = os.path.join(directory, missing_config)

                # Get the next available reference config file
                reference_config_path = get_next_available_file(directory, "config", ".ovpn")
                if reference_config_path is None:
                    log_message("No reference configuration file available.", verbose)
                    continue

                # Read the contents of the reference config file
                with open(reference_config_path, 'r') as ref_file:
                    content = ref_file.readlines()

                # Modify the line for auth-user-pass
                auth_index = missing_config.split('-')[1].split('.')[0]  # Get the index
                new_auth_line = f"auth-user-pass AUTH/auth-{auth_index}.txt\n"

                # Write the modified content to the new config file
                with open(missing_config_path, 'w') as new_file:
                    for line in content:
                        if line.startswith("auth-user-pass"):
                            new_file.write(new_auth_line)  # Write the modified line
                        else:
                            new_file.write(line)  # Write the original line

                log_message(f"Added missing VPN configuration file: {missing_config}", verbose)

                # Force copy the corresponding auth file if not already processed
                target_auth_path = os.path.join(auth_directory, f"auth-{auth_index}.txt")
                if target_auth_path not in processed_auths:
                    if auth_index != "1":
                        auth_reference_path = get_next_available_file(auth_directory, "auth", ".txt")
                    else:
                        auth_reference_path = os.path.join(auth_directory, "auth-1.txt")

                    # Avoid copying to the same file
                    if auth_reference_path and auth_reference_path != target_auth_path:
                        shutil.copyfile(auth_reference_path, target_auth_path)
                        log_message(f"Copied authentication file for {missing_config}: auth-{auth_index}.txt", verbose)
                        processed_auths.add(target_auth_path)  # Mark this auth file as processed
                    else:
                        log_message(f"No suitable authentication file found for {missing_config} or trying to copy to the same file.", verbose)

        # Handle missing auth files only if they haven't been processed
        if missing_auths:
            for missing_auth in missing_auths:
                missing_auth_path = os.path.join(auth_directory, missing_auth)
                if missing_auth_path not in processed_auths:  # Check if already processed
                    reference_auth_path = get_next_available_file(auth_directory, "auth", ".txt")
                    if reference_auth_path is None:
                        log_message("No reference authentication file available.", verbose)
                        continue

                    shutil.copyfile(reference_auth_path, missing_auth_path)
                    log_message(f"Added missing authentication file: {missing_auth}", verbose)
                    processed_auths.add(missing_auth_path)  # Mark as processed

        # Handle missing WireGuard config files
        if missing_wg_configs:
            for missing_wg_config in missing_wg_configs:
                missing_wg_config_path = os.path.join(wg_directory, missing_wg_config)

                # Get the next available reference WireGuard config file
                reference_wg_config_path = get_next_available_file(wg_directory, "config", ".conf")
                if reference_wg_config_path is None:
                    log_message("No reference WireGuard configuration file available.", verbose)
                    continue

                shutil.copyfile(reference_wg_config_path, missing_wg_config_path)
                log_message(f"Added missing WireGuard configuration file: {missing_wg_config}", verbose)

        # Check if everything is satisfied
        if not (missing_configs or missing_auths or missing_wg_configs):
            log_message("All required files and directories have been successfully verified and are present.", verbose)

    except FileNotFoundError:
        log_message(f"Oops! It looks like the directory '{directory}', '{auth_directory}', or '{wg_directory}' is missing. "
                    "Please ensure you have all essential files and folders.", verbose)
        exit(1)
    except Exception as e:
        log_message(f"An unexpected error occurred: {e}", verbose)

if __name__ == "__main__":
    display_banner()
    ensure_config_files_and_auth('OP_VPNS', 'AUTH', 'WG_VPNS', verbose=True)
