
# Test Helper

common_setup() {
    # Resolve the project root:
    # If this helper is included from tests/core/foo.bats, BATS_TEST_FILENAME is .../tests/core/foo.bats
    # dirname is .../tests/core
    # /.. is .../tests
    # /.. is .../ (Root)
    
    export PROJECT_ROOT="$( cd "$( dirname "$BATS_TEST_FILENAME" )/../.." >/dev/null 2>&1 && pwd )"
    export BATS_TEST_DIRNAME
    
    # Mocking setup
    export MOCK_BIN_DIR="$BATS_TMPDIR/mock_bin"
    mkdir -p "$MOCK_BIN_DIR"
    export PATH="$MOCK_BIN_DIR:$PROJECT_ROOT:$PATH"
}

fail() {
    echo "$@"
    return 1
}

common_teardown() {
    rm -rf "$MOCK_BIN_DIR"
}

# Helper to mock a command
# Usage: mock_command "command_name" "script_content"
mock_command() {
    local cmd="$1"
    local content="$2"
    local mock_path="$MOCK_BIN_DIR/$cmd"
    
    echo "#!/bin/bash" > "$mock_path"
    echo "echo \"\$@\" >> \"$MOCK_BIN_DIR/${cmd}.log\"" >> "$mock_path"
    echo "$content" >> "$mock_path"
    chmod +x "$mock_path"
}

# Helper to assert a command was called with specific args
# Assuming the mock writes to a log file
assert_command_called() {
    local cmd="$1"
    local log_file="$MOCK_BIN_DIR/${cmd}.log"
    if [ ! -f "$log_file" ]; then
        fail "Command '$cmd' was not called (log file missing)"
    fi
}
