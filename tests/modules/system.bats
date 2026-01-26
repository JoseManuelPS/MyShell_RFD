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
    
    # Mock enable_omz_plugin as it might be missing or in another file
    enable_omz_plugin() {
        echo "Enabled plugin $1" >> "$MOCK_BIN_DIR/omz_plugins.log"
    }

    # Source modules
    source "$PROJECT_ROOT/src/modules/containers.sh"
    source "$PROJECT_ROOT/src/modules/vcs.sh"
    source "$PROJECT_ROOT/src/modules/nvm.sh"
    source "$PROJECT_ROOT/src/modules/p10k.sh"
}

teardown() {
    common_teardown
    export HOME="$OLD_HOME"
    rm -rf "$BATS_TMPDIR/fake_home"
}

@test "configure_docker enables plugin" {
    mock_command "docker" "echo 1"
    export RESPONSE="y"
    run configure_docker
    grep "Enabled plugin docker" "$MOCK_BIN_DIR/omz_plugins.log"
}

@test "configure_podman adds completion and alias" {
    mock_command "podman" "echo 1"
    export RESPONSE="y"
    run configure_podman
    grep "source <(podman completion zsh)" "$SCRIPT_CONFIG_FILE"
    grep "alias docker=podman" "$SCRIPT_CONFIG_FILE"
}

@test "configure_github adds completion" {
    mock_command "gh" "echo 1"
    export RESPONSE="y"
    run configure_github
    grep "gh completion -s zsh" "$SCRIPT_CONFIG_FILE"
}

@test "configure_gitlab adds completion" {
    mock_command "glab" "echo 1"
    export RESPONSE="y"
    run configure_gitlab
    grep "glab completion -s zsh" "$SCRIPT_CONFIG_FILE"
}

@test "configure_nvm adds config if dir exists" {
    mkdir -p "$HOME/.nvm"
    export RESPONSE="y"
    run configure_nvm
    grep "export NVM_DIR=\"\$HOME/.nvm\"" "$SCRIPT_CONFIG_FILE"
}

@test "configure_p10k installs and updates zshrc" {
    local zshrc="$HOME/.zshrc"
    echo 'ZSH_THEME="robbyrussell"' > "$zshrc"
    mock_command "git" "mkdir -p $BATS_TMPDIR/fake_home/.oh-my-zsh/custom/themes/powerlevel10k"
    
    export RESPONSE="y"
    run configure_p10k
    
    grep 'ZSH_THEME="powerlevel10k/powerlevel10k"' "$zshrc"
    grep "PowerLevel10K" "$SCRIPT_CONFIG_FILE"
}
