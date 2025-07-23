# Makefile for fargo C++ project manager
#
# Usage:
#   make install          # Install system-wide (requires sudo)
#   make install-user     # Install to user directory
#   make uninstall        # Remove system installation
#   make uninstall-user   # Remove user installation
#

SCRIPT_NAME := fargo
PREFIX := /usr/local
BINDIR := $(PREFIX)/bin
USER_BINDIR := $(HOME)/.local/bin

.PHONY: help install install-user uninstall uninstall-user check

help:
	@echo "fargo installation targets:"
	@echo "  install          Install system-wide to $(BINDIR) (requires sudo)"
	@echo "  install-user     Install to user directory $(USER_BINDIR)"
	@echo "  uninstall        Remove system installation"
	@echo "  uninstall-user   Remove user installation"
	@echo "  check            Check system requirements"
	@echo ""
	@echo "Examples:"
	@echo "  make install              # System-wide installation"
	@echo "  make install-user         # User installation"
	@echo "  make PREFIX=/opt install  # Custom prefix"

check:
	@echo "Checking system requirements..."
	@command -v bash >/dev/null 2>&1 || { echo "ERROR: bash not found"; exit 1; }
	@command -v cmake >/dev/null 2>&1 || { echo "ERROR: cmake not found"; exit 1; }
	@(command -v g++ >/dev/null 2>&1 || command -v clang++ >/dev/null 2>&1) || { echo "ERROR: C++ compiler not found"; exit 1; }
	@(command -v ninja >/dev/null 2>&1 || command -v make >/dev/null 2>&1) || { echo "ERROR: build system not found"; exit 1; }
	@echo "All requirements satisfied"

install: check
	@echo "Installing $(SCRIPT_NAME) to $(BINDIR)..."
	@test -f $(SCRIPT_NAME) || { echo "ERROR: $(SCRIPT_NAME) script not found"; exit 1; }
	@mkdir -p $(BINDIR)
	@cp $(SCRIPT_NAME) $(BINDIR)/$(SCRIPT_NAME)
	@chmod +x $(BINDIR)/$(SCRIPT_NAME)
	@echo "$(SCRIPT_NAME) installed successfully to $(BINDIR)/$(SCRIPT_NAME)"
	@echo ""
	@echo "Try it out:"
	@echo "  fargo new myproject"
	@echo "  cd myproject"
	@echo "  fargo build && fargo run"

install-user: check
	@echo "Installing $(SCRIPT_NAME) to $(USER_BINDIR)..."
	@test -f $(SCRIPT_NAME) || { echo "ERROR: $(SCRIPT_NAME) script not found"; exit 1; }
	@mkdir -p $(USER_BINDIR)
	@cp $(SCRIPT_NAME) $(USER_BINDIR)/$(SCRIPT_NAME)
	@chmod +x $(USER_BINDIR)/$(SCRIPT_NAME)
	@echo "$(SCRIPT_NAME) installed successfully to $(USER_BINDIR)/$(SCRIPT_NAME)"
	@echo ""
	@if echo "$$PATH" | grep -q "$(USER_BINDIR)"; then \
		echo "$(USER_BINDIR) is already in your PATH"; \
	else \
		echo "Add $(USER_BINDIR) to your PATH:"; \
		echo "  export PATH=\"$(USER_BINDIR):\$$PATH\""; \
		echo ""; \
		echo "Add this to your shell profile (~/.bashrc, ~/.zshrc, etc.)"; \
	fi
	@echo ""
	@echo "Try it out:"
	@echo "  fargo new myproject"
	@echo "  cd myproject"
	@echo "  fargo build && fargo run"

uninstall:
	@echo "Removing $(SCRIPT_NAME) from $(BINDIR)..."
	@rm -f $(BINDIR)/$(SCRIPT_NAME)
	@echo "$(SCRIPT_NAME) uninstalled"

uninstall-user:
	@echo "Removing $(SCRIPT_NAME) from $(USER_BINDIR)..."
	@rm -f $(USER_BINDIR)/$(SCRIPT_NAME)
	@echo "$(SCRIPT_NAME) uninstalled"
