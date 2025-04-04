import datetime
import subprocess
import os
import sys
from datetime import datetime, timedelta  # Added timedelta to import

def list_installed_packages():
    result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--outdated', '--format=columns'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def upgrade_package(package_name):
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', package_name], check=True)
    except subprocess.CalledProcessError as e:
        with open('pip_upgrade_errors.log', 'a') as log_file:
            log_file.write(f"Failed to upgrade {package_name}: {e}\n")
        print(f"* Failed to upgrade {package_name}. Check upgrade_errors.log for details.")

def cleanup_old_files():
    """clean up old requirements files older than 14 days"""
    current_path = os.path.dirname(os.path.abspath(__file__))
    cutoff_date = datetime.now() - timedelta(days=14)  # Removed datetime. prefix
    
    for file in os.listdir(current_path):
        if file.startswith('requirements_'):
            file_path = os.path.join(current_path, file)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time < cutoff_date:
                try:
                    os.remove(file_path)
                    print(f"Removed old file: {file}")
                except OSError as e:
                    print(f"Error removing {file}: {e}")

def main():
    
    print(r"""
    ========================================================================
    Name:       pip_upgrade.py
    Purpose:    Upgrade all outdated pip packages and 
                makes dates requirements backup dated. 
    Written by: Todd Dube
    Date:       2025-04-04                                                                                                
    Version:    1.1 - Added error handling for package upgrades and logging
                1.0 - Initial version
    Notes:      This script will list all outdated packages,
                upgrade them, and create a backup of the current requirements.
                It will also clean up old requirements files older than 14 days.
                Make sure to run this script in a virtual environment or
                a controlled environment to avoid unintended upgrades.
    Usage:      python pip_upgrade.py
    Dependencies: pip, subprocess, os, sys, datetime
    ========================================================================
    """)
    # getting current path 
    current_path = os.path.dirname(os.path.abspath(__file__))
    # print(f"Current script path: {current_path}")
    
    print("Cleaning up old requirements files...")
    cleanup_old_files()
    
    # List outdated packages
    print("Listing outdated packages...")
    outdated_packages = list_installed_packages()
    
    # Write outdated packages to a file to use as a reference
    today = datetime.now().strftime('%Y-%m-%d')  # Correct usage
    output_file = current_path + f'/output/outdated_packages_{today}_{datetime.now().strftime("%H-%M-%S")}.txt'
    print(f"Writing outdated packages to {output_file}")
    with open(os.path.join(output_file), 'w') as file:
        file.write(outdated_packages)

    # Write requirements to a file
    requirements_file = current_path + f'/requirements_{today}_{datetime.now().strftime("%H-%M-%S")}.txt'
    with open(requirements_file, 'w') as file:
        subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=file)
    print(f"Requirements have been frozen to {requirements_file}")

    # Ask for confirmation before proceeding
    response = input("Do you want to proceed with upgrading packages? (y/n): ").lower()
    if response != 'y':
        print("Upgrade cancelled....")
        sys.exit(0)

    if outdated_packages:
        for line in outdated_packages.splitlines()[2:]:  # Skip header lines
            package_name = line.split()[0]
            print(f"Upgrading {package_name}...")
            upgrade_package(package_name)
            print(f"{package_name} upgraded successfully.")

if __name__ == "__main__":
    main()