
# Module: Terragrunt

MODULES["Terragrunt"]="configure_terragrunt"

configure_terragrunt() {
    if check_binary terragrunt; then
        print_header "Terragrunt Configuration"
        
        if prompt_yes_no "Enable Terragrunt autocompletion?" "y"; then
            local config_content="autoload -U +X bashcompinit && bashcompinit\ncomplete -o nospace -C /usr/local/bin/terragrunt terragrunt"
            add_to_config "Terragrunt" "$config_content"
            lecho "SUCCESS" "Terragrunt autocompletion configured."
        else
            lecho "INFO" "Skipping Terragrunt autocompletion."
        fi
    fi
}
