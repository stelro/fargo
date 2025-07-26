#!/usr/bin/env python3
"""
fargo installer script
----------------------

Cross-platform installer for fargo C++ project manager.
Supports Windows, macOS, and Linux.

Usage: python install.py [OPTIONS]

Author: Rostislav Stelmach (rstelmac.ro@gmail.com)

"""

import argparse
import os
import platform
import shutil
import stat
import sys
from pathlib import Path
from typing import Optional


class Colors:
    """Terminal colors for cross-platform support."""
    
    def __init__(self):
        self.enabled = self._supports_color()
        if self.enabled:
            self.BLUE = '\033[34m'
            self.GREEN = '\033[32m'
            self.YELLOW = '\033[33m'
            self.RED = '\033[31m'
            self.RESET = '\033[0m'
        else:
            self.BLUE = self.GREEN = self.YELLOW = self.RED = self.RESET = ''
    
    def _supports_color(self) -> bool:
        """Check if terminal supports colors."""
        if platform.system() == "Windows":
            try:
                import colorama
                colorama.init()
                return True
            except ImportError:
                return False
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


colors = Colors()


def log(message: str) -> None:
    """Log an informational message."""
    print(f"{colors.BLUE}[install]{colors.RESET} {message}")


def ok(message: str) -> None:
    """Log a success message."""
    print(f"{colors.GREEN}[OK]{colors.RESET} {message}")


def warn(message: str) -> None:
    """Log a warning message."""
    print(f"{colors.YELLOW}[WARN]{colors.RESET} {message}")


def error(message: str) -> None:
    """Log an error message."""
    print(f"{colors.RED}[ERROR]{colors.RESET} {message}", file=sys.stderr)


def die(message: str) -> None:
    """Log an error and exit."""
    error(message)
    sys.exit(1)


def get_default_install_dirs():
    """Get default installation directories for each platform."""
    system = platform.system()
    
    if system == "Windows":
        # Windows installation paths
        program_files = os.environ.get('PROGRAMFILES', r'C:\Program Files')
        user_local = Path.home() / "AppData" / "Local" / "fargo"
        system_wide = Path(program_files) / "fargo"
        
        return {
            'system': system_wide,
            'user': user_local,
            'bin_name': 'fargo.py'  # Keep .py extension on Windows for now
        }
    else:
        # Unix-like systems (macOS, Linux)
        return {
            'system': Path('/usr/local/bin'),
            'user': Path.home() / '.local' / 'bin',
            'bin_name': 'fargo'
        }


def check_requirements() -> bool:
    """Check if system requirements are met."""
    log("Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        error("Python 3.7+ is required")
        return False
    
    # Check for required tools
    required_tools = ['cmake']
    optional_tools = ['ninja', 'make', 'clang-format', 'clang-tidy', 'cppcheck']
    
    missing_required = []
    missing_optional = []
    
    for tool in required_tools:
        if not shutil.which(tool):
            missing_required.append(tool)
    
    for tool in optional_tools:
        if not shutil.which(tool):
            missing_optional.append(tool)
    
    # Check for C++ compiler
    cpp_compilers = ['g++', 'clang++', 'cl']  # cl for MSVC on Windows
    has_compiler = any(shutil.which(compiler) for compiler in cpp_compilers)
    
    if not has_compiler:
        missing_required.append("C++ compiler (g++, clang++, or MSVC)")
    
    # Report missing tools
    if missing_required:
        error("Missing required tools:")
        for tool in missing_required:
            error(f"  - {tool}")
        
        # Provide platform-specific installation hints
        system = platform.system()
        if system == "Linux":
            warn("Ubuntu/Debian: sudo apt install cmake build-essential")
            warn("Fedora: sudo dnf install cmake gcc-c++")
        elif system == "Darwin":
            warn("macOS: brew install cmake")
            warn("Install Xcode Command Line Tools: xcode-select --install")
        elif system == "Windows":
            warn("Windows: Install Visual Studio Build Tools or Visual Studio")
            warn("Install CMake from https://cmake.org/download/")
        
        return False
    
    if missing_optional:
        warn("Optional tools not found (recommended for full functionality):")
        for tool in missing_optional:
            warn(f"  - {tool}")
        
        system = platform.system()
        if system == "Linux":
            warn("Ubuntu/Debian: sudo apt install ninja-build clang-format clang-tidy cppcheck")
        elif system == "Darwin":
            warn("macOS: brew install ninja llvm cppcheck")
        elif system == "Windows":
            warn("Windows: Install LLVM from https://llvm.org/")
    
    ok("Required tools found")
    return True


def is_admin_windows() -> bool:
    """Check if running as administrator on Windows."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def needs_elevation(install_dir: Path) -> bool:
    """Check if installation requires elevation."""
    system = platform.system()
    
    if system == "Windows":
        # Check if trying to install to Program Files
        program_files = os.environ.get('PROGRAMFILES', r'C:\Program Files')
        if str(install_dir).startswith(program_files):
            return not is_admin_windows()
    else:
        # Unix-like: check if installing to system directories
        system_dirs = ['/usr', '/opt', '/bin', '/sbin']
        if any(str(install_dir).startswith(sys_dir) for sys_dir in system_dirs):
            return os.geteuid() != 0 if hasattr(os, 'geteuid') else True
    
    return False


def create_windows_batch_wrapper(install_dir: Path, script_name: str) -> None:
    """Create a batch file wrapper for Windows."""
    batch_content = f"""@echo off
python "{install_dir / script_name}" %*
"""
    
    batch_file = install_dir / "fargo.bat"
    batch_file.write_text(batch_content)
    
    # Also create a PowerShell wrapper
    ps1_content = f"""#!/usr/bin/env pwsh
& python "{install_dir / script_name}" @args
"""
    
    ps1_file = install_dir / "fargo.ps1"
    ps1_file.write_text(ps1_content)


def install_fargo(install_dir: Path, user_install: bool = False) -> None:
    """Install fargo to the specified directory."""
    script_dir = Path(__file__).parent
    source_script = script_dir / "fargo.py"
    
    if not source_script.exists():
        die(f"fargo.py not found in {script_dir}")
    
    # Get platform-specific settings
    dirs = get_default_install_dirs()
    bin_name = dirs['bin_name']
    target_script = install_dir / bin_name
    
    # Check if elevation is needed
    if needs_elevation(install_dir):
        system = platform.system()
        if system == "Windows":
            error("Administrator privileges required for system-wide installation")
            error("Run Command Prompt or PowerShell as Administrator, or use --user flag")
        else:
            error("Root privileges required for system-wide installation")
            error("Run with sudo, or use --user flag")
        sys.exit(1)
    
    # Create installation directory
    log(f"Creating installation directory: {install_dir}")
    install_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy the script
    log(f"Installing fargo to {target_script}")
    shutil.copy2(source_script, target_script)
    
    # Make executable on Unix-like systems
    if platform.system() != "Windows":
        # Make executable
        current_mode = target_script.stat().st_mode
        target_script.chmod(current_mode | stat.S_IEXEC)
    else:
        # Create batch and PowerShell wrappers for Windows
        create_windows_batch_wrapper(install_dir, bin_name)
    
    # Check if install directory is in PATH
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    in_path = any(Path(p).resolve() == install_dir.resolve() for p in path_dirs if p)
    
    ok(f"fargo installed successfully to {target_script}")
    
    if not in_path:
        warn(f"Installation directory {install_dir} is not in your PATH")
        system = platform.system()
        
        if system == "Windows":
            warn("Add to PATH using System Properties > Environment Variables")
            warn(f"Or add this to your PowerShell profile: $env:PATH += ';{install_dir}'")
        else:
            shell_config = "~/.bashrc" if Path.home().joinpath('.bashrc').exists() else "~/.profile"
            warn(f"Add to your {shell_config}:")
            warn(f"  export PATH=\"{install_dir}:$PATH\"")
    
    # Display usage examples
    print()
    ok("Installation complete! Try it out:")
    
    if platform.system() == "Windows":
        if in_path:
            print("  fargo new myproject")
        else:
            print(f"  {install_dir / 'fargo.bat'} new myproject")
    else:
        if in_path:
            print("  fargo new myproject")
        else:
            print(f"  {target_script} new myproject")
    
    print("  cd myproject")
    print("  fargo build && fargo run")


def uninstall_fargo(install_dir: Path) -> None:
    """Uninstall fargo from the specified directory."""
    dirs = get_default_install_dirs()
    bin_name = dirs['bin_name']
    target_script = install_dir / bin_name
    
    files_to_remove = [target_script]
    
    # Add Windows-specific files
    if platform.system() == "Windows":
        files_to_remove.extend([
            install_dir / "fargo.bat",
            install_dir / "fargo.ps1"
        ])
    
    removed_files = []
    for file_path in files_to_remove:
        if file_path.exists():
            try:
                file_path.unlink()
                removed_files.append(file_path)
                log(f"Removed {file_path}")
            except Exception as e:
                error(f"Failed to remove {file_path}: {e}")
    
    if removed_files:
        ok(f"fargo uninstalled successfully")
    else:
        warn(f"No fargo installation found in {install_dir}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Cross-platform installer for fargo C++ project manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python install.py                      # Install system-wide
  python install.py --user               # Install to user directory
  python install.py --prefix ~/tools     # Install to custom directory
  python install.py --uninstall          # Uninstall system installation
  python install.py --uninstall --user   # Uninstall user installation

Platform-specific notes:
  Windows: System installation requires Administrator privileges
  Linux/macOS: System installation requires sudo
"""
    )
    
    parser.add_argument("--user", action="store_true",
                       help="Install to user directory instead of system-wide")
    parser.add_argument("--prefix", type=Path,
                       help="Install to custom directory")
    parser.add_argument("--uninstall", action="store_true",
                       help="Uninstall fargo")
    parser.add_argument("--check", action="store_true",
                       help="Check system requirements only")
    
    args = parser.parse_args()
    
    # Check requirements first
    if not check_requirements():
        sys.exit(1)
    
    if args.check:
        ok("All requirements satisfied")
        return
    
    # Determine installation directory
    dirs = get_default_install_dirs()
    
    if args.prefix:
        install_dir = args.prefix
    elif args.user:
        install_dir = dirs['user']
    else:
        install_dir = dirs['system']
    
    # Perform installation or uninstallation
    if args.uninstall:
        uninstall_fargo(install_dir)
    else:
        install_fargo(install_dir, args.user)


if __name__ == "__main__":
    main()
