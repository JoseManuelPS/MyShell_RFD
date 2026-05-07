
# Module: Claude CLI

MODULES["Claude"]="configure_claude"

configure_claude() {
    if [[ -f "$HOME/.local/bin/claude" ]]; then
        print_header "Claude CLI Configuration"

        if prompt_yes_no "Add ~/.local/bin to PATH for Claude CLI?" "y"; then
            local config_content='export PATH="$HOME/.local/bin:$PATH"'
            add_to_config "Claude" "$config_content"
            lecho "SUCCESS" "Claude CLI PATH configured."
        else
            lecho "INFO" "Skipping Claude CLI configuration."
        fi
    fi
}
