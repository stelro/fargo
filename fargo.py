#!/usr/bin/env python3
"""
fargo - tiny C++ project bootstrap/build helper (Cargo-like)
------------------------------------------------------------

Author: Rostislav Stelmach <stelmach.ro@gmail.com>
Repository: https://github.com/stelro/fargo
License: MIT

Requirements: Python 3.7+, cmake 3.18+, a C++ compiler, and make or ninja.
GoogleTest is fetched automatically via CMake's FetchContent when you use `fargo new`.
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import configparser
import glob
import re

__version__ = "0.1.0"

# ---------- Configuration ----------
BUILD_DIR = "build"
DEBUG_SUBDIR = "debug"
RELEASE_SUBDIR = "release"
ASAN_SUBDIR = "debug_asan"
TSAN_SUBDIR = "debug_tsan"

# Configuration profiles
PROFILE_DIR = ".fargo"
PROFILES_DIR = f"{PROFILE_DIR}/profiles"
DEFAULT_PROFILE = "default"

SRC_DIR = "src"
TEST_DIR = "test"
BENCH_DIR = "bench"
MAIN_FILE = "main.cpp"
TEST_FILE = "example_test.cpp"
BENCH_FILE = "example_bench.cpp"
CMAKELISTS_FILE = "CMakeLists.txt"

# Global state
verbose = False
current_profile = DEFAULT_PROFILE


class Colors:
    """Terminal colors for cross-platform support."""
    
    def __init__(self):
        self.enabled = self._supports_color()
        if self.enabled:
            self.BLUE = '\033[34m'
            self.GREEN = '\033[32m'
            self.YELLOW = '\033[33m'
            self.RED = '\033[31m'
            self.BOLD = '\033[1m'
            self.RESET = '\033[0m'
        else:
            self.BLUE = self.GREEN = self.YELLOW = self.RED = self.BOLD = self.RESET = ''
    
    def _supports_color(self) -> bool:
        """Check if terminal supports colors."""
        if platform.system() == "Windows":
            # Windows 10+ supports ANSI colors
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
    print(f"{colors.BLUE}[fargo]{colors.RESET} {message}")


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


def need_cmd(command: str) -> None:
    """Check if a required command is available."""
    if not shutil.which(command):
        die(f"Required command '{command}' not found. Please install it.")


def run_command(cmd: List[str], cwd: Optional[Path] = None, capture_output: bool = False, 
                check: bool = True) -> subprocess.CompletedProcess:
    """Run a command with proper error handling."""
    if verbose and not capture_output:
        log(f"Running: {' '.join(cmd)}")
    
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=check
        )
    except subprocess.CalledProcessError as e:
        if not capture_output:
            error(f"Command failed: {' '.join(cmd)}")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr, file=sys.stderr)
        raise
    except FileNotFoundError:
        die(f"Command not found: {cmd[0]}")


def find_project_root() -> Optional[Path]:
    """Find the project root by looking for CMakeLists.txt with project()."""
    current = Path.cwd()
    
    while current != current.parent:
        cmake_file = current / CMAKELISTS_FILE
        if cmake_file.exists():
            try:
                content = cmake_file.read_text()
                if 'project(' in content:
                    return current
            except Exception:
                pass
        current = current.parent
    
    return None


def ensure_project_root() -> Path:
    """Ensure we're in a fargo project and return the root directory."""
    root = find_project_root()
    if not root:
        die("Not inside a fargo project (can't find top-level CMakeLists.txt)")
    return root


def get_cpu_count() -> int:
    """Get the number of CPU cores for parallel builds."""
    try:
        return os.cpu_count() or 4
    except Exception:
        return 4


def get_project_name(root: Path) -> str:
    """Extract project name from CMakeLists.txt."""
    cmake_file = root / CMAKELISTS_FILE
    if not cmake_file.exists():
        die(f"CMakeLists.txt not found in {root}")
    
    content = cmake_file.read_text()
    match = re.search(r'project\(\s*(\w+)', content)
    if match:
        return match.group(1)
    
    die("Could not extract project name from CMakeLists.txt")


def load_profile(profile_name: str = None) -> Dict[str, str]:
    """Load profile configuration."""
    if profile_name is None:
        profile_name = current_profile
    
    root = find_project_root()
    if not root:
        return {}
    
    profile_file = root / PROFILES_DIR / f"{profile_name}.conf"
    
    if profile_file.exists():
        log(f"Loading profile: {profile_name}")
        config = configparser.ConfigParser()
        # Add a default section for simple key=value files
        content = "[DEFAULT]\n" + profile_file.read_text()
        config.read_string(content)
        return dict(config['DEFAULT'])
    elif profile_name != DEFAULT_PROFILE:
        warn(f"Profile '{profile_name}' not found, using defaults")
    
    return {}


def create_default_profile(profiles_dir: Path) -> None:
    """Create default profile configuration."""
    profiles_dir.mkdir(parents=True, exist_ok=True)
    
    default_config = """# Default fargo profile configuration
# Override these values in custom profiles

# Build configuration
CMAKE_GENERATOR=Ninja
CMAKE_CXX_STANDARD=20
CMAKE_BUILD_TYPE_DEBUG=Debug
CMAKE_BUILD_TYPE_RELEASE=Release

# Compiler flags
CXX_FLAGS_DEBUG=-Wall -Wextra -g
CXX_FLAGS_RELEASE=-O3 -DNDEBUG

# Additional CMake options
CMAKE_EXTRA_OPTIONS=

# Test configuration
TEST_PARALLEL_JOBS=auto
TEST_OUTPUT_ON_FAILURE=ON

# Benchmark configuration
BENCH_MIN_TIME=1
BENCH_REPETITIONS=3

# Documentation
DOC_EXTRACT_ALL=YES
DOC_GENERATE_CALL_GRAPH=YES

# Static analysis
STATIC_ANALYSIS_SEVERITY=warning
"""
    
    (profiles_dir / f"{DEFAULT_PROFILE}.conf").write_text(default_config)


# ---------- Templates ----------
def write_cmakelists(project_name: str) -> None:
    """Write CMakeLists.txt template."""
    template = f"""cmake_minimum_required(VERSION 3.18)

# ---- Project ----
project({project_name} VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)  # Generate compile_commands.json for static analysis

# ---- Build Configuration ----
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Debug)
endif()

# ---- Source Files ----
file(GLOB_RECURSE SOURCES "src/*.cpp" "src/*.cxx" "src/*.cc")
file(GLOB_RECURSE HEADERS "src/*.h" "src/*.hpp" "src/*.hxx")

# ---- Main Executable ----
add_executable(${{PROJECT_NAME}} src/main.cpp)

# ---- Library (if you have multiple source files) ----
# Uncomment and modify as needed:
# add_library(${{PROJECT_NAME}}_lib ${{SOURCES}})
# target_include_directories(${{PROJECT_NAME}}_lib PUBLIC src)
# target_link_libraries(${{PROJECT_NAME}} ${{PROJECT_NAME}}_lib)

# ---- Tests ----
include(CTest)
enable_testing()

# Fetch GoogleTest
include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/v1.15.0.zip
  DOWNLOAD_EXTRACT_TIMESTAMP true
)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

# Test executable
file(GLOB_RECURSE TEST_SOURCES "test/*.cpp" "test/*.cxx" "test/*.cc")
add_executable(${{PROJECT_NAME}}_tests ${{TEST_SOURCES}})
target_link_libraries(${{PROJECT_NAME}}_tests gtest_main)
target_include_directories(${{PROJECT_NAME}}_tests PRIVATE src)

add_test(NAME ${{PROJECT_NAME}}_tests COMMAND ${{PROJECT_NAME}}_tests)

# ---- Benchmarks ----
# Fetch Google Benchmark
FetchContent_Declare(
  googlebenchmark
  URL https://github.com/google/benchmark/archive/refs/tags/v1.8.3.zip
  DOWNLOAD_EXTRACT_TIMESTAMP true
)
set(BENCHMARK_ENABLE_TESTING OFF CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googlebenchmark)

# Benchmark executable
file(GLOB_RECURSE BENCH_SOURCES "bench/*.cpp" "bench/*.cxx" "bench/*.cc")
add_executable(${{PROJECT_NAME}}_bench ${{BENCH_SOURCES}})
target_link_libraries(${{PROJECT_NAME}}_bench benchmark::benchmark)
target_include_directories(${{PROJECT_NAME}}_bench PRIVATE src)

# ---- Custom Targets ----
# Example: add more executables here
# add_executable(${{PROJECT_NAME}}_tool tools/tool.cpp)
# target_link_libraries(${{PROJECT_NAME}}_tool ${{PROJECT_NAME}}_lib)

# ---- Installation ----
install(TARGETS ${{PROJECT_NAME}} DESTINATION bin)

# ---- Packaging ----
set(CPACK_PACKAGE_NAME ${{PROJECT_NAME}})
set(CPACK_PACKAGE_VERSION ${{PROJECT_VERSION}})
include(CPack)
"""
    
    Path(CMAKELISTS_FILE).write_text(template)


def write_main_cpp() -> None:
    """Write main.cpp template."""
    src_dir = Path(SRC_DIR)
    src_dir.mkdir(exist_ok=True)
    
    template = """#include <iostream>

int main() {
    std::cout << "Hello, world!\\n";
    return 0;
}
"""
    (src_dir / MAIN_FILE).write_text(template)


def write_test_cpp() -> None:
    """Write test template."""
    test_dir = Path(TEST_DIR)
    test_dir.mkdir(exist_ok=True)
    
    template = """#include <gtest/gtest.h>


TEST(SampleTest, BasicAssertion) {
    EXPECT_EQ(2 + 2, 4);
}
"""
    (test_dir / TEST_FILE).write_text(template)


def write_bench_cpp() -> None:
    """Write benchmark template."""
    bench_dir = Path(BENCH_DIR)
    bench_dir.mkdir(exist_ok=True)
    
    template = """#include <benchmark/benchmark.h>
#include <vector>
#include <algorithm>

// Example benchmark: sorting a vector
static void BM_VectorSort(benchmark::State& state) {
  for (auto _ : state) {
    state.PauseTiming();
    std::vector<int> data(state.range(0));
    std::generate(data.begin(), data.end(), std::rand);
    state.ResumeTiming();
    
    std::sort(data.begin(), data.end());
  }
  state.SetComplexityN(state.range(0));
}

BENCHMARK(BM_VectorSort)->Range(8, 8<<10)->Complexity();

// Example benchmark: simple function
static void BM_StringCreation(benchmark::State& state) {
  for (auto _ : state) {
    std::string empty_string;
  }
}

BENCHMARK(BM_StringCreation);

BENCHMARK_MAIN();
"""
    (bench_dir / BENCH_FILE).write_text(template)


def write_gitignore() -> None:
    """Write .gitignore template."""
    template = """/build/
/.cmake/
/CMakeFiles/
/docs/

/CMakeCache.txt
*.user
*.suo

*.vcxproj*
*.code-workspace
*.idea
Doxyfile.bak
.clang-format.bak

# Keep fargo configuration but ignore user-specific settings
/.fargo/user/
"""
    Path(".gitignore").write_text(template)


# ---------- Commands ----------
def cmd_new(args: argparse.Namespace) -> None:
    """Create a new C++ project."""
    if not args.name:
        die("Usage: fargo new <project_name>")
    
    project_dir = Path(args.name)
    if project_dir.exists():
        die(f"Directory '{args.name}' already exists.")
    
    log(f"Creating new project: {args.name}")
    project_dir.mkdir()
    os.chdir(project_dir)
    
    write_cmakelists(args.name)
    write_main_cpp()
    write_test_cpp()
    write_bench_cpp()
    write_gitignore()
    
    # Create fargo configuration directory and default profile
    profiles_dir = Path(PROFILES_DIR)
    create_default_profile(profiles_dir)
    
    ok("Project structure created:")
    if shutil.which("tree"):
        run_command(["tree", "-a", "-I", ".git"], check=False)
    else:
        run_command(["find", ".", "-maxdepth", "3", "-print"], check=False)
    
    ok(f"Done. cd '{args.name}' and start hacking!")


def cmd_profile(args: argparse.Namespace) -> None:
    """Handle profile management commands."""
    root = ensure_project_root()
    os.chdir(root)
    
    action = args.action or "list"
    profile_name = getattr(args, 'profile_name', None)
    
    profiles_dir = root / PROFILES_DIR
    
    if action in ["list", "ls"]:
        if profiles_dir.exists():
            log("Available profiles:")
            for profile_file in profiles_dir.glob("*.conf"):
                name = profile_file.stem
                if name == DEFAULT_PROFILE:
                    print(f"  {name} (default)")
                else:
                    print(f"  {name}")
        else:
            warn("No profiles directory found. Run 'fargo profile init' to create it.")
    
    elif action == "init":
        create_default_profile(profiles_dir)
        ok("Profile system initialized with default profile")
    
    elif action in ["new", "create"]:
        if not profile_name:
            die("Usage: fargo profile new <profile_name>")
        
        profile_file = profiles_dir / f"{profile_name}.conf"
        if profile_file.exists():
            die(f"Profile '{profile_name}' already exists")
        
        profiles_dir.mkdir(parents=True, exist_ok=True)
        default_file = profiles_dir / f"{DEFAULT_PROFILE}.conf"
        
        if not default_file.exists():
            create_default_profile(profiles_dir)
        
        # Copy from default profile
        content = default_file.read_text()
        content = f"# Custom profile: {profile_name}\n" + content
        profile_file.write_text(content)
        
        ok(f"Profile '{profile_name}' created. Edit {profile_file} to customize.")
    
    elif action == "show":
        if not profile_name:
            profile_name = DEFAULT_PROFILE
        profile_file = profiles_dir / f"{profile_name}.conf"
        
        if profile_file.exists():
            log(f"Profile: {profile_name}")
            print(profile_file.read_text())
        else:
            die(f"Profile '{profile_name}' not found")
    
    else:
        die(f"Unknown profile action '{action}'. Use: list, init, new, show")


def get_build_dir(mode: str) -> Path:
    """Get the build directory for a specific mode."""
    return Path(BUILD_DIR) / mode


def configure_build(build_type: str, outdir: Path, sanitizer: str = None, target: str = None) -> None:
    """Configure CMake build."""
    need_cmd("cmake")
    
    root = ensure_project_root()
    os.chdir(root)
    
    # Load profile configuration
    profile = load_profile()
    
    # Determine generator
    preferred_generator = profile.get("cmake_generator", "Ninja")
    generator_args = []
    
    if preferred_generator == "Ninja" and shutil.which("ninja"):
        generator_args = ["-G", "Ninja"]
        log(f"Configuring {build_type} build in {outdir} (using Ninja)")
    elif preferred_generator == "Make" or not shutil.which("ninja"):
        log(f"Configuring {build_type} build in {outdir} (using Make)")
    else:
        generator_args = ["-G", preferred_generator]
        log(f"Configuring {build_type} build in {outdir} (using {preferred_generator})")
    
    # Build CMake command
    cmake_cmd = [
        "cmake", "-S", ".", "-B", str(outdir),
        f"-DCMAKE_BUILD_TYPE={build_type}"
    ] + generator_args
    
    # Add C++ standard from profile
    cxx_standard = profile.get("cmake_cxx_standard")
    if cxx_standard:
        cmake_cmd.append(f"-DCMAKE_CXX_STANDARD={cxx_standard}")
    
    # Add compiler flags from profile
    cxx_flags = ""
    if build_type == "Debug":
        cxx_flags = profile.get("cxx_flags_debug", "")
    elif build_type == "Release":
        cxx_flags = profile.get("cxx_flags_release", "")
    
    # Add sanitizer flags if specified
    if sanitizer == "asan":
        cxx_flags += " -fsanitize=address"
        cmake_cmd.append("-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address")
        log("Enabling AddressSanitizer")
    elif sanitizer == "tsan":
        cxx_flags += " -fsanitize=thread"
        cmake_cmd.append("-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=thread")
        log("Enabling ThreadSanitizer")
    
    if cxx_flags.strip():
        cmake_cmd.append(f"-DCMAKE_CXX_FLAGS={cxx_flags.strip()}")
    
    # Add extra options from profile
    extra_options = profile.get("cmake_extra_options")
    if extra_options:
        cmake_cmd.extend(extra_options.split())
    
    start_time = time.time()
    outdir.mkdir(parents=True, exist_ok=True)
    
    try:
        run_command(cmake_cmd, capture_output=False)
    except subprocess.CalledProcessError:
        die("CMake configuration failed")
    
    config_duration = int(time.time() - start_time)
    ok(f"{build_type} configuration completed ({config_duration}s)")
    
    if target:
        log(f"Configured for target: {target}")


def cmd_build_like(mode: str, sanitizer: str = None, target: str = None) -> None:
    """Build with specific mode."""
    build_type = "Debug" if mode == DEBUG_SUBDIR else "Release"
    if sanitizer:
        build_type = "Debug"
    
    root = ensure_project_root()
    os.chdir(root)
    
    outdir = get_build_dir(mode)
    total_start_time = time.time()
    
    configure_build(build_type, outdir, sanitizer, target)
    
    # Build
    jobs = get_cpu_count()
    build_cmd = ["cmake", "--build", str(outdir), "--parallel", str(jobs)]
    
    if target:
        build_cmd.extend(["--target", target])
        log(f"Building target '{target}' ({build_type}) with {jobs} parallel jobs...")
    else:
        log(f"Building ({build_type}) with {jobs} parallel jobs...")
    
    if verbose:
        build_cmd.append("--verbose")
    
    build_start_time = time.time()
    try:
        run_command(build_cmd)
    except subprocess.CalledProcessError:
        die("Build failed")
    
    build_duration = int(time.time() - build_start_time)
    total_duration = int(time.time() - total_start_time)
    
    if target:
        ok(f"Target '{target}' build finished: {outdir} (build: {build_duration}s, total: {total_duration}s)")
    else:
        ok(f"Build finished: {outdir} (build: {build_duration}s, total: {total_duration}s)")


def cmd_build(args: argparse.Namespace) -> None:
    """Build debug target."""
    if args.target:
        # Build specific target
        cmd_build_like(DEBUG_SUBDIR, target=args.target)
    else:
        # Build all targets (main, tests, benchmarks) to ensure everything is up to date
        log("Building all targets...")
        cmd_build_like(DEBUG_SUBDIR)


def cmd_release(args: argparse.Namespace) -> None:
    """Build release target."""
    cmd_build_like(RELEASE_SUBDIR, target=args.target)


def cmd_clean(args: argparse.Namespace) -> None:
    """Clean build artifacts."""
    root = ensure_project_root()
    os.chdir(root)
    
    build_dir = Path(BUILD_DIR)
    if build_dir.exists():
        log(f"Removing '{BUILD_DIR}' directory")
        shutil.rmtree(build_dir)
        ok("Cleaned build artifacts")
    else:
        warn(f"Nothing to clean (no '{BUILD_DIR}' directory)")


def cmd_run(args: argparse.Namespace) -> None:
    """Run the debug binary."""
    root = ensure_project_root()
    os.chdir(root)
    
    outdir = get_build_dir(DEBUG_SUBDIR)
    project_name = get_project_name(root)
    
    # Determine binary extension for Windows
    binary_ext = ".exe" if platform.system() == "Windows" else ""
    binary_path = outdir / f"{project_name}{binary_ext}"
    
    needs_rebuild = False
    
    # Check if build directory exists
    if not outdir.exists():
        log("No debug build found. Building first...")
        needs_rebuild = True
    elif not binary_path.exists():
        log("Binary not found. Building first...")
        needs_rebuild = True
    else:
        # Check if any source files are newer than the binary
        source_patterns = [
            f"{SRC_DIR}/**/*.cpp", f"{SRC_DIR}/**/*.cxx", f"{SRC_DIR}/**/*.cc",
            f"{SRC_DIR}/**/*.h", f"{SRC_DIR}/**/*.hpp", f"{SRC_DIR}/**/*.hxx",
            f"{TEST_DIR}/**/*.cpp", f"{TEST_DIR}/**/*.cxx", f"{TEST_DIR}/**/*.cc",
            f"{TEST_DIR}/**/*.h", f"{TEST_DIR}/**/*.hpp", f"{TEST_DIR}/**/*.hxx",
            CMAKELISTS_FILE
        ]
        
        binary_mtime = binary_path.stat().st_mtime
        
        for pattern in source_patterns:
            for source_file in glob.glob(pattern, recursive=True):
                if Path(source_file).stat().st_mtime > binary_mtime:
                    log(f"Source file '{source_file}' is newer than binary. Rebuilding...")
                    needs_rebuild = True
                    break
            if needs_rebuild:
                break
    
    # Rebuild if needed
    if needs_rebuild:
        cmd_build_like(DEBUG_SUBDIR)
    
    # Verify binary exists after potential rebuild
    if not binary_path.exists():
        die(f"Binary not found at '{binary_path}'. Build may have failed.")
    
    log(f"Running {project_name}...")
    
    # Run the binary with any additional arguments
    run_cmd = [str(binary_path)] + (args.args or [])
    try:
        subprocess.run(run_cmd, check=False)
    except KeyboardInterrupt:
        log("Interrupted by user")


def cmd_test(args: argparse.Namespace) -> None:
    """Run tests."""
    root = ensure_project_root()
    os.chdir(root)
    
    outdir = get_build_dir(DEBUG_SUBDIR)
    project_name = get_project_name(root)
    binary_ext = ".exe" if platform.system() == "Windows" else ""
    test_binary = outdir / f"{project_name}_tests{binary_ext}"
    
    needs_rebuild = False
    
    # Check if build directory exists
    if not outdir.exists():
        log("No debug build found. Building first...")
        needs_rebuild = True
    elif not test_binary.exists():
        log("Test binary not found. Building first...")
        needs_rebuild = True
    else:
        # Check if any source files are newer than the test binary
        source_patterns = [
            f"{SRC_DIR}/**/*.cpp", f"{SRC_DIR}/**/*.cxx", f"{SRC_DIR}/**/*.cc",
            f"{SRC_DIR}/**/*.h", f"{SRC_DIR}/**/*.hpp", f"{SRC_DIR}/**/*.hxx",
            f"{TEST_DIR}/**/*.cpp", f"{TEST_DIR}/**/*.cxx", f"{TEST_DIR}/**/*.cc",
            f"{TEST_DIR}/**/*.h", f"{TEST_DIR}/**/*.hpp", f"{TEST_DIR}/**/*.hxx",
            CMAKELISTS_FILE
        ]
        
        test_binary_mtime = test_binary.stat().st_mtime
        
        for pattern in source_patterns:
            for source_file in glob.glob(pattern, recursive=True):
                if Path(source_file).stat().st_mtime > test_binary_mtime:
                    log(f"Source file '{source_file}' is newer than test binary. Rebuilding...")
                    needs_rebuild = True
                    break
            if needs_rebuild:
                break
    
    # Rebuild if needed
    if needs_rebuild:
        cmd_build_like(DEBUG_SUBDIR)
    
    # Verify test binary exists after potential rebuild
    if not test_binary.exists():
        die(f"Test binary not found at '{test_binary}'. Build may have failed.")
    
    # If no arguments provided, use CTest for test discovery and execution
    if not args.args:
        log("Running tests with CTest...")
        try:
            run_command(["ctest", "--output-on-failure"], cwd=outdir)
        except subprocess.CalledProcessError:
            die("Tests failed")
    else:
        log("Running tests with custom arguments...")
        test_cmd = [str(test_binary)] + args.args
        try:
            subprocess.run(test_cmd, check=False)
        except KeyboardInterrupt:
            log("Interrupted by user")


def cmd_bench(args: argparse.Namespace) -> None:
    """Run benchmarks."""
    root = ensure_project_root()
    os.chdir(root)
    
    outdir = get_build_dir(RELEASE_SUBDIR)
    project_name = get_project_name(root)
    binary_ext = ".exe" if platform.system() == "Windows" else ""
    bench_binary = outdir / f"{project_name}_bench{binary_ext}"
    
    needs_rebuild = False
    
    # Check if build directory exists
    if not outdir.exists():
        log("No release build found. Building first...")
        needs_rebuild = True
    elif not bench_binary.exists():
        log("Benchmark binary not found. Building first...")
        needs_rebuild = True
    else:
        # Check if any source files are newer than the benchmark binary
        source_patterns = [
            f"{SRC_DIR}/**/*.cpp", f"{SRC_DIR}/**/*.cxx", f"{SRC_DIR}/**/*.cc",
            f"{SRC_DIR}/**/*.h", f"{SRC_DIR}/**/*.hpp", f"{SRC_DIR}/**/*.hxx",
            f"{BENCH_DIR}/**/*.cpp", f"{BENCH_DIR}/**/*.cxx", f"{BENCH_DIR}/**/*.cc",
            f"{BENCH_DIR}/**/*.h", f"{BENCH_DIR}/**/*.hpp", f"{BENCH_DIR}/**/*.hxx",
            CMAKELISTS_FILE
        ]
        
        bench_binary_mtime = bench_binary.stat().st_mtime
        
        for pattern in source_patterns:
            for source_file in glob.glob(pattern, recursive=True):
                if Path(source_file).stat().st_mtime > bench_binary_mtime:
                    log(f"Source file '{source_file}' is newer than benchmark binary. Rebuilding...")
                    needs_rebuild = True
                    break
            if needs_rebuild:
                break
    
    # Rebuild if needed
    if needs_rebuild:
        cmd_build_like(RELEASE_SUBDIR)
    
    # Verify benchmark binary exists after potential rebuild
    if not bench_binary.exists():
        die(f"Benchmark binary not found at '{bench_binary}'. Build may have failed.")
    
    log("Running benchmarks...")
    bench_cmd = [str(bench_binary)] + (args.args or [])
    try:
        subprocess.run(bench_cmd, check=False)
    except KeyboardInterrupt:
        log("Interrupted by user")


def cmd_asan(args: argparse.Namespace) -> None:
    """Build and run with AddressSanitizer."""
    root = ensure_project_root()
    os.chdir(root)
    
    # Build with AddressSanitizer
    cmd_build_like(ASAN_SUBDIR, "asan")
    
    project_name = get_project_name(root)
    outdir = get_build_dir(ASAN_SUBDIR)
    binary_ext = ".exe" if platform.system() == "Windows" else ""
    binary_path = outdir / f"{project_name}{binary_ext}"
    
    if not binary_path.exists():
        die(f"AddressSanitizer binary not found at '{binary_path}'")
    
    log(f"Running {project_name} with AddressSanitizer...")
    log("Note: AddressSanitizer will detect memory errors, leaks, and buffer overflows")
    
    # Set ASAN environment variables for better output
    env = os.environ.copy()
    env["ASAN_OPTIONS"] = "color=always:print_stats=1:check_initialization_order=1:strict_init_order=1"
    
    run_cmd = [str(binary_path)] + (args.args or [])
    try:
        subprocess.run(run_cmd, env=env, check=False)
    except KeyboardInterrupt:
        log("Interrupted by user")


def cmd_tsan(args: argparse.Namespace) -> None:
    """Build and run with ThreadSanitizer."""
    root = ensure_project_root()
    os.chdir(root)
    
    # Build with ThreadSanitizer
    cmd_build_like(TSAN_SUBDIR, "tsan")
    
    project_name = get_project_name(root)
    outdir = get_build_dir(TSAN_SUBDIR)
    binary_ext = ".exe" if platform.system() == "Windows" else ""
    binary_path = outdir / f"{project_name}{binary_ext}"
    
    if not binary_path.exists():
        die(f"ThreadSanitizer binary not found at '{binary_path}'")
    
    log(f"Running {project_name} with ThreadSanitizer...")
    log("Note: ThreadSanitizer will detect data races and threading issues")
    
    # Set TSAN environment variables for better output
    env = os.environ.copy()
    env["TSAN_OPTIONS"] = "color=always:print_stats=1:halt_on_error=1"
    
    run_cmd = [str(binary_path)] + (args.args or [])
    try:
        subprocess.run(run_cmd, env=env, check=False)
    except KeyboardInterrupt:
        log("Interrupted by user")


def find_cpp_files() -> List[Path]:
    """Find all C++ source and header files."""
    patterns = [
        f"{SRC_DIR}/**/*.cpp", f"{SRC_DIR}/**/*.cxx", f"{SRC_DIR}/**/*.cc",
        f"{SRC_DIR}/**/*.h", f"{SRC_DIR}/**/*.hpp", f"{SRC_DIR}/**/*.hxx",
        f"{TEST_DIR}/**/*.cpp", f"{TEST_DIR}/**/*.cxx", f"{TEST_DIR}/**/*.cc",
        f"{TEST_DIR}/**/*.h", f"{TEST_DIR}/**/*.hpp", f"{TEST_DIR}/**/*.hxx",
        f"{BENCH_DIR}/**/*.cpp", f"{BENCH_DIR}/**/*.cxx", f"{BENCH_DIR}/**/*.cc",
        f"{BENCH_DIR}/**/*.h", f"{BENCH_DIR}/**/*.hpp", f"{BENCH_DIR}/**/*.hxx",
    ]
    
    files = []
    for pattern in patterns:
        files.extend(Path(f) for f in glob.glob(pattern, recursive=True))
    
    return files


def cmd_format(args: argparse.Namespace) -> None:
    """Format C++ code with clang-format."""
    root = ensure_project_root()
    os.chdir(root)
    
    if not shutil.which("clang-format"):
        warn("clang-format not found. Install it to format code.")
        if platform.system() == "Linux":
            warn("Ubuntu/Debian: sudo apt install clang-format")
            warn("Fedora: sudo dnf install clang-tools-extra")
        elif platform.system() == "Darwin":
            warn("macOS: brew install clang-format")
        elif platform.system() == "Windows":
            warn("Windows: Install LLVM or use package manager like chocolatey")
        return
    
    # Create .clang-format if it doesn't exist
    clang_format_file = Path(".clang-format")
    if not clang_format_file.exists():
        log("Creating .clang-format configuration...")
        
        config = """---
BasedOnStyle: Google
IndentWidth: 4
TabWidth: 4
UseTab: Never
ColumnLimit: 100
BreakBeforeBraces: Attach
AllowShortIfStatementsOnASingleLine: true
AllowShortLoopsOnASingleLine: true
AllowShortFunctionsOnASingleLine: All
AllowShortBlocksOnASingleLine: true
KeepEmptyLinesAtTheStartOfBlocks: false
MaxEmptyLinesToKeep: 1
PointerAlignment: Left
ReferenceAlignment: Left
AlignConsecutiveAssignments: false
AlignConsecutiveDeclarations: false
AlignTrailingComments: true
SpaceAfterCStyleCast: false
SpaceBeforeParens: ControlStatements
SpaceInEmptyParentheses: false
SpacesInAngles: false
SpacesInContainerLiterals: false
SpacesInCStyleCastParentheses: false
SpacesInParentheses: false
SpacesInSquareBrackets: false
Standard: c++20
SortIncludes: true
IncludeBlocks: Regroup
"""
        clang_format_file.write_text(config)
        ok(".clang-format created with sensible defaults")
    
    # Find all C++ files
    cpp_files = find_cpp_files()
    
    if not cpp_files:
        warn("No C++ source files found to format")
        return
    
    log(f"Formatting {len(cpp_files)} C++ files...")
    start_time = time.time()
    
    if args.check:
        log("Checking code formatting (dry run)...")
        needs_formatting = False
        
        for file_path in cpp_files:
            try:
                result = run_command(
                    ["clang-format", "--dry-run", "--Werror", str(file_path)],
                    capture_output=True,
                    check=False
                )
                if result.returncode != 0:
                    warn(f"File needs formatting: {file_path}")
                    needs_formatting = True
            except Exception:
                warn(f"Could not check formatting for: {file_path}")
                needs_formatting = True
        
        if needs_formatting:
            warn("Some files need formatting. Run 'fargo format' to fix them.")
            sys.exit(1)
        else:
            ok("All files are properly formatted")
    else:
        # Actually format the files
        for file_path in cpp_files:
            try:
                run_command(["clang-format", "-i", str(file_path)], capture_output=True)
            except Exception:
                warn(f"Could not format file: {file_path}")
        
        format_duration = int(time.time() - start_time)
        ok(f"Code formatting completed ({format_duration}s, {len(cpp_files)} files)")


def cmd_check(args: argparse.Namespace) -> None:
    """Run static analysis."""
    root = ensure_project_root()
    os.chdir(root)
    
    # Ensure we have compile_commands.json
    outdir = get_build_dir(DEBUG_SUBDIR)
    compile_commands = outdir / "compile_commands.json"
    
    if not compile_commands.exists():
        warn("No compile_commands.json found. Building first to generate it...")
        cmd_build_like(DEBUG_SUBDIR)
    
    log("Running static analysis...")
    found_analyzer = False
    has_issues = False
    
    # Run clang-tidy if available
    if shutil.which("clang-tidy"):
        found_analyzer = True
        log("Running clang-tidy analysis...")
        
        cpp_files = find_cpp_files()
        source_files = [f for f in cpp_files if f.suffix in ['.cpp', '.cxx', '.cc']][:20]  # Limit to avoid too much output
        
        if source_files:
            try:
                result = run_command(
                    ["clang-tidy"] + [str(f) for f in source_files] + ["-p", str(outdir)],
                    capture_output=True,
                    check=False
                )
                
                if result.stdout:
                    print(result.stdout)
                    if "warning:" in result.stdout or "error:" in result.stdout:
                        has_issues = True
                else:
                    ok("clang-tidy: No issues found")
            except Exception:
                warn("clang-tidy analysis failed")
    
    # Run cppcheck if available
    if shutil.which("cppcheck"):
        found_analyzer = True
        log("Running cppcheck analysis...")
        
        try:
            result = run_command([
                "cppcheck", "--enable=warning,style,performance,portability",
                "--std=c++20", "--suppress=missingIncludeSystem", "--quiet",
                SRC_DIR, TEST_DIR, BENCH_DIR
            ], capture_output=True, check=False)
            
            if result.stderr:
                print(result.stderr)
                has_issues = True
            else:
                ok("cppcheck: No issues found")
        except Exception:
            warn("cppcheck analysis failed")
    
    if not found_analyzer:
        warn("No static analysis tools found. Install clang-tidy or cppcheck.")
        if platform.system() == "Linux":
            warn("Ubuntu/Debian: sudo apt install clang-tidy cppcheck")
            warn("Fedora: sudo dnf install clang-tools-extra cppcheck")
        elif platform.system() == "Darwin":
            warn("macOS: brew install llvm cppcheck")
        return
    
    if has_issues:
        warn("Static analysis found potential issues")
        sys.exit(1)
    else:
        ok("Static analysis completed - no issues found")


def cmd_doc(args: argparse.Namespace) -> None:
    """Generate documentation with Doxygen."""
    root = ensure_project_root()
    os.chdir(root)
    
    if not shutil.which("doxygen"):
        warn("Doxygen not found. Install it to generate documentation.")
        if platform.system() == "Linux":
            warn("Ubuntu/Debian: sudo apt install doxygen")
            warn("Fedora: sudo dnf install doxygen")
        elif platform.system() == "Darwin":
            warn("macOS: brew install doxygen")
        elif platform.system() == "Windows":
            warn("Windows: Download from doxygen.nl or use package manager")
        return
    
    doc_dir = Path("docs")
    doxyfile = Path("Doxyfile")
    
    doc_dir.mkdir(exist_ok=True)
    
    # Generate Doxyfile if it doesn't exist
    if not doxyfile.exists():
        log("Creating Doxyfile configuration...")
        project_name = get_project_name(root)
        
        config = f"""# Doxyfile for {project_name}
PROJECT_NAME           = "{project_name}"
PROJECT_BRIEF          = "A C++ project built with fargo"
OUTPUT_DIRECTORY       = {doc_dir}
INPUT                  = {SRC_DIR} README.md
RECURSIVE              = YES
EXTRACT_ALL            = YES
EXTRACT_PRIVATE        = YES
EXTRACT_STATIC         = YES
GENERATE_HTML          = YES
GENERATE_LATEX         = NO
HTML_OUTPUT            = html
HTML_COLORSTYLE_HUE    = 220
HTML_COLORSTYLE_SAT    = 100
HTML_COLORSTYLE_GAMMA  = 80
SOURCE_BROWSER         = YES
INLINE_SOURCES         = YES
REFERENCED_BY_RELATION = YES
REFERENCES_RELATION    = YES
CALL_GRAPH             = YES
CALLER_GRAPH           = YES
HAVE_DOT               = YES
DOT_GRAPH_MAX_NODES    = 50
QUIET                  = YES
WARNINGS               = YES
WARN_IF_UNDOCUMENTED   = YES
WARN_IF_DOC_ERROR      = YES
FILE_PATTERNS          = *.cpp *.h *.hpp *.cxx *.cc
EXCLUDE_PATTERNS       = */build/* */.*
USE_MDFILE_AS_MAINPAGE = README.md
MARKDOWN_SUPPORT       = YES
AUTOLINK_SUPPORT       = YES
"""
        doxyfile.write_text(config)
        ok("Doxyfile created. You can customize it for your project needs.")
    
    # Create basic README.md if it doesn't exist
    readme = Path("README.md")
    if not readme.exists():
        project_name = get_project_name(root)
        readme_content = f"""# {project_name}

A C++ project built with fargo.

## Building

```bash
fargo build    # Debug build
fargo release  # Release build
```

## Running

```bash
fargo run      # Run the application
fargo test     # Run tests
fargo bench    # Run benchmarks
```

## Documentation

```bash
fargo doc      # Generate documentation
```

## Analysis

```bash
fargo check    # Static analysis
fargo asan     # AddressSanitizer
fargo tsan     # ThreadSanitizer
```
"""
        readme.write_text(readme_content)
        ok("README.md created with basic project information.")
    
    log("Generating documentation with Doxygen...")
    start_time = time.time()
    
    try:
        run_command(["doxygen", str(doxyfile)], capture_output=not verbose)
    except subprocess.CalledProcessError:
        die("Documentation generation failed")
    
    doc_duration = int(time.time() - start_time)
    
    index_file = doc_dir / "html" / "index.html"
    if index_file.exists():
        ok(f"Documentation generated successfully ({doc_duration}s)")
        log(f"Open {index_file} in your browser to view the documentation")
        
        # Try to open documentation in browser
        if platform.system() == "Darwin":
            subprocess.run(["open", str(index_file)], check=False)
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", str(index_file)], check=False)
        elif platform.system() == "Windows":
            subprocess.run(["start", str(index_file)], shell=True, check=False)
    else:
        warn("Documentation generation may have failed. Check Doxyfile configuration.")


def cmd_targets(args: argparse.Namespace) -> None:
    """List available build targets."""
    root = ensure_project_root()
    os.chdir(root)
    
    outdir = get_build_dir(DEBUG_SUBDIR)
    
    if outdir.exists():
        log("Available build targets:")
        
        # Try to get targets from build system
        if (outdir / "build.ninja").exists() and shutil.which("ninja"):
            try:
                result = run_command(["ninja", "-C", str(outdir), "-t", "targets"], capture_output=True)
                targets = []
                for line in result.stdout.splitlines():
                    if ':' in line and not line.startswith('#'):
                        target = line.split(':')[0]
                        targets.append(target)
                
                for target in sorted(set(targets)):
                    print(f"  {target}")
            except Exception:
                warn("Could not get targets from ninja")
        
        elif (outdir / "Makefile").exists():
            try:
                result = run_command(["make", "-C", str(outdir), "help"], capture_output=True, check=False)
                for line in result.stdout.splitlines():
                    if line.startswith("..."):
                        target = line[3:].strip()
                        print(f"  {target}")
            except Exception:
                warn("Could not get targets from make")
        else:
            warn("No build system found. Run 'fargo build' first.")
    else:
        warn("No build directory found. Run 'fargo build' first.")
        log("Expected targets based on CMakeLists.txt:")
        project_name = get_project_name(root)
        print(f"  {project_name} (main executable)")
        print(f"  {project_name}_tests (unit tests)")
        print(f"  {project_name}_bench (benchmarks)")


def main() -> None:
    """Main entry point."""
    global verbose, current_profile
    
    parser = argparse.ArgumentParser(
        description="fargo - tiny C++ project bootstrap/build helper (Cargo-like)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  fargo new myapp
  cd myapp && fargo build
  fargo build myapp_tests     # Build specific target
  fargo run
  fargo -v build              # Build with verbose output
  fargo -v run                # Run with verbose build output
  fargo -p release build      # Use 'release' profile
  fargo test                  # Run all tests with CTest
  fargo test -- --gtest_filter=MyTest*       # Run specific tests
  fargo test -- --gtest_repeat=5             # Run tests multiple times
  fargo check                 # Run static analysis
  fargo format                # Format all C++ files
  fargo format --check        # Check formatting (dry run)
  fargo asan                  # Build and run with AddressSanitizer
  fargo tsan                  # Build and run with ThreadSanitizer
  fargo doc                   # Generate documentation
  fargo bench                 # Run all benchmarks
  fargo bench -- --benchmark_filter=MyBench  # Run specific benchmark
  fargo bench -- --benchmark_min_time=5s     # Run with custom timing
  fargo release
  fargo clean
  fargo profile list          # List configuration profiles
  fargo profile new myprofile # Create custom profile
  fargo targets               # List available build targets

Version: {__version__}
"""
    )
    
    parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output")
    parser.add_argument("-p", "--profile", help="Use specific configuration profile")
    parser.add_argument("--version", action="version", version=f"fargo {__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # new command
    new_parser = subparsers.add_parser("new", help="Create a new C++ project")
    new_parser.add_argument("name", nargs="?", help="Project name")
    
    # build command
    build_parser = subparsers.add_parser("build", help="Build debug target")
    build_parser.add_argument("target", nargs="?", help="Specific target to build")
    
    # release command
    release_parser = subparsers.add_parser("release", help="Build release target")
    release_parser.add_argument("target", nargs="?", help="Specific target to build")
    
    # run command
    run_parser = subparsers.add_parser("run", aliases=["r"], help="Run the debug binary")
    run_parser.add_argument("args", nargs="*", help="Arguments to pass to the binary")
    
    # test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("args", nargs="*", help="Arguments to pass to the test binary (use -- to separate fargo options from test options)")
    
    # bench command
    bench_parser = subparsers.add_parser("bench", help="Run benchmarks")
    bench_parser.add_argument("args", nargs="*", help="Arguments to pass to the benchmark binary (use -- to separate fargo options from benchmark options)")
    
    # check command
    subparsers.add_parser("check", help="Run static analysis")
    
    # format command
    format_parser = subparsers.add_parser("format", help="Format C++ code with clang-format")
    format_parser.add_argument("-c", "--check", action="store_true", help="Check formatting without making changes")
    
    # asan command
    asan_parser = subparsers.add_parser("asan", help="Build and run with AddressSanitizer")
    asan_parser.add_argument("args", nargs="*", help="Arguments to pass to the binary")
    
    # tsan command
    tsan_parser = subparsers.add_parser("tsan", help="Build and run with ThreadSanitizer")
    tsan_parser.add_argument("args", nargs="*", help="Arguments to pass to the binary")
    
    # doc command
    subparsers.add_parser("doc", help="Generate documentation with Doxygen")
    
    # clean command
    subparsers.add_parser("clean", help="Remove build directory")
    
    # profile command
    profile_parser = subparsers.add_parser("profile", help="Manage configuration profiles")
    profile_parser.add_argument("action", nargs="?", choices=["list", "ls", "init", "new", "create", "show"], 
                                help="Profile action")
    profile_parser.add_argument("profile_name", nargs="?", help="Profile name")
    
    # targets command
    subparsers.add_parser("targets", help="List available build targets")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Set global options
    verbose = args.verbose
    if args.profile:
        current_profile = args.profile
    
    # Dispatch to command handlers
    command_map = {
        "new": cmd_new,
        "build": cmd_build,
        "release": cmd_release,
        "run": cmd_run,
        "r": cmd_run,
        "test": cmd_test,
        "bench": cmd_bench,
        "check": cmd_check,
        "format": cmd_format,
        "asan": cmd_asan,
        "tsan": cmd_tsan,
        "doc": cmd_doc,
        "clean": cmd_clean,
        "profile": cmd_profile,
        "targets": cmd_targets,
    }
    
    if args.command in command_map:
        try:
            command_map[args.command](args)
        except KeyboardInterrupt:
            log("Interrupted by user")
            sys.exit(1)
        except Exception as e:
            if verbose:
                import traceback
                traceback.print_exc()
            die(f"Unexpected error: {e}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
