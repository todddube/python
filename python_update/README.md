# Python Packages App

A Streamlit-based application for managing Python packages, upgrading outdated packages, and installing from requirements files.

## Features

- 📦 **Package Management**: List and upgrade outdated packages using pip or UV
- 📄 **Requirements Installation**: Find, preview, and install from requirements files
- 🧹 **Cleanup Utilities**: Remove old package files and logs
- ⚡ **UV Support**: Fast package management with UV package manager
- 📊 **Progress Tracking**: Real-time installation progress and logs

## 🚀 Quick Start with UV Virtual Environment

**NEW**: The app now includes a pre-configured UV virtual environment for optimal performance!

### Windows
```bash
# Run with UV environment (Recommended)
run_python_packages_app.bat

# Or use PowerShell
.\run_python_packages_app.ps1
```

### Manual UV Environment
```bash
# Activate the UV environment
python_packages_env\Scripts\activate

# Run the app
streamlit run python_packages_app.py
```

### Linux/Mac
```bash
chmod +x run_app.sh
./run_app.sh
```

### Manual Setup
```bash
# Install dependencies
python setup.py

# Run the app
streamlit run python_packages_app.py
```

## Requirements

- Python 3.8+
- pip (Python package installer)
- Streamlit 1.32.0+
- pandas 2.0.0+

## Usage

1. **Package Management**:
   - Click "📋 List Outdated Packages" to see packages that need updating
   - Select packages to upgrade individually or in bulk
   - Choose between pip and UV package managers

2. **Requirements Installation**:
   - Click "📥 Install from Requirements" to find requirements files
   - Preview file contents before installation
   - Install packages from selected requirements file

3. **Cleanup**:
   - Click "🧹 Cleanup Old Files" to remove temporary files
   - Configure cleanup age (days) in sidebar

## Package Managers

### pip (Default)
- Standard Python package manager
- Widely compatible
- Slower installation

### UV (Optional)
- Fast Rust-based package manager
- Drop-in replacement for pip
- Requires separate installation: `pip install uv`

## 🛠️ UV Virtual Environment

The app now includes a pre-configured UV virtual environment with all dependencies:
- **Location**: `python_packages_env/`
- **Python Version**: 3.13.3
- **Package Manager**: UV 0.7.12
- **Pre-installed Packages**: streamlit, pandas, uv, requests, packaging

### Benefits of UV Environment:
- ⚡ **Faster**: 10-100x faster package installation
- 🔒 **Isolated**: Clean, dedicated environment
- 🛡️ **Reliable**: Consistent dependency resolution
- 🚀 **Modern**: Latest Python packaging technology

## File Structure

```
python_update/
├── python_packages_app.py    # Main application
├── requirements.txt          # Dependencies
├── setup.py                 # Setup script
├── run_app.bat             # Windows launcher
├── run_app.sh              # Linux/Mac launcher
├── output/                 # Log files and exports
└── README.md              # This file
```

## Logs

All package operations are logged to the `output/` directory:
- Installation logs with timestamps
- Error logs for troubleshooting
- Package upgrade history

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues or feature requests, please create an issue in the GitHub repository.
