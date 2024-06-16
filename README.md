# NetBackupAutomate

NetBackupAutomate is a Python-based network automation tool designed to automate the backup process of Cisco device configurations. It facilitates regular backups, manages local storage, and uploads backups to an FTP server for offsite storage.

## Features

- **Automated Backup**: Schedule and perform regular backups of Cisco device configurations.
- **FTP Upload**: Automatically upload backups to an FTP server for offsite storage.
- **Local Backup Management**: Manage local backups to ensure only the latest configurations are retained.
- **Device-specific Backup**: Each device stores its backups in a dedicated directory.
- **Empty Directory Cleanup**: Automatically removes empty directories after backup management.
- **Configuration Compliance**: Monitor and enforce compliance with network configuration policies.

## Requirements

- Python 3.x
- Required Python packages (`netmiko`, `pyyaml`, `colorama`): Install using `pip install -r requirements.txt`.
- Access to Cisco devices with SSH enabled.
- Access to an FTP server for remote backup storage.

## Installation

1. **Clone the repository**:
```sh
   git clone https://github.com/elshan-tahermanesh/NetBackupAutomate.git
   cd NetBackupAutomate
```

2. **Install required packages**:

```sh
pip install -r requirements.txt
```

3. **Configure config.yaml**:

- Copy **config.example.yaml** to **config.yaml**.
- Update **config.yaml** with your Cisco device and FTP server details.



# Usage

## Backup a Cisco Device

To backup the configuration of a Cisco device, run **setup.py** with the --device-name argument specifying the device name configured in **config.yaml**.

```sh
python setup.py --device-name "Router1"
```

## Automate Regular Backups

### Using Cron (Linux/macOS)

You can use cron to schedule regular backups. For example, to run the backup script every Sunday at midnight:

### 1. Open your crontab for editing:

```sh
crontab -e
```

### 2. Add the following line to schedule the backup:

```sh
# Run the backup script every Sunday at 2 AM
0 2 * * * /usr/bin/python3 /path/to/NetBackupAutomate/setup.py --device-name "Router1" >> /path/to/NetBackupAutomate/backup.log 2>&1
```

Replace **/usr/bin/python3** with the path to your Python executable if it differs, and **/path/to/NetBackupAutomate/** with the actual path to your **NetBackupAutomate** directory.

- 0 2 * * *: Runs the command at 2:00 AM every day.
- **/usr/bin/python3**: Path to the Python interpreter.
- **/path/to/NetBackupAutomate/setup.py**: Path to your backup script.
- **--device-name "Router1"**: Replace "Router1" with the actual device name.
- **/path/to/NetBackupAutomate/backup.log 2>&1**: Redirects output and errors to a log file for troubleshooting.

### Automate Regular Backups on Windows

On Windows, you can use Task Scheduler to automate the backup script:

1. Open Task Scheduler.
2. Create a new basic task.
3. Set the trigger to daily, and choose 2:00 AM as the time.
4. Set the action to start a program.
5. Choose python.exe as the program/script.
6. Add the script path and arguments (setup.py --device-name "Router1") in the "Add arguments" field.
7. Finish the setup and save the task.

## Manage Backups
The script manages local backups by storing them in **backups/<device_name>** directories. It ensures only the latest 30 backups are retained per device, preventing storage overflow.

## Upload to FTP Server
Backups are automatically uploaded to the FTP server specified in **config.yaml**. Ensure FTP server credentials and directory settings are correctly configured.

## Example config.yaml

```sh
devices:
  - name: Router1
    host: 192.168.1.1
    username: admin
    password: password
    device_type: cisco_ios

ftp:
  host: ftp.example.com
  username: ftpuser
  password: ftppassword
  directory: /backups
```

## Contributing
Contributions are welcome! If you have any ideas, improvements, or issues, please create an issue or pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

```sh

---

### Key Changes:

- **Cron Job Timing**: Updated the cron job line to run the backup at 2 AM every day.
- **Task Scheduler Instructions**: Changed the trigger time to 2:00 AM in the Windows Task Scheduler instructions.

This README.md now provides comprehensive guidance on setting up regular backups using cron and Windows Task Scheduler, including the specific schedule to run nightly at 2 AM.
```