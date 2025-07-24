# Makefile for fargo C++ project manager
#
# Usage:
#   make install          # Install system-wide (requires sudo on Unix)
#   make install-user     # Install to user directory
#   make uninstall        # Remove system installation
#   make uninstall-user   # Remove user installation
#

PYTHON := python3
INSTALLER := install.py
SCRIPT_NAME := fargo.py

# Detect if we have python3, fallback to python
ifeq ($(shell which python3 2>/dev/null),)
	PYTHON := python
endif

.PHONY: help install install-user uninstall uninstall-user check test-install

help:
	@echo "fargo installation targets:"
	@echo "  install          Install system-wide (requires sudo on Unix, Admin on Windows)"
	@echo "  install-user     Install to user directory"
	@echo "  uninstall        Remove system installation"
	@echo "  uninstall-user   Remove user installation"
	@echo "  check            Check system requirements"
	@echo "  test-install     Test installation in current directory"
	@echo ""
	@echo "Examples:"
	@echo "  make install              # System-wide installation"
	@echo "  make install-user         # User installation"
	@echo "  make check                # Check requirements only"
	@echo ""
	@echo "Cross-platform installation (recommended):"
	@echo "  $(PYTHON) $(INSTALLER) --help    # Show all installation options"

check:
	@echo "Checking system requirements..."
	@$(PYTHON) $(INSTALLER) --check

install: check
	@echo "Installing $(SCRIPT_NAME) system-wide..."
	@$(PYTHON) $(INSTALLER)

install-user: check
	@echo "Installing $(SCRIPT_NAME) to user directory..."
	@$(PYTHON) $(INSTALLER) --user

uninstall:
	@echo "Uninstalling $(SCRIPT_NAME) from system..."
	@$(PYTHON) $(INSTALLER) --uninstall

uninstall-user:
	@echo "Uninstalling $(SCRIPT_NAME) from user directory..."
	@$(PYTHON) $(INSTALLER) --uninstall --user

test-install:
	@echo "Testing fargo in current directory..."
	@test -f $(SCRIPT_NAME) || { echo "ERROR: $(SCRIPT_NAME) not found"; exit 1; }
	@$(PYTHON) $(SCRIPT_NAME) --version
	@echo "fargo test successful"
