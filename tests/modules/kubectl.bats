#!/usr/bin/env bats

load '../test_helper'

setup() {
    common_setup
    export OLD_HOME="$HOME"
    export HOME="$BATS_TMPDIR/fake_home"
    mkdir -p "$HOME"
    
    # Mock SCRIPT_CONFIG_FILE as utils.sh uses it
    export SCRIPT_ROOT_DIR="$HOME/.myshell_rfd"
    export SCRIPT_CONFIG_FILE="$SCRIPT_ROOT_DIR/config"
    mkdir -p "$SCRIPT_ROOT_DIR"
    
    # Source Utils (we need add_to_config, check_binary)
    # We assume utils.sh is correct (tested separately)
    source "$PROJECT_ROOT/src/core/utils.sh"
    
    # Mock UI functions
    # We allow controlling the response via export RESPONSE
    prompt_yes_no() {
        if [ "$RESPONSE" == "y" ]; then return 0; else return 1; fi
    }
    
    lecho() { :; }
    print_header() { :; }
    
    # Source the module under test
    source "$PROJECT_ROOT/src/modules/kubectl.sh"
    
    # Common Mocks
    mock_command "uname" 'if [ "$1" == "-m" ]; then echo x86_64; else echo Linux; fi'
}

teardown() {
    common_teardown
    export HOME="$OLD_HOME"
    rm -rf "$BATS_TMPDIR/fake_home"
}

@test "configure_kubectl does nothing if kubectl missing" {
    # No mock_command for kubectl -> check_binary fails
    run configure_kubectl
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}

@test "configure_kubectl adds aliases if approved" {
    mock_command "kubectl" "echo 1.0"
    export RESPONSE="y" # Approve aliases, Approve Krew
    
    # Mock Krew installation dependencies to avoid errors
    mock_command "curl" "exit 1" # Fail download to skip install part logic for this test
    
    run configure_kubectl
    
    [ -f "$SCRIPT_CONFIG_FILE" ]
    run grep "## Section: Kubectl" "$SCRIPT_CONFIG_FILE"
    [ "$status" -eq 0 ]
    run grep "alias k=kubectl" "$SCRIPT_CONFIG_FILE"
    [ "$status" -eq 0 ]
}

@test "configure_kubectl skips aliases if denied" {
    mock_command "kubectl" "echo 1.0"
    export RESPONSE="n" # Deny
    
    run configure_kubectl
    
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}

@test "install_krew downloads and installs" {
    mock_command "kubectl" "echo 1.0"
    mock_command "tar" "echo tar"
    
    # Complex mock for curl to simulate downloading and creating the installer
    mock_command "curl" '
        echo "Mock Curl Downloading..."
        # Create the dummy installer file that the script expects
        # Name depends on uname mock: krew-linux_amd64
        echo "#!/bin/bash" > krew-linux_amd64
        echo "echo Krew Installer Running" >> krew-linux_amd64
        chmod +x krew-linux_amd64
        touch krew-linux_amd64.tar.gz
        exit 0
    '
    
    export RESPONSE="y" # Yes to aliases, Yes to Krew
    # Note: prompt_yes_no is called twice. 
    # Logic: if RESPONSE=y, it returns 0 (yes) always.
    
    run configure_kubectl
    
    assert_command_called "curl"
    
    # Check if config was updated with krew path
    run grep "## Section: Krew" "$SCRIPT_CONFIG_FILE"
    [ "$status" -eq 0 ]

    # Verify plugins were installed individually
    run grep "krew install ai" "$MOCK_BIN_DIR/kubectl.log"
    [ "$status" -eq 0 ]
    run grep "krew install ns" "$MOCK_BIN_DIR/kubectl.log"
    [ "$status" -eq 0 ]
    run grep "krew install keda" "$MOCK_BIN_DIR/kubectl.log"
    [ "$status" -eq 0 ]
}
