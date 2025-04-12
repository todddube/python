import streamlit as st
import subprocess
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

# Add after imports
def check_uv_installed():
    """Check if UV is installed"""
    try:
        subprocess.run(['uv', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_uv():
    """Install UV using pip"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'uv'], 
                      capture_output=True, check=True)
        return True, "UV installed successfully"
    except subprocess.CalledProcessError as e:
        return False, str(e)

def list_installed_packages_uv():
    """List outdated packages using UV"""
    try:
        result = subprocess.run(['uv', 'pip', 'list', '--outdated'], 
                              capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, str(e)

def upgrade_package(package_name: str, package_manager: str = "pip") -> tuple[bool, str]:
    """
    Upgrade a package using the specified package manager
    Args:
        package_name: Name of the package to upgrade
        package_manager: Either 'pip' or 'uv'
    Returns:
        Tuple of (success, message)
    """
    try:
        if package_manager == "uv":
            result = subprocess.run(['uv', 'pip', 'install', '--upgrade', package_name],
                                 capture_output=True, text=True, check=True)
        else:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', package_name],
                                 capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, str(e)

def log_upgrade_output(package_name: str, success: bool, output: str, package_manager: str):
    """Log upgrade output to a single combined log file"""
    current_path = Path(os.path.dirname(os.path.abspath(__file__)))
    output_dir = current_path / 'output'
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    # Use a single log file for all output
    log_file = output_dir / f'package_upgrades_{package_manager}_{package_name}_{timestamp}.log'
    
    # Format the log entry with clear separation and status indicators
    log_entry = f"""
        {'='*80}
        📦 Package: {package_name}
        ⏰ Timestamp: {timestamp}
        ✔️ Status: {'SUCCESS' if success else '❌ FAILED'}
        {'‾'*50}
        Output:
        {output}
        {'_'*80}
        """
    
    # Append the log entry to the file
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    
    return str(log_file)

# Initialize session state
if 'last_action' not in st.session_state:
    st.session_state.last_action = None
if 'package_manager' not in st.session_state:
    st.session_state.package_manager = "pip"

def list_installed_packages():
    result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--outdated', '--format=columns'], 
                          stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def create_requirements():
    """Create a full requirements.txt file based on selected package manager"""
    current_path = Path(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_dir = current_path / 'output'
    output_dir.mkdir(exist_ok=True)
    
    requirements_file = output_dir / f'requirements_full_{st.session_state.package_manager}_{today}.txt'
    
    try:
        if st.session_state.package_manager == "uv":
            result = subprocess.run(['uv', 'pip', 'freeze'], 
                                 capture_output=True, text=True, check=True)
            with open(requirements_file, 'w') as file:
                file.write(result.stdout)
        else:
            with open(requirements_file, 'w') as file:
                subprocess.run([sys.executable, '-m', 'pip', 'freeze'], 
                             stdout=file, check=True)
        return True, str(requirements_file)
    except subprocess.CalledProcessError as e:
        return False, str(e)

def cleanup_old_files(days=7):
    """Clean up old requirements and package upgrade files"""
    current_path = Path(os.path.dirname(os.path.abspath(__file__)))
    cutoff_date = datetime.now() - timedelta(days=days)
    removed_files = []
    errors = []
    
    # Patterns to match both requirements and package upgrade logs
    patterns = [
        'output/requirements_*.txt',
        'output/package_upgrades_*.log'
    ]
    
    for pattern in patterns:
        for file in current_path.glob(pattern):
            if file.stat().st_mtime < cutoff_date.timestamp():
                try:
                    file.unlink()
                    removed_files.append(file.name)
                except OSError as e:
                    errors.append(f"Error removing {file.name}: {e}")
    
    return removed_files, errors

def main():
    st.set_page_config(page_title="PIP Package Manager", page_icon="🐍", layout="wide")
    
    st.title("🐍 Python Package Manager")
    st.write("Manage your Python packages with ease picking between pip and uv.")

    # Sidebar for actions
    with st.sidebar:
        st.header("Actions")
        
        # Add UV section
        st.subheader("📦 Package Manager")
        package_manager = st.radio("Select Package Manager", ["pip", "uv"])
        
        if package_manager == "uv" and not check_uv_installed():
            if st.button("Install UV"):
                with st.spinner("Installing UV..."):
                    success, message = install_uv()
                    if success:
                        st.success("UV installed successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to install UV: {message}")
        
        # Modified buttons to handle both pip and uv
        if st.button("📦 List Outdated Packages"):
            st.session_state.last_action = "list"
            st.session_state.package_manager = package_manager

        if st.button("📄 Create Requirements File"):
            st.session_state.last_action = "requirements"
            st.session_state.package_manager = package_manager
            
        if st.button("⬆️ Upgrade All Packages"):
            st.session_state.last_action = "upgrade"
            st.session_state.package_manager = package_manager
                        
        if st.button("🧹 Cleanup Old Files"):
            st.session_state.last_action = "cleanup"
        
        # Cleanup days settings
        st.sidebar.markdown("---")
        cleanup_option = st.sidebar.radio("Cleanup Option", ["By Age", "All Files"])
        if cleanup_option == "By Age":
            cleanup_days = st.sidebar.slider("Cleanup Age (days)", 1, 30, 7)
        else:
            cleanup_days = 0  # Will remove all files when set to 0

    # Main content area
    if st.session_state.last_action == "list":
        st.header(f"📦 Outdated Packages ({st.session_state.package_manager.upper()})")
        with st.spinner(f"Checking for outdated packages using {st.session_state.package_manager.upper()}..."):
            if st.session_state.package_manager == "uv":
                success, packages_output = list_installed_packages_uv()
                if not success:
                    st.error(f"Error listing packages: {packages_output}")
                    return
                packages = packages_output
            else:
                packages = list_installed_packages()

            if packages.strip():
                lines = packages.strip().split('\n')
                headers = lines[0].split()
                data = [line.split() for line in lines[2:]]
                
                if data:
                    df = pd.DataFrame(data, columns=headers)
                    st.dataframe(df, use_container_width=True)
                    st.download_button(
                        "Download as CSV",
                        df.to_csv(index=False).encode('utf-8'),
                        "outdated_packages.csv",
                        "text/csv"
                    )
            else:
                st.success("No outdated packages found!")

    elif st.session_state.last_action == "upgrade":
        st.header("⬆️ Package Upgrade")
        package_manager = st.session_state.package_manager
        
        # Get list of outdated packages
        if package_manager == "uv":
            success, packages_output = list_installed_packages_uv()
            if not success:
                st.error(f"Error listing packages: {packages_output}")
                return
        else:
            packages_output = list_installed_packages()

        if not packages_output.strip():
            st.success("No packages need upgrading!")
            return

        # Parse package list
        outdated = [line.split()[0] for line in packages_output.splitlines()[2:]]
        
        # Allow package selection
        selected_packages = st.multiselect(
            "Select packages to upgrade",
            options=outdated,
            default=outdated,
            help="Choose specific packages or leave all selected to upgrade everything"
        )

        if not selected_packages:
            st.warning("Please select at least one package to upgrade")
            return

        if st.button(f"Upgrade {len(selected_packages)} Selected Packages"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, package in enumerate(selected_packages):
                status_text.text(f"Upgrading {package}...")
                success, output = upgrade_package(package, package_manager)
                
                # Log output and errors
                log_file = log_upgrade_output(package, success, output, package_manager)
                
                if success:
                    st.success(f"✅ Upgraded {package}")
                else:
                    st.error(f"❌ Failed to upgrade {package}: {output}")
                progress_bar.progress((i + 1) / len(selected_packages))
                
            status_text.text("Upgrade process completed!")
            
            # Show log file location
            st.info(f"Detailed upgrade log can be found at:\n"
                   f"📝 {log_file}")
            
            # Refresh package list after upgrades
            st.rerun()

    elif st.session_state.last_action == "requirements":
        st.header("📄 Requirements File")
        success, result = create_requirements()
        if success:
            st.success(f"Requirements file created at: {result}")
        else:
            st.error(f"Failed to create requirements file: {result}")

    elif st.session_state.last_action == "cleanup":
        st.header("🧹 Cleanup")
        removed_files, errors = cleanup_old_files(cleanup_days)
        
        if removed_files:
            st.success(f"Removed {len(removed_files)} old files")
            with st.expander("Show removed files"):
                for file in removed_files:
                    st.write(f"- {file}")
        else:
            st.info("No files needed cleanup")
            
        if errors:
            st.error("Some errors occurred during cleanup")
            with st.expander("Show errors"):
                for error in errors:
                    st.write(f"- {error}")

if __name__ == "__main__":
    main()