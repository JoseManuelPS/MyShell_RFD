
# Module: Terraform & OpenTofu

MODULES["Terraform"]="configure_terraform"
MODULES["OpenTofu"]="configure_opentofu"

configure_terraform() {
    if check_binary terraform; then
        print_header "Terraform Configuration"
        
        if prompt_yes_no "Enable Terraform autocompletion and aliases?" "y"; then
            read -r -d '' config_content << EOM
autoload -U +X bashcompinit && bashcompinit
complete -o nospace -C /usr/local/bin/terraform terraform
alias t='terraform'
EOM
            add_to_config "Terraform" "$config_content"
            lecho "SUCCESS" "Terraform configured."
        else
            lecho "INFO" "Skipping Terraform configuration."
        fi
    fi
}

configure_opentofu() {
    if check_binary opentofu; then
        print_header "OpenTofu Configuration"
        
        if prompt_yes_no "Enable OpenTofu autocompletion and aliases?" "y"; then
             read -r -d '' config_content << EOM
complete -o nospace -C /usr/local/bin/opentofu opentofu
alias ot='opentofu'
EOM
            add_to_config "OpenTofu" "$config_content"
            lecho "SUCCESS" "OpenTofu configured."
        else
            lecho "INFO" "Skipping OpenTofu configuration."
        fi
    fi
}
