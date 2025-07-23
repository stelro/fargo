# Installation Guide

## Requirements

Before installing fargo, ensure you have the following dependencies:

- **bash 4+**
- **cmake 3.18+**
- **C++ compiler** (g++ or clang++)
- **Build system** (ninja recommended, make as fallback)

### Optional Tools
- ninja (for faster builds)
- clang-tidy (static analysis)
- cppcheck (static analysis)  
- clang-format (code formatting)
- doxygen (documentation generation)

## Installation Methods

### Method 1: Automatic Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/stelro/fargo.git
cd fargo

# Install system-wide (requires sudo)
./install.sh

# OR install to user directory (~/.local/bin)
./install.sh --user

# OR install to custom location
./install.sh --prefix ~/bin
```

### Method 2: Using Make

```bash
# System-wide installation (requires sudo)
make install

# User installation
make install-user

# Custom prefix
make PREFIX=/opt install

# Uninstall
make uninstall         # Remove system installation
make uninstall-user    # Remove user installation
```

### Method 3: Manual Installation

```bash
# Copy to a directory in your PATH
sudo cp fargo /usr/local/bin/
sudo chmod +x /usr/local/bin/fargo

# Or for user installation
mkdir -p ~/.local/bin
cp fargo ~/.local/bin/
chmod +x ~/.local/bin/fargo

# Add to PATH if needed
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

## Platform-Specific Instructions

### Ubuntu/Debian

```bash
# Install dependencies
sudo apt update
sudo apt install build-essential cmake ninja-build

# Optional tools
sudo apt install clang-tidy cppcheck clang-format doxygen

# Install fargo
./install.sh
```

### Fedora/RHEL

```bash
# Install dependencies
sudo dnf install gcc-c++ cmake ninja-build

# Optional tools  
sudo dnf install clang-tools-extra cppcheck doxygen

# Install fargo
./install.sh
```

### macOS

```bash
# Install dependencies (requires Homebrew)
brew install cmake ninja

# Optional tools
brew install llvm doxygen

# Install fargo
./install.sh
```

### Arch Linux

```bash
# Install dependencies
sudo pacman -S base-devel cmake ninja

# Optional tools
sudo pacman -S clang doxygen

# Install fargo
./install.sh
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

2. **For user installation**: Add ~/.local/bin to PATH
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Restart shell**: Open a new terminal or run `source ~/.bashrc`

### Permission denied

If you get permission errors:

- Use `sudo` for system-wide installation
- Use `--user` flag for user installation
- Check file permissions with `ls -la fargo`

### Missing dependencies

If cmake or compiler is missing:

```bash
# Ubuntu/Debian
sudo apt install build-essential cmake

# Fedora
sudo dnf install gcc-c++ cmake

# macOS
brew install cmake
xcode-select --install
```

## Uninstallation

### Using the installer
```bash
# Remove from system
sudo rm /usr/local/bin/fargo

# Remove from user directory
rm ~/.local/bin/fargo
```

### Using Make
```bash
make uninstall         # System installation
make uninstall-user    # User installation
```

## Development Installation

For development or contributing:

```bash
# Clone repository
git clone https://github.com/stelro/fargo.git
cd fargo

# Make executable
chmod +x fargo

# Run from current directory
./fargo --version

# Or symlink to PATH
ln -s "$(pwd)/fargo" ~/.local/bin/fargo
```
