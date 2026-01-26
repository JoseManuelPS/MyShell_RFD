
# Module: Tridentctl

MODULES["Tridentctl"]="configure_tridentctl"

configure_tridentctl() {
    if check_binary tridentctl; then
        print_header "Tridentctl Configuration"
        
        if prompt_yes_no "Enable Tridentctl autocompletion?" "y"; then
            read -r -d '' config_content << EOM
source <(tridentctl completion zsh); compdef _tridentctl tridentctl
compdef __start_tridentctl astra
alias astra='tridentctl -n trident'
EOM
            add_to_config "Tridentctl" "$config_content"
            lecho "SUCCESS" "Tridentctl autocompletion configured."
        else
            lecho "INFO" "Skipping Tridentctl autocompletion."
        fi
    fi
}
