import subprocess
import sys
from datetime import date 

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

def main():
    
    print(r"""
    ========================================================================
    Name:       pip_upgrade.py
    Purpose:    Upgrade all outdated pip packages and 
                makes dates requirements backup dated. 
    Written by: Todd Dube
    Date:       2025-03-09                                                                                                   
    Version:    1.0.1
    ========================================================================
    """)
    print("Listing outdated packages...")
    outdated_packages = list_installed_packages()
    
    # write outdated packages to a file to use as a reference
    today = date.today().strftime('%Y-%m-%d')
    with open(f'outdated_packages_{today}.txt', 'w') as file:
        file.write(outdated_packages)
        subprocess.run(['code', f'outdated_packages_{today}.txt'])
    
    # Ask for confirmation before proceeding
    response = input("Do you want to proceed with upgrading packages? (y/n): ").lower()
    if response != 'y':
        print("Upgrade cancelled.")
        sys.exit(0)

    requirements_file = f"requirements_{today}.txt"
    with open(requirements_file, 'w') as file:
        subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=file)
    print(f"Requirements have been frozen to {requirements_file}")
 

    if outdated_packages:
        for line in outdated_packages.splitlines()[2:]:  # Skip header lines
            package_name = line.split()[0]
            print(f"Upgrading {package_name}...")
            upgrade_package(package_name)
            print(f"{package_name} upgraded successfully.")

if __name__ == "__main__":
    main()