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
    
    source "$PROJECT_ROOT/src/modules/tools.sh"
}

teardown() {
    common_teardown
    export HOME="$OLD_HOME"
    rm -rf "$BATS_TMPDIR/fake_home"
}

@test "configure_batcat leverages batcat if present" {
    mock_command "batcat" "echo 1"
    # bat is missing by default (no mock)
    export RESPONSE="y"
    
    run configure_batcat
    
    grep "alias cat='batcat'" "$SCRIPT_CONFIG_FILE"
}

@test "configure_batcat leverages bat if batcat missing" {
    # Override check_binary to force batcat missing
    check_binary() {
        if [ "$1" == "batcat" ]; then return 1; fi
        command -v "$1" >/dev/null 2>&1
    }

    mock_command "bat" "echo 1"
    export RESPONSE="y"
    
    run configure_batcat
    
    grep "alias cat='bat'" "$SCRIPT_CONFIG_FILE"
}

@test "configure_pls adds sudo alias" {
    mock_command "sudo" "echo sudo"
    export RESPONSE="y"
    
    run configure_pls
    
    grep "## Section: PLS" "$SCRIPT_CONFIG_FILE"
    grep "function pls() { sudo" "$SCRIPT_CONFIG_FILE"
}

@test "configure_python creates venv if missing" {
    mock_command "python3" '
        if [ "$1" == "-m" ] && [ "$2" == "venv" ]; then
            mkdir -p "$3"
            mkdir -p "$3/bin"
            touch "$3/bin/activate"
        fi
    '
    
    export RESPONSE="y" # Yes to activate, Yes to create
    
    run configure_python
    
    # venv should be created
    [ -d "$HOME/.py-venv-default" ]
    [ -f "$HOME/.py-venv-default/bin/activate" ]
    
    # config added
    grep "source $HOME/.py-venv-default/bin/activate" "$SCRIPT_CONFIG_FILE"
    
    assert_command_called "python3"
}

@test "configure_python uses existing venv" {
    mock_command "python3" "echo python"
    
    # Pre-create venv
    mkdir -p "$HOME/.py-venv-default/bin"
    touch "$HOME/.py-venv-default/bin/activate"
    
    export RESPONSE="y"
    
    run configure_python
    
    # Should find it and just add config, no create
    grep "source $HOME/.py-venv-default/bin/activate" "$SCRIPT_CONFIG_FILE"
}
