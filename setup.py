import os
import argparse
import time
from datetime import datetime
from netmiko import ConnectHandler
from ftplib import FTP
import yaml
from collections import deque
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def load_config(config_file="config.yaml"):
    """Load configurations from a YAML file."""
    print(f"{Fore.CYAN}Loading configuration from {config_file}...")
    time.sleep(1)
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    print(f"{Fore.GREEN}Configuration loaded successfully.")
    time.sleep(1)
    return config

def upload_to_ftp(local_file, remote_file, ftp_config, device_name):
    """Upload a file to the FTP server in the device-specific directory."""
    print(f"{Fore.CYAN}Connecting to FTP server {ftp_config['host']}...")
    time.sleep(1)
    try:
        with FTP(ftp_config['host']) as ftp:
            ftp.login(ftp_config['username'], ftp_config['password'])
            print(f"{Fore.GREEN}Logged in to FTP server.")
            time.sleep(1)
            # Create and navigate to device-specific directory
            device_directory = f"{ftp_config['directory']}/{device_name}".replace("\\", "/")
            try:
                # Split the path and ensure each directory exists
                for part in device_directory.strip('/').split('/'):
                    if part not in ftp.nlst():
                        ftp.mkd(part)
                    ftp.cwd(part)
                print(f"{Fore.GREEN}Changed directory to {device_directory}.")
            except Exception as e:
                print(f"{Fore.RED}Failed to create or change directory to {device_directory}: {e}")
                return
            with open(local_file, "rb") as file:
                ftp.storbinary(f"STOR {remote_file}", file)
            print(f"{Fore.GREEN}Uploaded {local_file} to FTP server as {remote_file}.")
            time.sleep(1)
            # Delete local backup file after successful upload
            os.remove(local_file)
            print(f"{Fore.YELLOW}Deleted local backup file: {local_file}")
            time.sleep(1)
    except Exception as e:
        print(f"{Fore.RED}Failed to upload {local_file} to FTP server: {e}")
        time.sleep(1)

def manage_backups(backup_dir, device_name):
    """Ensure only the latest 30 backups are retained in device-specific directories and clean up empty directories."""
    print(f"{Fore.CYAN}Managing backups in {backup_dir} for device {device_name}...")
    time.sleep(1)
    device_backup_dir = os.path.join(backup_dir, device_name)
    os.makedirs(device_backup_dir, exist_ok=True)
    backups = deque()
    for filename in sorted(os.listdir(device_backup_dir)):
        if filename.endswith(".cfg"):
            backups.append(filename)
    while len(backups) > 30:
        oldest_backup = backups.popleft()
        os.remove(os.path.join(device_backup_dir, oldest_backup))
        print(f"{Fore.YELLOW}Deleted oldest backup: {oldest_backup}")
        time.sleep(1)
    # Check if the directory is empty and delete it if so
    if not os.listdir(device_backup_dir):
        os.rmdir(device_backup_dir)
        print(f"{Fore.YELLOW}Deleted empty backup directory: {device_backup_dir}")
        time.sleep(1)
    print(f"{Fore.GREEN}Backup management completed.")
    time.sleep(1)

def backup_device(device, ftp_config):
    """Backup the running configuration of a network device and upload to FTP."""
    print(f"{Fore.CYAN}Starting backup for device {device['name']}...")
    time.sleep(1)
    backup_dir = "backups"
    device_backup_dir = os.path.join(backup_dir, device['name'])
    os.makedirs(device_backup_dir, exist_ok=True)
    print(f"{Fore.GREEN}Backup directory '{device_backup_dir}' created or already exists.")
    time.sleep(1)

    # Generate timestamp with both date and time
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    backup_file = os.path.join(device_backup_dir, f"{device['name']}_{timestamp}.cfg")

    connection = None
    try:
        # Remove 'name' from the device dictionary for Netmiko
        device_connection = {key: device[key] for key in device if key != 'name'}
        print(f"{Fore.CYAN}Connecting to device {device['name']} at {device['host']}...")
        time.sleep(1)
        connection = ConnectHandler(**device_connection)
        connection.enable()
        print(f"{Fore.GREEN}Connected and enabled on device {device['name']}. Retrieving configuration...")
        time.sleep(1)
        config_data = connection.send_command("show running-config")
        with open(backup_file, "w") as file:
            file.write(config_data)
        print(f"{Fore.GREEN}Configuration saved to {backup_file}.")
        time.sleep(1)

        # Upload to FTP
        remote_file = f"{device['name']}_{timestamp}.cfg"
        print(f"{Fore.CYAN}Uploading backup to FTP server...")
        time.sleep(1)
        upload_to_ftp(backup_file, remote_file, ftp_config, device['name'])

        # Manage backups
        print(f"{Fore.CYAN}Managing local backups for device {device['name']}...")
        time.sleep(1)
        manage_backups(backup_dir, device['name'])

        # Check if the backups directory is empty and delete it if so
        if not os.listdir(backup_dir):
            os.rmdir(backup_dir)
            print(f"{Fore.YELLOW}Deleted empty backups directory: {backup_dir}")
            time.sleep(1)

    except Exception as e:
        print(f"{Fore.RED}Failed to backup {device['name']}: {e}")
        time.sleep(1)
    finally:
        if connection:
            print(f"{Fore.CYAN}Disconnecting from device {device['name']}...")
            time.sleep(1)
            connection.disconnect()
            print(f"{Fore.GREEN}Disconnected from device {device['name']}.")
            time.sleep(1)

def main(device_name):
    print(f"{Fore.CYAN}Starting backup process for device: {device_name}")
    time.sleep(1)
    config = load_config()
    ftp_config = config['ftp']
    device = next((device for device in config['devices'] if device['name'] == device_name), None)
    if device:
        backup_device(device, ftp_config)
    else:
        print(f"{Fore.RED}No configuration found for device: {device_name}")
        time.sleep(1)
    print(f"{Fore.GREEN}Backup process completed.")
    time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup Cisco device configurations and upload to FTP server")
    parser.add_argument("--device-name", required=True, help="Name of the device to backup")
    args = parser.parse_args()
    main(args.device_name)
