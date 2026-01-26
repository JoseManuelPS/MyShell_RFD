#!/usr/bin/env bats

load '../test_helper'

setup() {
    common_setup
    # Override HOME to prevent touching real config
    export OLD_HOME="$HOME"
    export HOME="$BATS_TMPDIR/fake_home"
    mkdir -p "$HOME"
    
    # We need to source the file AFTER setting HOME because it sets variables based on HOME at top level
    source "$PROJECT_ROOT/src/core/utils.sh"
    
    # Needs lecho to be defined or mocked, as utils.sh calls it
    # We can mock lecho
    lecho() {
        echo "$1: $2"
    }
}

teardown() {
    common_teardown
    export HOME="$OLD_HOME"
    rm -rf "$BATS_TMPDIR/fake_home"
}

@test "init_config creates directories and file" {
    run init_config
    [ "$status" -eq 0 ]
    [ -d "$SCRIPT_ROOT_DIR" ]
    [ -d "$SCRIPT_BACKUP_DIR" ]
    [ -f "$SCRIPT_CONFIG_FILE" ]
    run grep "MyShell_RFD Configuration" "$SCRIPT_CONFIG_FILE"
    [ "$status" -eq 0 ]
}

@test "init_config is idempotent" {
    init_config
    echo "Dummy content" >> "$SCRIPT_CONFIG_FILE"
    
    run init_config
    [ "$status" -eq 0 ]
    # Should not have overwritten
    run grep "Dummy content" "$SCRIPT_CONFIG_FILE"
    [ "$status" -eq 0 ]
}

@test "check_binary returns 0 if binary exists" {
    mock_command "fake_tool" "echo 'I exist'"
    run check_binary "fake_tool"
    [ "$status" -eq 0 ]
}

@test "check_binary returns 1 if binary missing" {
    run check_binary "non_existent_tool_xyz"
    [ "$status" -ne 0 ]
}

@test "add_to_config appends content if section missing" {
    init_config
    run add_to_config "TEST_SECTION" "key=value"
    
    [ "$status" -eq 0 ]
    grep "## Section: TEST_SECTION" "$SCRIPT_CONFIG_FILE"
    grep "key=value" "$SCRIPT_CONFIG_FILE"
}

@test "add_to_config does not duplicate section" {
    init_config
    add_to_config "TEST_SECTION" "key=value"
    
    run add_to_config "TEST_SECTION" "new_key=new_value"
    [ "$status" -eq 0 ]
    
    # Count occurrences of section header
    local count=$(grep -c "## Section: TEST_SECTION" "$SCRIPT_CONFIG_FILE")
    [ "$count" -eq 1 ]
}

@test "backup_file creates a backup" {
    init_config
    local file_to_backup="$SCRIPT_CONFIG_FILE"
    
    run backup_file "$file_to_backup"
    [ "$status" -eq 0 ]
    
    count=$(ls "$SCRIPT_BACKUP_DIR" | wc -l)
    [ "$count" -ge 1 ]
}

@test "enable_omz_plugin patches .zshrc" {
    local zshrc="$HOME/.zshrc"
    echo "plugins=(git)" > "$zshrc"
    
    run enable_omz_plugin "docker"
    [ "$status" -eq 0 ]
    grep "plugins=(git docker)" "$zshrc"
}
