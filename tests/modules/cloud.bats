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
    source "$PROJECT_ROOT/src/modules/aws.sh"
    source "$PROJECT_ROOT/src/modules/terraform.sh"
    source "$PROJECT_ROOT/src/modules/helm.sh"
}

teardown() {
    common_teardown
    export HOME="$OLD_HOME"
    rm -rf "$BATS_TMPDIR/fake_home"
}

@test "configure_aws adds completion if approved" {
    mock_command "aws" "echo 1"
    export RESPONSE="y"
    run configure_aws
    grep "complete -C '/usr/local/bin/aws_completer' aws" "$SCRIPT_CONFIG_FILE"
}

@test "configure_terraform adds completion and alias" {
    mock_command "terraform" "echo 1"
    export RESPONSE="y"
    run configure_terraform
    grep "alias t='terraform'" "$SCRIPT_CONFIG_FILE"
    grep "alias ti='terraform init'" "$SCRIPT_CONFIG_FILE"
    grep "alias tp='terraform plan'" "$SCRIPT_CONFIG_FILE"
    grep "alias ta='terraform apply'" "$SCRIPT_CONFIG_FILE"
    grep "complete -o nospace -C /usr/local/bin/terraform terraform" "$SCRIPT_CONFIG_FILE"
}

@test "configure_opentofu adds completion and alias" {
    mock_command "opentofu" "echo 1"
    export RESPONSE="y"
    run configure_opentofu
    grep "alias ot='opentofu'" "$SCRIPT_CONFIG_FILE"
    grep "alias oti='opentofu init'" "$SCRIPT_CONFIG_FILE"
    grep "alias otp='opentofu plan'" "$SCRIPT_CONFIG_FILE"
    grep "alias ota='opentofu apply'" "$SCRIPT_CONFIG_FILE"
    grep "alias otd='opentofu destroy'" "$SCRIPT_CONFIG_FILE"
    grep "alias otv='opentofu validate'" "$SCRIPT_CONFIG_FILE"
    grep "alias otfmt='opentofu fmt'" "$SCRIPT_CONFIG_FILE"
    grep "alias oto='opentofu output'" "$SCRIPT_CONFIG_FILE"
    grep "alias ots='opentofu state'" "$SCRIPT_CONFIG_FILE"
    grep "complete -o nospace -C /usr/local/bin/opentofu opentofu" "$SCRIPT_CONFIG_FILE"
}

@test "configure_helm adds completion" {
    mock_command "helm" "echo 1"
    export RESPONSE="y"
    run configure_helm
    grep "source <(helm completion zsh)" "$SCRIPT_CONFIG_FILE"
}
