# fargo 🚢

> A modern C++ project build tool inspired by 'Others programming language' Cargo

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language: Bash](https://img.shields.io/badge/Language-Bash-blue.svg)](https://www.gnu.org/software/bash/)
[![C++ Standard](https://img.shields.io/badge/C%2B%2B-20-blue.svg)](https://isocpp.org/)

**Author:** Rostislav Stelmach (stelmach.ro@gmail.com)

**fargo** is a lightweight, powerful build tool for C++ projects that brings the simplicity and elegance of Rust's Cargo to the C++ ecosystem. It provides project scaffolding, build management, testing, benchmarking, static analysis, documentation generation, and much more—all with a single, intuitive command-line interface.

## Why fargo?

### The Problem
C++ development often involves:
- Complex build system setup (CMake, Make, etc.)
- Managing dependencies manually
- Setting up testing frameworks
- Configuring static analysis tools
- Creating documentation systems
- Dealing with different build configurations

### The Solution
fargo eliminates this complexity by providing:
- **Zero-configuration project setup** - Get started instantly
- **Intelligent build management** - Automatic dependency handling
- **Integrated toolchain** - Testing, benchmarking, analysis, and docs
- **Configuration profiles** - Environment-specific settings
- **Modern C++ standards** - C++20 support out of the box

##  Quick Start

### Installation

#### Cross-Platform Installation (Recommended)

**Requirements:** Python 3.7+, CMake 3.18+, C++ compiler

```bash
# Clone the repository
git clone https://github.com/stelro/fargo.git
cd fargo

# Install system-wide (requires sudo on Unix, Administrator on Windows)
python install.py

# OR install to user directory (no elevated privileges needed)
python install.py --user

# OR use Make (Unix-like systems)
make install          # System-wide
make install-user     # User directory
```

#### Windows-Specific
```cmd
REM For Windows users who prefer batch files
install.bat           REM System-wide (requires Administrator)
install.bat --user    REM User directory
```

#### Manual Installation
```bash
# Make the Python script executable (Unix-like systems)
chmod +x fargo.py

# Add to PATH or run directly
./fargo.py --version
```

### Verify Installation
```bash
fargo --version
fargo --help
```

### Create Your First Project
```bash
# Create a new C++ project
fargo new myapp

# Navigate to the project
cd myapp

# Build and run
fargo build
fargo run
```

That's it! You now have a fully functional C++ project with:
- CMake build system
- GoogleTest integration
- Google Benchmark setup
- Static analysis configuration
- Documentation generation
- Sanitizer support

#### Quick Command Reference

| Command | Description |
|---------|-------------|
| `fargo new <name>` | Create new C++ project with scaffolding |
| `fargo build [target]` | Build project in debug mode |
| `fargo release [target]` | Build project in release mode |
| `fargo run` / `fargo r` | Build and run main executable |
| `fargo test` | Run unit tests with GoogleTest |
| `fargo bench` | Run benchmarks with Google Benchmark |
| `fargo check` | Run static analysis (clang-tidy, cppcheck) |
| `fargo format` | Format code with clang-format |
| `fargo asan` | Build and run with AddressSanitizer |
| `fargo tsan` | Build and run with ThreadSanitizer |
| `fargo doc` | Generate documentation with Doxygen |
| `fargo clean` | Remove build directory |
| `fargo targets` | List available build targets |
| `fargo profile list` | List configuration profiles |

**Options:** `-v/--verbose` (verbose output), `-p/--profile <name>` (use profile)

##  Features

###  Project Management
- **Instant scaffolding** - Create new projects with all necessary files
- **Smart project detection** - Automatically finds project root
- **Template generation** - CMakeLists.txt, source files, tests, and benchmarks

###  Build System
- **Multi-generator support** - Ninja (preferred) and Make
- **Parallel builds** - Automatic CPU detection for optimal performance
- **Multiple configurations** - Debug, Release, and sanitizer builds
- **Target-specific builds** - Build only what you need

###  Testing & Quality
- **Integrated testing** - GoogleTest automatically configured
- **Performance benchmarking** - Google Benchmark integration
- **Static analysis** - clang-tidy, cppcheck, and scan-build support
- **Code formatting** - clang-format with sensible defaults
- **Memory analysis** - AddressSanitizer and ThreadSanitizer

###  Documentation
- **Auto-generated docs** - Doxygen integration with beautiful defaults
- **Markdown support** - README.md as main page
- **Call graphs** - Visual representation of code relationships

###  Configuration Profiles
- **Environment-specific settings** - Different configs for different needs
- **Flexible customization** - Override any build parameter
- **Team collaboration** - Share configurations across team members

##  Command Reference

### Project Commands

#### `fargo new <name>`
Creates a new C++ project with complete scaffolding.

**What it creates:**
- `src/main.cpp` - Hello world application
- `test/example_test.cpp` - Sample test with GoogleTest
- `bench/example_bench.cpp` - Sample benchmark with Google Benchmark
- `CMakeLists.txt` - Complete build configuration
- `.gitignore` - Sensible defaults for C++ projects
- `.fargo/profiles/` - Configuration system

**Example:**
```bash
fargo new calculator
cd calculator
```

### Build Commands

#### `fargo build [target]`
Builds the project in debug mode.

**Features:**
- Automatic dependency resolution
- Parallel compilation
- Compile commands generation for IDEs
- Incremental builds

**Examples:**
```bash
fargo build                    # Build all targets
fargo build calculator_tests   # Build only tests
fargo build -v                 # Verbose output
fargo build -p release         # Use release profile
```

#### `fargo release [target]`
Builds the project in release mode with optimizations.

**Optimizations:**
- `-O3` compiler flag
- `NDEBUG` preprocessor definition
- Link-time optimization (if supported)

**Example:**
```bash
fargo release                  # Optimized build
fargo release calculator       # Build only main executable
```

### Execution Commands

#### `fargo run` (alias: `fargo r`)
Runs the main executable, building if necessary.

**Features:**
- Automatic build detection
- Rebuilds if sources changed
- Passes arguments to executable

**Examples:**
```bash
fargo run                      # Run with no arguments
fargo run --input data.txt     # Pass arguments to program
fargo run -v                   # Verbose build output
```

#### `fargo test`
Runs all unit tests using GoogleTest.

**Features:**
- Parallel test execution
- Detailed failure output
- Integration with CTest

**Example:**
```bash
fargo test                     # Run all tests
```

#### `fargo bench`
Runs performance benchmarks using Google Benchmark.

**Features:**
- Release build for accurate measurements
- Statistical analysis
- Regression detection
- Multiple output formats

**Example:**
```bash
fargo bench                    # Run all benchmarks
```

### Analysis Commands

#### `fargo check`
Runs comprehensive static analysis.

**Tools used:**
- **clang-tidy** - Modernization and bug detection
- **cppcheck** - Additional static analysis
- **scan-build** - Clang static analyzer

**Benefits:**
- Early bug detection
- Code quality improvement
- Best practices enforcement

**Example:**
```bash
fargo check                    # Run all analyzers
```

#### `fargo format`
Formats C++ code using clang-format.

**Features:**
- Google style by default
- Configurable via `.clang-format`
- Supports dry-run mode

**Examples:**
```bash
fargo format                   # Format all files
fargo format --check          # Check without modifying
```

### Sanitizer Commands

#### `fargo asan`
Builds and runs with AddressSanitizer for memory error detection.

**Detects:**
- Buffer overflows
- Use-after-free
- Memory leaks
- Double-free errors

**Example:**
```bash
fargo asan                     # Build and run with ASAN
```

#### `fargo tsan`
Builds and runs with ThreadSanitizer for concurrency analysis.

**Detects:**
- Data races
- Deadlocks
- Thread safety issues

**Example:**
```bash
fargo tsan                     # Build and run with TSAN
```

### Documentation Commands

#### `fargo doc`
Generates comprehensive documentation using Doxygen.

**Features:**
- Automatic API documentation
- Source code browser
- Call and dependency graphs
- Markdown integration

**Generated content:**
- HTML documentation
- Class diagrams
- File relationships
- Search functionality

**Example:**
```bash
fargo doc                      # Generate and open docs
```

### Profile Management

#### `fargo profile list`
Lists all available configuration profiles.

**Example:**
```bash
fargo profile list
# Output:
# Available profiles:
#   default (default)
#   release
#   debug-strict
```

#### `fargo profile new <name>`
Creates a new configuration profile.

**Example:**
```bash
fargo profile new strict-warnings
# Edit .fargo/profiles/strict-warnings.conf
```

#### `fargo profile show [name]`
Displays profile configuration.

**Example:**
```bash
fargo profile show release
```

### Information Commands

#### `fargo targets`
Lists all available build targets.

**Example:**
```bash
fargo targets
# Output:
# Available build targets:
#   calculator (main executable)
#   calculator_tests (unit tests)
#   calculator_bench (benchmarks)
```

#### `fargo clean`
Removes all build artifacts.

**Example:**
```bash
fargo clean                    # Clean build directory
```

##  Configuration Profiles

Configuration profiles allow you to customize build settings for different environments, teams, or use cases.

### Profile System

Profiles are stored in `.fargo/profiles/` as shell configuration files. Each profile can override:

- **Build settings** - Generator, C++ standard, build types
- **Compiler flags** - Debug/release optimization levels
- **Tool configuration** - Test runners, benchmark settings
- **Analysis settings** - Static analysis severity levels

### Default Profile

The default profile (`default.conf`) includes sensible defaults:

```bash
# Build configuration
CMAKE_GENERATOR="Ninja"
CMAKE_CXX_STANDARD="20"
CMAKE_BUILD_TYPE_DEBUG="Debug"
CMAKE_BUILD_TYPE_RELEASE="Release"

# Compiler flags
CXX_FLAGS_DEBUG="-Wall -Wextra -g"
CXX_FLAGS_RELEASE="-O3 -DNDEBUG"

# Additional CMake options
CMAKE_EXTRA_OPTIONS=""

# Test configuration
TEST_PARALLEL_JOBS="auto"
TEST_OUTPUT_ON_FAILURE="ON"

# Benchmark configuration
BENCH_MIN_TIME="1"
BENCH_REPETITIONS="3"

# Documentation
DOC_EXTRACT_ALL="YES"
DOC_GENERATE_CALL_GRAPH="YES"

# Static analysis
STATIC_ANALYSIS_SEVERITY="warning"
```

### Creating Custom Profiles

#### Example: Strict Warnings Profile
```bash
fargo profile new strict

# Edit .fargo/profiles/strict.conf
CXX_FLAGS_DEBUG="-Wall -Wextra -Werror -Wpedantic -g"
CXX_FLAGS_RELEASE="-Wall -Wextra -Werror -O3 -DNDEBUG"
STATIC_ANALYSIS_SEVERITY="error"
```

#### Example: Performance Profile
```bash
fargo profile new performance

# Edit .fargo/profiles/performance.conf
CXX_FLAGS_RELEASE="-O3 -DNDEBUG -march=native -flto"
CMAKE_EXTRA_OPTIONS="-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON"
BENCH_MIN_TIME="5"
BENCH_REPETITIONS="10"
```

#### Example: Cross-compilation Profile
```bash
fargo profile new arm64

# Edit .fargo/profiles/arm64.conf
CMAKE_EXTRA_OPTIONS="-DCMAKE_TOOLCHAIN_FILE=arm64-toolchain.cmake"
CMAKE_GENERATOR="Make"
```

### Using Profiles

```bash
# Use a specific profile for any command
fargo build -p strict
fargo test -p performance
fargo release -p arm64

# Combine with other flags
fargo build -p strict -v          # Strict profile with verbose output
fargo run -p performance --bench  # Performance profile for benchmarking
```

### Profile Benefits

1. **Team Consistency** - Share build configurations across team members
2. **Environment Adaptation** - Different settings for CI/CD, development, production
3. **Specialization** - Profiles for specific tasks (debugging, profiling, release)
4. **Experimentation** - Test different compiler flags and optimizations
5. **Tool Integration** - Custom configurations for different analysis tools

##  Requirements

### Supported Platforms
- **Linux** - Ubuntu 20.04+, Debian 11+, Fedora 35+, Arch Linux, CentOS 8+
- **macOS** - macOS 11.0+ (Big Sur and later) with Xcode Command Line Tools

*Windows support with WSL (Windows Subsystem for Linux) should work but is not officially tested.*

### System Requirements
- **Bash 3+** - Shell for script execution
- **CMake 3.18+** - Build system generator
- **C++ Compiler** - GCC 10+, Clang 12+, or MSVC 2019+
- **Build System** - Ninja (recommended) or Make

### Optional Tools
- **clang-format** - Code formatting
- **clang-tidy** - Static analysis
- **cppcheck** - Additional static analysis
- **scan-build** - Clang static analyzer
- **doxygen** - Documentation generation
- **graphviz** - Enhanced documentation graphs

### Installation Commands

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install build-essential cmake ninja-build clang-format clang-tidy cppcheck doxygen graphviz
```

#### Fedora/RHEL
```bash
sudo dnf install gcc-c++ cmake ninja-build clang-tools-extra cppcheck doxygen graphviz
```

#### macOS
```bash
brew install cmake ninja clang-format llvm doxygen graphviz
```

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Support

- **Issues** - [GitHub Issues](https://github.com/stelro/fargo/issues)
- **Discussions** - [GitHub Discussions](https://github.com/stelro/fargo/discussions)
- **Wiki** - [Documentation Wiki](https://github.com/stelro/fargo/wiki)

---

*fargo - Making C++ development as simple as it should be.*
