#!/usr/bin/env bats

load '../test_helper'

setup() {
    common_setup
    export OLD_HOME="$HOME"
    export HOME="$BATS_TMPDIR/fake_home"
    mkdir -p "$HOME"
    
    export SCRIPT_ROOT_DIR="$HOME/.myshell_rfd"
    export SCRIPT_CONFIG_FILE="$SCRIPT_ROOT_DIR/config"
    mkdir -p "$SCRIPT_ROOT_DIR"
    
    source "$PROJECT_ROOT/src/core/utils.sh"
    
    # Mock UI
    prompt_yes_no() {
         if [ "$RESPONSE" == "y" ]; then return 0; else return 1; fi
    }
    lecho() { :; }
    print_header() { :; }
    
    # Source modules
    source "$PROJECT_ROOT/src/modules/infracost.sh"
    source "$PROJECT_ROOT/src/modules/sops.sh"
}

teardown() {
    common_teardown
    export HOME="$OLD_HOME"
    rm -rf "$BATS_TMPDIR/fake_home"
}

@test "configure_infracost adds Infracost completion if approved" {
    mock_command "infracost" "echo 1"
    export RESPONSE="y"
    run configure_infracost
    grep "source <(infracost completion --shell zsh); compdef _infracost infracost" "$SCRIPT_CONFIG_FILE"
}

@test "configure_sops adds SOPS completion if approved" {
    mock_command "sops" "echo 1"
    export RESPONSE="y"
    run configure_sops
    grep "source <(sops completion zsh)" "$SCRIPT_CONFIG_FILE"
}
