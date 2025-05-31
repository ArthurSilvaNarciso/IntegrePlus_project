"""
Required packages for Integre+ System
Install using: pip install -r requiremments.txt
"""

requirements = [
    # GUI and Image Processing
    'tkinter',  # Usually comes with Python
    'Pillow',   # PIL fork for image processing
    
    # Data Handling and Visualization
    'pandas',
    'matplotlib',
    'numpy',
    
    # Database
    'sqlite3',  # Usually comes with Python
    
    # Excel Support
    'openpyxl',  # For Excel file handling
    'xlrd',      # For reading Excel files
    'xlwt',      # For writing Excel files
    
    # Date/Time Handling
    'python-dateutil',
    
    # Optional but recommended
    'tkcalendar',  # Calendar widget for date picking
    'customtkinter',  # Modern looking widgets
    'darkdetect',    # Auto dark/light theme detection
]

# Version Information
VERSION = '2.0.0'
PYTHON_MIN_VERSION = '3.8.0'

def check_dependencies():
    """Check if all required packages are installed"""
    import pkg_resources
    import sys
    
    missing = []
    
    # Check Python version
    if sys.version_info < tuple(map(int, PYTHON_MIN_VERSION.split('.'))):
        print(f"Error: Python {PYTHON_MIN_VERSION} or higher is required")
        sys.exit(1)
    
    # Check each required package
    for package in requirements:
        try:
            pkg_resources.require(package)
        except pkg_resources.DistributionNotFound:
            missing.append(package)
    
    if missing:
        print("Missing required packages:")
        print("\n".join(f"  - {pkg}" for pkg in missing))
        print("\nInstall using: pip install " + " ".join(missing))
        return False
    
    return True

if __name__ == "__main__":
    check_dependencies()
