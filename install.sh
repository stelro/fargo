#!/usr/bin/env bash
#
# fargo installer script
# ----------------------
#
# This script installs fargo to your system.
# Usage: ./install.sh [OPTIONS]
#
set -euo pipefail

# Configuration
FARGO_SCRIPT="fargo"
DEFAULT_INSTALL_DIR="/usr/local/bin"
USER_INSTALL_DIR="$HOME/.local/bin"

# Colors for output
if [[ -t 1 ]]; then
  t_red=$(tput setaf 1); t_green=$(tput setaf 2)
  t_yellow=$(tput setaf 3); t_blue=$(tput setaf 4); t_reset=$(tput sgr0)
else
  t_red=""; t_green=""; t_yellow=""; t_blue=""; t_reset=""
fi

log()   { echo -e "${t_blue}[install]${t_reset} $*"; }
ok()    { echo -e "${t_green}[OK]${t_reset} $*"; }
warn()  { echo -e "${t_yellow}[WARN]${t_reset} $*"; }
err()   { echo -e "${t_red}[ERROR]${t_reset} $*" >&2; }
die()   { err "$@"; exit 1; }

print_help() {
  cat <<EOF
fargo installer

USAGE:
    ./install.sh [OPTIONS]

OPTIONS:
    --user          Install to user directory (~/.local/bin) instead of system-wide
    --prefix DIR    Install to custom directory (default: /usr/local/bin)
    --help, -h      Show this help message

EXAMPLES:
    ./install.sh                    # Install system-wide (requires sudo)
    ./install.sh --user             # Install to user directory
    ./install.sh --prefix ~/bin     # Install to custom directory

REQUIREMENTS:
    - bash 4+
    - cmake 3.18+
    - A C++ compiler (g++/clang++)
    - make or ninja (ninja recommended)

After installation, you can create a new C++ project with:
    fargo new myproject
    cd myproject
    fargo build
    fargo run
EOF
}

check_requirements() {
  log "Checking system requirements..."
  
  local missing_deps=()
  
  # Check bash version
  if [[ ${BASH_VERSION%%.*} -lt 4 ]]; then
    missing_deps+=("bash 4+ (current: $BASH_VERSION)")
  fi
  
  # Check for cmake
  if ! command -v cmake >/dev/null 2>&1; then
    missing_deps+=("cmake")
  else
    local cmake_version
    cmake_version=$(cmake --version | head -n1 | grep -o '[0-9]\+\.[0-9]\+')
    local cmake_major=${cmake_version%%.*}
    local cmake_minor=${cmake_version#*.}
    if [[ $cmake_major -lt 3 ]] || [[ $cmake_major -eq 3 && $cmake_minor -lt 18 ]]; then
      missing_deps+=("cmake 3.18+ (current: $cmake_version)")
    fi
  fi
  
  # Check for C++ compiler
  if ! command -v g++ >/dev/null 2>&1 && ! command -v clang++ >/dev/null 2>&1; then
    missing_deps+=("C++ compiler (g++ or clang++)")
  fi
  
  # Check for build system (prefer ninja, fallback to make)
  if ! command -v ninja >/dev/null 2>&1 && ! command -v make >/dev/null 2>&1; then
    missing_deps+=("build system (ninja or make)")
  fi
  
  if [[ ${#missing_deps[@]} -gt 0 ]]; then
    err "Missing required dependencies:"
    for dep in "${missing_deps[@]}"; do
      echo "  - $dep"
    done
    echo
    echo "Please install the missing dependencies and try again."
    echo
    echo "On Ubuntu/Debian:"
    echo "  sudo apt update"
    echo "  sudo apt install build-essential cmake ninja-build"
    echo
    echo "On Fedora:"
    echo "  sudo dnf install gcc-c++ cmake ninja-build"
    echo
    echo "On macOS:"
    echo "  brew install cmake ninja"
    echo "  # Xcode command line tools for compiler"
    echo
    exit 1
  fi
  
  ok "All requirements satisfied"
}

install_fargo() {
  local install_dir="$1"
  local target_path="$install_dir/$FARGO_SCRIPT"
  
  # Check if fargo script exists
  if [[ ! -f "$FARGO_SCRIPT" ]]; then
    die "fargo script not found in current directory. Please run this installer from the fargo repository root."
  fi
  
  # Create install directory if it doesn't exist
  if [[ ! -d "$install_dir" ]]; then
    log "Creating directory: $install_dir"
    mkdir -p "$install_dir" || die "Failed to create directory: $install_dir"
  fi
  
  # Check if we need sudo for system installation
  if [[ "$install_dir" == "$DEFAULT_INSTALL_DIR" ]] && [[ ! -w "$install_dir" ]]; then
    if command -v sudo >/dev/null 2>&1; then
      log "Installing fargo to $target_path (requires sudo)"
      sudo cp "$FARGO_SCRIPT" "$target_path" || die "Failed to install fargo"
      sudo chmod +x "$target_path" || die "Failed to make fargo executable"
    else
      die "No write permission to $install_dir and sudo not available. Try --user option or install as root."
    fi
  else
    log "Installing fargo to $target_path"
    cp "$FARGO_SCRIPT" "$target_path" || die "Failed to install fargo"
    chmod +x "$target_path" || die "Failed to make fargo executable"
  fi
  
  ok "fargo installed successfully to $target_path"
}

check_path() {
  local install_dir="$1"
  
  # Check if install directory is in PATH
  if [[ ":$PATH:" != *":$install_dir:"* ]]; then
    warn "Directory $install_dir is not in your PATH"
    echo
    echo "To use fargo from anywhere, add this directory to your PATH:"
    echo "  export PATH=\"$install_dir:\$PATH\""
    echo
    
    if [[ "$install_dir" == "$USER_INSTALL_DIR" ]]; then
      echo "Add this line to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
      echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
    echo
  else
    ok "Installation directory is in PATH"
  fi
}

verify_installation() {
  local install_dir="$1"
  local target_path="$install_dir/$FARGO_SCRIPT"
  
  if [[ -x "$target_path" ]]; then
    log "Verifying installation..."
    local version
    version=$("$target_path" --version 2>/dev/null) || die "fargo is not working correctly"
    ok "fargo $version is ready to use!"
    echo
    echo "Try it out:"
    echo "  fargo new myproject"
    echo "  cd myproject"
    echo "  fargo build"
    echo "  fargo run"
  else
    die "Installation verification failed"
  fi
}

main() {
  local install_dir="$DEFAULT_INSTALL_DIR"
  local user_install=false
  
  # Parse command line arguments
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --user)
        user_install=true
        install_dir="$USER_INSTALL_DIR"
        shift
        ;;
      --prefix)
        shift
        [[ $# -eq 0 ]] && die "--prefix requires a directory argument"
        install_dir="$1"
        shift
        ;;
      --help|-h)
        print_help
        exit 0
        ;;
      *)
        die "Unknown option: $1. Use --help for usage information."
        ;;
    esac
  done
  
  log "fargo installer"
  log "Installing to: $install_dir"
  echo
  
  check_requirements
  install_fargo "$install_dir"
  check_path "$install_dir"
  verify_installation "$install_dir"
  
  echo
  ok "Installation complete!"
}

main "$@"
