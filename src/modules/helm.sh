
# Module: Helm

MODULES["Helm"]="configure_helm"

configure_helm() {
    if check_binary helm; then
        print_header "Helm Configuration"
        
        if prompt_yes_no "Enable Helm autocompletion?" "y"; then
            local config_content="source <(helm completion zsh); compdef _helm helm"
            add_to_config "Helm" "$config_content"
            lecho "SUCCESS" "Helm autocompletion configured."
        else
            lecho "INFO" "Skipping Helm autocompletion."
        fi
    fi
}
