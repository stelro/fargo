# Installation Guide

## Requirements

Before installing fargo, ensure you have the following dependencies:

- **Python 3.7+**
- **cmake 3.18+**
- **C++ compiler** (g++, clang++, or MSVC on Windows)
- **Build system** (ninja recommended, make as fallback)

### Optional Tools (Recommended)
- ninja (for faster builds)
- clang-tidy (static analysis)
- cppcheck (static analysis)  
- clang-format (code formatting)
- doxygen (documentation generation)

## Cross-Platform Installation

### Method 1: Python Installer (Recommended)

Works on Windows, macOS, and Linux:

```bash
# Clone the repository
git clone https://github.com/stelro/fargo.git
cd fargo

# Check system requirements
python install.py --check

# Install system-wide (requires sudo on Unix, Administrator on Windows)
python install.py

# OR install to user directory (no elevated privileges needed)
python install.py --user

# OR install to custom location
python install.py --prefix ~/tools
```

### Method 2: Using Make (Unix-like systems)

```bash
# System-wide installation (requires sudo)
make install

# User installation
make install-user

# Check requirements only
make check

# Uninstall
make uninstall         # Remove system installation
make uninstall-user    # Remove user installation
```

### Method 3: Windows-Specific Installers

For Windows users who prefer native scripts:

```cmd
REM Batch file installer
install.bat           REM System-wide (requires Administrator)
install.bat --user    REM User directory
```

```powershell
# PowerShell installer
.\install.ps1          # System-wide (requires Administrator)
.\install.ps1 -User    # User directory
.\install.ps1 -Check   # Check requirements only
```

### Method 4: Manual Installation

```bash
# Make the Python script executable (Unix-like systems)
chmod +x fargo.py

# Copy to a directory in your PATH
sudo cp fargo.py /usr/local/bin/fargo
sudo chmod +x /usr/local/bin/fargo

# Or for user installation
mkdir -p ~/.local/bin
cp fargo.py ~/.local/bin/fargo
chmod +x ~/.local/bin/fargo

# Add to PATH if needed
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

## Platform-Specific Instructions

### Windows

```cmd
REM Install Python 3.7+ from https://python.org
REM Make sure to check "Add Python to PATH"

REM Install Visual Studio Build Tools or Visual Studio Community
REM Install CMake from https://cmake.org/download/

REM Clone and install fargo
git clone https://github.com/stelro/fargo.git
cd fargo
python install.py --user
```

### Ubuntu/Debian

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip build-essential cmake ninja-build

# Optional tools
sudo apt install clang-tidy cppcheck clang-format doxygen

# Install fargo
python3 install.py --user
```

### Fedora/RHEL

```bash
# Install dependencies
sudo dnf install python3 python3-pip gcc-c++ cmake ninja-build

# Optional tools  
sudo dnf install clang-tools-extra cppcheck doxygen

# Install fargo
python3 install.py --user
```

### macOS

```bash
# Install dependencies (requires Homebrew)
brew install python3 cmake ninja

# Optional tools
brew install llvm doxygen

# Install fargo
python3 install.py --user
```

### Arch Linux

```bash
# Install dependencies
sudo pacman -S python base-devel cmake ninja

# Optional tools
sudo pacman -S clang doxygen

# Install fargo
python install.py --user
```

## Verification

After installation, verify fargo is working:

```bash
# Check version
fargo --version

# Create a test project
fargo new test-project
cd test-project
fargo build
fargo run
```

## Troubleshooting

### Command not found

If you get "command not found" after installation:

1. **Check PATH**: Ensure the installation directory is in your PATH
   ```bash
   echo $PATH
   ```

2. **For user installation**: Add ~/.local/bin to PATH (Unix) or check Windows PATH
   ```bash
   # Unix-like systems
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```
   
   ```cmd
   REM Windows: Add to PATH via System Properties > Environment Variables
   REM Or temporarily in current session:
   set PATH=%PATH%;%USERPROFILE%\AppData\Local\fargo
   ```

3. **Restart shell**: Open a new terminal or source your shell config

### Permission denied

If you get permission errors:

- Use `sudo` for system-wide installation (Unix)
- Run as Administrator on Windows for system-wide installation
- Use `--user` flag for user installation
- Check file permissions with `ls -la fargo.py`

### Missing dependencies

If Python, cmake, or compiler is missing:

```bash
# Ubuntu/Debian
sudo apt install python3 build-essential cmake

# Fedora
sudo dnf install python3 gcc-c++ cmake

# macOS
brew install python3 cmake
xcode-select --install
```

```cmd
REM Windows
REM Install Python from https://python.org
REM Install Visual Studio Build Tools
REM Install CMake from https://cmake.org
```

## Uninstallation

### Using the Python installer
```bash
# Remove from system
python install.py --uninstall

# Remove from user directory
python install.py --uninstall --user
```

### Using Make (Unix-like systems)
```bash
make uninstall         # System installation
make uninstall-user    # User installation
```

### Manual removal
```bash
# Unix-like systems
sudo rm /usr/local/bin/fargo        # System installation
rm ~/.local/bin/fargo               # User installation

# Windows
# Remove from Program Files\fargo or %USERPROFILE%\AppData\Local\fargo
# Remove from PATH environment variable
```

## Development Installation

For development or contributing:

```bash
# Clone repository
git clone https://github.com/stelro/fargo.git
cd fargo

# Make executable (Unix-like systems)
chmod +x fargo.py

# Run from current directory
python fargo.py --version

# Or symlink to PATH (Unix-like systems)
ln -s "$(pwd)/fargo.py" ~/.local/bin/fargo
```
