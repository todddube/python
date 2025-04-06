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

def upgrade_package_uv(package_name):
    """Upgrade a package using UV"""
    try:
        result = subprocess.run(['uv', 'pip', 'install', '--upgrade', package_name],
                              capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, str(e)

# Initialize session state
if 'last_action' not in st.session_state:
    st.session_state.last_action = None
if 'package_manager' not in st.session_state:
    st.session_state.package_manager = "pip"

def list_installed_packages():
    result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--outdated', '--format=columns'], 
                          stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def upgrade_package(package_name):
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', package_name], 
                              capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

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
    """Clean up old requirements files"""
    current_path = Path(os.path.dirname(os.path.abspath(__file__)))
    cutoff_date = datetime.now() - timedelta(days=days)
    removed_files = []
    errors = []
    
    for file in current_path.glob('output/requirements_*.txt'):
        if file.stat().st_mtime < cutoff_date.timestamp():
            try:
                file.unlink()
                removed_files.append(file.name)
            except OSError as e:
                errors.append(f"Error removing {file.name}: {e}")
    
    return removed_files, errors

def main():
    st.set_page_config(page_title="PIP Package Manager", page_icon="🐍", layout="wide")
    
    st.title("🐍 PIP Package Manager")
    st.write("Manage your Python packages with ease")

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
        cleanup_days = st.sidebar.slider("Cleanup Age (days)", 1, 30, 7)

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
        if st.session_state.package_manager == "uv":
            success, packages_output = list_installed_packages_uv()
            if not success:
                st.error(f"Error listing packages: {packages_output}")
                return
            packages = packages_output
        else:
            packages = list_installed_packages()

        if not packages.strip():
            st.success("No packages need upgrading!")
        else:
            outdated = [line.split()[0] for line in packages.splitlines()[2:]]
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, package in enumerate(outdated):
                status_text.text(f"Upgrading {package}...")
                if st.session_state.package_manager == "uv":
                    success, output = upgrade_package_uv(package)
                else:
                    success, output = upgrade_package(package)
                
                if success:
                    st.success(f"✅ Upgraded {package}")
                else:
                    st.error(f"❌ Failed to upgrade {package}: {output}")
                progress_bar.progress((i + 1) / len(outdated))
            
            status_text.text("Upgrade process completed!")

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