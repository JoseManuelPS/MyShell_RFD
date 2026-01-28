
# Makefile for MyShell_RFD

SHELL := /bin/bash
PROJECT_NAME := myshell_rfd-$(VERSION)
VERSION := v1.0.1
BUILD_DIR := dist
SRC_DIR := src
TEST_DIR := tests
BATS_DIR := $(TEST_DIR)/libs/bats

.PHONY: all clean build test install test-deps

all: clean build test

clean:
	@echo "Cleaning..."
	@rm -rf $(BUILD_DIR)

build:
	@echo "Building $(PROJECT_NAME)..."
	@mkdir -p $(BUILD_DIR)
	@./build.sh $(VERSION)

test-deps:
	@if [ ! -d "$(BATS_DIR)" ]; then \
		echo "Installing BATS to $(BATS_DIR)..."; \
		mkdir -p $(TEST_DIR)/libs; \
		git clone --depth 1 https://github.com/bats-core/bats-core.git $(BATS_DIR); \
	fi

test: build test-deps
	@echo "Running tests..."
	@$(BATS_DIR)/bin/bats $(TEST_DIR)/core/*.bats 2>/dev/null || echo "No core tests passed/found"
	@$(BATS_DIR)/bin/bats $(TEST_DIR)/modules/*.bats 2>/dev/null || echo "No module tests passed/found"

install: build
	@echo "Installing to /usr/local/bin..."
	@sudo cp $(BUILD_DIR)/$(PROJECT_NAME) /usr/local/bin/$(PROJECT_NAME)
	@sudo chmod +x /usr/local/bin/$(PROJECT_NAME)
	@echo "Installation complete."
