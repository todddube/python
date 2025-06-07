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
if 'selected_requirements_file' not in st.session_state:
    st.session_state.selected_requirements_file = None
if 'requirements_files' not in st.session_state:
    st.session_state.requirements_files = []

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

def find_requirements_files():
    """Find all requirements files in the output directory and the workspace"""
    current_path = Path(os.path.dirname(os.path.abspath(__file__)))
    output_dir = current_path / 'output'
    output_dir.mkdir(exist_ok=True)
    
    # Find all requirements files in output directory
    req_files_output = list(output_dir.glob('requirements_*.txt'))
    
    # Find all requirements files in the workspace and parent directory
    workspace_files = list(current_path.glob('requirements*.txt'))
    parent_files = list(current_path.parent.glob('requirements*.txt'))
    
    # Combine all found files
    all_files = req_files_output + workspace_files + parent_files
    
    # Sort files by creation date extracted from filename if possible, otherwise by modification time
    def get_sort_key(file_path):
        # Try to extract date from filename (format: requirements_full_pip_2025-05-02_07-01-30.txt)
        filename = file_path.name
        try:
            # Extract date part from filename
            date_parts = [p for p in filename.split('_') if '-' in p]
            if date_parts and len(date_parts) >= 1:
                date_str = '_'.join(date_parts)
                # Try to parse the date
                try:
                    # For format YYYY-MM-DD_HH-MM-SS
                    if '-' in date_str:
                        date_str = date_str.replace('-', '').replace('_', '')
                        return datetime.strptime(date_str, '%Y%m%d%H%M%S')
                except ValueError:
                    pass
        except Exception:
            pass
            
        # Fallback to file modification time
        return datetime.fromtimestamp(file_path.stat().st_mtime)
    
    # Sort files by date (newest first)
    sorted_files = sorted(all_files, key=get_sort_key, reverse=True)
    
    return sorted_files

def install_from_requirements(file_path, package_manager="pip"):
    """Install packages from a requirements file
    
    Args:
        file_path: Path to requirements file
        package_manager: Either 'pip' or 'uv'
        
    Returns:
        Tuple of (success, output)
    """
    try:
        if package_manager == "uv":
            result = subprocess.run(['uv', 'pip', 'install', '-r', str(file_path)],
                                 capture_output=True, text=True)
        else:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(file_path)],
                                 capture_output=True, text=True)
        
        if result.returncode != 0:
            return False, result.stderr
        return True, result.stdout
    except subprocess.SubprocessError as e:
        return False, str(e)

def cleanup_old_files(days):
    """Clean up old requirements and package upgrade files
    Args:
        days: Number of days to keep files, defaults to 7. If 0, removes all files.
    """
    current_path = Path(os.path.dirname(os.path.abspath(__file__)))
    removed_files = []
    errors = []
    
    # Patterns to match both requirements and package upgrade logs
    patterns = [
        'output/requirements_*.txt',
        'output/package_upgrades_*.log'
    ]
    
    for pattern in patterns:
        for file in current_path.glob(pattern):
            # If days is 0, remove all files, otherwise check date
            if days == 0 or file.stat().st_mtime < (datetime.now() - timedelta(days=days)).timestamp():
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
    
    # Show welcome screen if no action selected
    if not st.session_state.last_action:
        st.subheader("👋 Welcome to Python Package Manager")
        
        # Feature tiles using columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📦 Package Management
            - List outdated packages
            - Upgrade selected packages
            - Create requirements.txt files
            """)
            
        with col2:
            st.markdown("""
            ### 📥 Requirements Installation
            - Install from requirements files
            - Sort requirements by date
            - Preview package contents
            """)
            
        st.info("👈 Select an action from the sidebar to get started!")

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
            
        # New option: Install from Requirements
        if st.button("📥 Install from Requirements"):
            st.session_state.last_action = "install_requirements"
            st.session_state.package_manager = package_manager
            # Find requirements files when this option is selected
            st.session_state.requirements_files = find_requirements_files()
                        
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

    elif st.session_state.last_action == "install_requirements":
        st.header("📥 Install from Requirements File")
        
        # Add a refresh button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Requirements Files")
        with col2:
            if st.button("🔄 Refresh List"):
                st.session_state.requirements_files = find_requirements_files()
                st.rerun()
        
        if not st.session_state.requirements_files:
            st.session_state.requirements_files = find_requirements_files()
            
        if not st.session_state.requirements_files:
            st.warning("No requirements files found in the workspace or output directory.")
        else:
            # Create a list of options with file paths and dates
            file_options = []
            for req_file in st.session_state.requirements_files:
                # Get file modification time
                mod_time = datetime.fromtimestamp(req_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                # Format display name
                display_name = f"{req_file.name} (Modified: {mod_time})"
                file_options.append((display_name, str(req_file)))
                
            # File source selection
            file_source = st.radio(
                "Source",
                ["Select from Found Files", "Enter Custom Path"],
                horizontal=True
            )
            
            if file_source == "Select from Found Files":
                # Create selectbox with formatted options
                selected_option = st.selectbox(
                    "Select Requirements File",
                    options=[name for name, _ in file_options],
                    index=0,
                    help="Choose a requirements file to install packages from"
                )
                
                # Get the actual file path for the selected option
                selected_file_path = next(path for name, path in file_options if name == selected_option)
            else:
                # Manual path entry
                custom_path = st.text_input(
                    "Enter Path to Requirements File",
                    placeholder="e.g., C:\\path\\to\\requirements.txt",
                    help="Enter the full path to a requirements file"
                )
                
                if custom_path:
                    selected_file_path = custom_path
                    # Check if file exists
                    if not os.path.exists(selected_file_path):
                        st.warning("⚠️ File does not exist. Please check the path.")
                        st.stop()
                else:
                    st.warning("Please enter a valid file path.")
                    st.stop()
            
            # Display file content preview
            with st.expander("Preview File Content"):
                try:
                    with open(selected_file_path, 'r') as f:
                        content = f.read()
                        if len(content) > 1000:
                            st.code(content[:1000] + "\n[...]", language="pip-requirements")
                            st.caption(f"Showing first 1000 characters of {len(content)} total")
                        else:
                            st.code(content, language="pip-requirements")
                            
                    # Count packages
                    package_count = len([line for line in content.splitlines() if line.strip() and not line.startswith('#')])
                    st.info(f"📦 File contains approximately {package_count} packages")
                except Exception as e:
                    st.error(f"Error reading file: {e}")
            
            # Install options
            col1, col2 = st.columns(2)
            with col1:
                install_btn = st.button(
                    f"Install with {st.session_state.package_manager.upper()}",
                    type="primary",
                    help=f"Install all packages from the selected file using {st.session_state.package_manager}"
                )
                
            with col2:
                ignore_errors = st.checkbox(
                    "Ignore Errors",
                    value=True,
                    help="Continue installation even if some packages fail"
                )
                
            if install_btn:
                with st.spinner(f"Installing packages from {os.path.basename(selected_file_path)}..."):
                    # Add --ignore-installed option if ignore_errors is checked
                    if ignore_errors:
                        # Create a temporary file with adjusted options
                        temp_dir = Path(os.path.dirname(os.path.abspath(__file__))) / 'output'
                        temp_dir.mkdir(exist_ok=True)
                        temp_file = temp_dir / f"temp_requirements_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
                        
                        try:
                            with open(selected_file_path, 'r') as src_file:
                                with open(temp_file, 'w') as dest_file:
                                    for line in src_file:
                                        dest_file.write(line)
                            
                            # Use the temp file for installation
                            success, output = install_from_requirements(temp_file, st.session_state.package_manager)
                            
                            # Clean up temp file
                            try:
                                temp_file.unlink()
                            except:
                                pass
                        except Exception as e:
                            success = False
                            output = str(e)
                    else:
                        # Install directly from the selected file
                        success, output = install_from_requirements(selected_file_path, st.session_state.package_manager)
                    
                    if success:
                        st.success("✅ Packages installed successfully!")
                    else:
                        st.error(f"❌ Error installing packages: {output}")
                    
                    # Display output
                    with st.expander("Installation Log"):
                        st.code(output)
                    
                    # Log the installation
                    log_path = log_upgrade_output("requirements_install", success, output, st.session_state.package_manager)
                    st.info(f"📝 Full installation log saved to: {log_path}")

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