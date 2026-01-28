
#!./tests/libs/bats/bin/bats

load '../test_helper'

setup() {
    common_setup
}

@test "Build artifact exists" {
  run ls $PROJECT_ROOT/dist/myshell_rfd-v1.0.1
  [ "$status" -eq 0 ]
}

@test "Script runs and shows version" {
    run bash $PROJECT_ROOT/dist/myshell_rfd-v1.0.1 --version
    # Check if the output contains the version string
    [[ "$output" == *"MyShell_RFD v1.0.1"* ]]
    
    # Check if it's executable
    [ -x "$PROJECT_ROOT/dist/myshell_rfd-v1.0.1" ]
}

@test "Colors module defines variables" {
    # Source colors and check
    run bash -c "source $PROJECT_ROOT/src/core/colors.sh && echo \$RED"
    [ "$status" -eq 0 ]
    [ -n "$output" ]
}

@test "lecho prints message with type" {
    source "$PROJECT_ROOT/src/core/lecho.sh"
    run lecho "INFO" "Test message"
    [ "$status" -eq 0 ]
    [[ "$output" == *"[INFO]"* ]]
    [[ "$output" == *"Test message"* ]]
}
