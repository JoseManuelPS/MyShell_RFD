
# Module: Eksctl

MODULES["Eksctl"]="configure_eksctl"

configure_eksctl() {
    if check_binary eksctl; then
        print_header "Eksctl Configuration"
        
        if prompt_yes_no "Enable eksctl autocompletion?" "y"; then
            local config_content="source <(eksctl completion zsh)"
            add_to_config "Eksctl" "$config_content"
            lecho "SUCCESS" "Eksctl autocompletion configured."
        else
            lecho "INFO" "Skipping Eksctl autocompletion."
        fi
    fi
}
