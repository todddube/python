import os
import subprocess
import sys

def install_pyenv():
    # Install pyenv
    subprocess.check_call(['curl', '-L', 'https://pyenv.run', '|', 'bash'])

    # Add pyenv to shell
    shell_config = os.path.expanduser('~/.bashrc')
    with open(shell_config, 'a') as f:
        f.write('\n# Pyenv configuration\n')
        f.write('export PATH="$HOME/.pyenv/bin:$PATH"\n')
        f.write('eval "$(pyenv init --path)"\n')
        f.write('eval "$(pyenv init -)"\n')
        f.write('eval "$(pyenv virtualenv-init -)"\n')

    # Reload shell configuration
    subprocess.check_call(['source', shell_config], shell=True)

def create_and_activate_venv():
    # Create virtual environment
    subprocess.check_call([sys.executable, '-m', 'venv', 'venv'])

    # Activate virtual environment
    if os.name == 'nt':
        activate_script = os.path.join('venv', 'Scripts', 'activate.bat')
    else:
        activate_script = os.path.join('venv', 'bin', 'activate')

    print(f"Virtual environment created. To activate it, run:\nsource {activate_script}")

def validate_pyenv():
    # Validate pyenv installation
    try:
        subprocess.check_call(['pyenv', '--version'])
        print("pyenv is installed successfully.")
    except subprocess.CalledProcessError:
        print("pyenv installation failed.")

if __name__ == "__main__":
    install_pyenv()
    validate_pyenv()
    create_and_activate_venv()