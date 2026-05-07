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

    prompt_yes_no() {
        if [ "$RESPONSE" == "y" ]; then return 0; else return 1; fi
    }
    lecho() { :; }
    print_header() { :; }

    source "$PROJECT_ROOT/src/modules/eksctl.sh"
    source "$PROJECT_ROOT/src/modules/minikube.sh"
    source "$PROJECT_ROOT/src/modules/oc.sh"
    source "$PROJECT_ROOT/src/modules/rosa.sh"
    source "$PROJECT_ROOT/src/modules/tridentctl.sh"
}

teardown() {
    common_teardown
    export HOME="$OLD_HOME"
    rm -rf "$BATS_TMPDIR/fake_home"
}

# --- Eksctl ---

@test "configure_eksctl adds completion if approved" {
    mock_command "eksctl" "echo 1"
    export RESPONSE="y"
    run configure_eksctl
    grep "source <(eksctl completion zsh)" "$SCRIPT_CONFIG_FILE"
}

@test "configure_eksctl skips when binary missing" {
    run configure_eksctl
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}

@test "configure_eksctl skips when user declines" {
    mock_command "eksctl" "echo 1"
    export RESPONSE="n"
    run configure_eksctl
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}

# --- Minikube ---

@test "configure_minikube adds completion if approved" {
    mock_command "minikube" "echo 1"
    export RESPONSE="y"
    run configure_minikube
    grep "source <(minikube completion zsh)" "$SCRIPT_CONFIG_FILE"
}

@test "configure_minikube skips when binary missing" {
    run configure_minikube
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}

@test "configure_minikube skips when user declines" {
    mock_command "minikube" "echo 1"
    export RESPONSE="n"
    run configure_minikube
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}

# --- OC (OpenShift) ---

@test "configure_oc adds completion if approved" {
    mock_command "oc" "echo 1"
    export RESPONSE="y"
    run configure_oc
    grep "source <(oc completion zsh)" "$SCRIPT_CONFIG_FILE"
}

@test "configure_oc skips when binary missing" {
    run configure_oc
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}

@test "configure_oc skips when user declines" {
    mock_command "oc" "echo 1"
    export RESPONSE="n"
    run configure_oc
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}

# --- Rosa ---

@test "configure_rosa adds completion if approved" {
    mock_command "rosa" "echo 1"
    export RESPONSE="y"
    run configure_rosa
    grep "source <(rosa completion zsh" "$SCRIPT_CONFIG_FILE"
}

@test "configure_rosa skips when binary missing" {
    run configure_rosa
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}

@test "configure_rosa skips when user declines" {
    mock_command "rosa" "echo 1"
    export RESPONSE="n"
    run configure_rosa
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}

# --- Tridentctl ---

@test "configure_tridentctl adds completion and alias if approved" {
    mock_command "tridentctl" "echo 1"
    export RESPONSE="y"
    run configure_tridentctl
    grep "source <(tridentctl completion zsh)" "$SCRIPT_CONFIG_FILE"
    grep "alias astra='tridentctl -n trident'" "$SCRIPT_CONFIG_FILE"
}

@test "configure_tridentctl skips when binary missing" {
    run configure_tridentctl
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}

@test "configure_tridentctl skips when user declines" {
    mock_command "tridentctl" "echo 1"
    export RESPONSE="n"
    run configure_tridentctl
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}
