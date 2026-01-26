
# Module: Rosa

MODULES["Rosa"]="configure_rosa"

configure_rosa() {
    if check_binary rosa; then
        print_header "Rosa Configuration"
        
        if prompt_yes_no "Enable Rosa autocompletion?" "y"; then
            local config_content="source <(rosa completion zsh)"
            add_to_config "Rosa" "$config_content"
            lecho "SUCCESS" "Rosa autocompletion configured."
        else
            lecho "INFO" "Skipping Rosa autocompletion."
        fi
    fi
}
