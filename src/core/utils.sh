
# Core: Utils
# General utility functions.

SCRIPT_ROOT_DIR="$HOME/.myshell_rfd"
SCRIPT_CONFIG_FILE="$SCRIPT_ROOT_DIR/config"
SCRIPT_BACKUP_DIR="$SCRIPT_ROOT_DIR/backups"

# Check if a binary exists
check_binary() {
    command -v "$1" >/dev/null 2>&1
}

# Create config file if it doesn't exist
init_config() {
    if [[ ! -d "$SCRIPT_ROOT_DIR" ]]; then
        mkdir -p "$SCRIPT_ROOT_DIR"
    fi

    if [[ ! -d "$SCRIPT_BACKUP_DIR" ]]; then
        mkdir -p "$SCRIPT_BACKUP_DIR"
    fi
    
    if [[ ! -f "$SCRIPT_CONFIG_FILE" ]]; then
        lecho "INFO" "Creating configuration file at $SCRIPT_CONFIG_FILE"
        echo "# MyShell_RFD Configuration" > "$SCRIPT_CONFIG_FILE"
        echo "# Generated on $(date)" >> "$SCRIPT_CONFIG_FILE"
        echo "" >> "$SCRIPT_CONFIG_FILE"
    fi
}

# Clean/Reset configuration
clean_config() {
    print_header "Clean Configuration"
    if [[ -f "$SCRIPT_CONFIG_FILE" ]]; then
        if prompt_yes_no "Are you sure you want to delete the current configuration ($SCRIPT_CONFIG_FILE)?" "n"; then
            backup_file "$SCRIPT_CONFIG_FILE"
            rm "$SCRIPT_CONFIG_FILE"
            lecho "SUCCESS" "Configuration removed (backup created)."
        else
            lecho "INFO" "Clean cancelled."
        fi
    else
        lecho "WARN" "No configuration file found to clean."
    fi
}

# Append to config file exclusively (idempotent-ish)
# Usage: add_to_config "SECTION_NAME" "content"
add_to_config() {
    local section="$1"
    local content="$2"

    if grep -q "## Section: $section" "$SCRIPT_CONFIG_FILE"; then
        lecho "DEBUG" "Section $section already exists in config."
        return
    fi

    echo "## Section: $section" >> "$SCRIPT_CONFIG_FILE"
    echo "$content" >> "$SCRIPT_CONFIG_FILE"
    echo "" >> "$SCRIPT_CONFIG_FILE"
}

# Safely back up a file before modifying
backup_file() {
    local file="$1"
    if [[ -f "$file" ]]; then
        cp "$file" "$SCRIPT_BACKUP_DIR/$(basename "$file").$(date +%s).bak"
    fi
}

# Source the config in .zshrc if not present
ensure_zshrc_source() {
    local zshrc="$HOME/.zshrc"
    local source_line="[ -f \"$SCRIPT_CONFIG_FILE\" ] && source \"$SCRIPT_CONFIG_FILE\""
    
    if [[ -f "$zshrc" ]]; then
        if ! grep -qF "$SCRIPT_CONFIG_FILE" "$zshrc"; then
            lecho "INFO" "Adding source line to .zshrc"
            backup_file "$zshrc"
            echo "" >> "$zshrc"
            echo "# MyShell_RFD Source" >> "$zshrc"
            echo "$source_line" >> "$zshrc"
        fi
    fi
}

# Helper to enable OMZ plugin if not already enabled
enable_omz_plugin() {
    local plugin="$1"
    local zshrc="$HOME/.zshrc"
    
    if [[ ! -f "$zshrc" ]]; then
        return
    fi

    if grep -q "plugins=(" "$zshrc"; then
         if ! grep -q "$plugin" "$zshrc"; then
             lecho "INFO" "Enabling plugin '$plugin' in .zshrc..."
             local current_plugins=$(grep '^plugins=(' "$zshrc" | sed 's/plugins=(//g' | sed 's/)//g')
             sed -i "/^plugins=/c plugins=($current_plugins $plugin)" "$zshrc"
         fi
    fi
}
