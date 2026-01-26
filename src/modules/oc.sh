
# Module: OC

MODULES["OC"]="configure_oc"

configure_oc() {
    if check_binary oc; then
        print_header "OC (OpenShift) Configuration"
        
        if prompt_yes_no "Enable OC autocompletion?" "y"; then
            local config_content="source <(oc completion zsh); compdef _oc oc"
            add_to_config "OC" "$config_content"
            lecho "SUCCESS" "OC autocompletion configured."
        else
            lecho "INFO" "Skipping OC autocompletion."
        fi
    fi
}
