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
    enable_omz_plugin() {
        echo "$1" >> "$MOCK_BIN_DIR/omz_plugins.log"
    }

    source "$PROJECT_ROOT/src/modules/fzf.sh"
    source "$PROJECT_ROOT/src/modules/k_plugin.sh"
    source "$PROJECT_ROOT/src/modules/zsh_plugins.sh"
}

teardown() {
    common_teardown
    export HOME="$OLD_HOME"
    rm -rf "$BATS_TMPDIR/fake_home"
}

# --- FZF ---

@test "configure_fzf skips when dir already exists" {
    local fzf_dir="$HOME/.oh-my-zsh/custom/fzf"
    mkdir -p "$fzf_dir"

    run configure_fzf
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}

@test "configure_fzf skips when user declines" {
    export RESPONSE="n"
    run configure_fzf
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}

@test "configure_fzf installs and adds config if approved" {
    local fzf_dir="$HOME/.oh-my-zsh/custom/fzf"

    mock_command "git" "
        target=\"\${@: -1}\"
        mkdir -p \"\$target\"
        printf '#!/bin/bash\ntouch \"\$HOME/.fzf.zsh\"\n' > \"\$target/install\"
        chmod +x \"\$target/install\"
    "

    export RESPONSE="y"
    run configure_fzf

    grep "fzf.zsh" "$SCRIPT_CONFIG_FILE"
}

# --- K_Plugin ---

@test "configure_k_plugin skips when dir already exists" {
    local k_dir="$HOME/.oh-my-zsh/custom/plugins/k"
    mkdir -p "$k_dir"

    run configure_k_plugin
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}

@test "configure_k_plugin skips when user declines" {
    export RESPONSE="n"
    run configure_k_plugin
    [ ! -f "$SCRIPT_CONFIG_FILE" ]
}

@test "configure_k_plugin installs if approved" {
    local k_dir="$HOME/.oh-my-zsh/custom/plugins/k"

    mock_command "git" "
        target=\"\${@: -1}\"
        mkdir -p \"\$target\"
        echo 'k () {' > \"\$target/k.sh\"
    "
    mock_command "sed" "echo sed called"

    export RESPONSE="y"
    run configure_k_plugin

    grep "k.sh" "$SCRIPT_CONFIG_FILE"
    grep "alias f='z -ha'" "$SCRIPT_CONFIG_FILE"
}

# --- ZSH Plugins ---

@test "configure_plugin skips when dir already exists" {
    local plugin_dir="$HOME/.oh-my-zsh/custom/plugins/zsh-autosuggestions"
    mkdir -p "$plugin_dir"

    run configure_plugin "zsh-autosuggestions" "https://github.com/zsh-users/zsh-autosuggestions" "zsh-autosuggestions"
    [ ! -f "$MOCK_BIN_DIR/omz_plugins.log" ]
}

@test "configure_plugin skips when user declines" {
    export RESPONSE="n"
    run configure_plugin "zsh-autosuggestions" "https://github.com/zsh-users/zsh-autosuggestions" "zsh-autosuggestions"
    [ ! -f "$MOCK_BIN_DIR/omz_plugins.log" ]
}

@test "configure_plugin installs and enables plugin if approved" {
    mock_command "git" 'mkdir -p "${@: -1}"'

    export RESPONSE="y"
    run configure_plugin "zsh-autosuggestions" "https://github.com/zsh-users/zsh-autosuggestions" "zsh-autosuggestions"

    assert_command_called "git"
    grep "zsh-autosuggestions" "$MOCK_BIN_DIR/omz_plugins.log"
}
