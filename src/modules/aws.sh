
# Module: AWS

MODULES["AWS"]="configure_aws"

configure_aws() {
    if check_binary aws; then
        print_header "AWS Configuration"
        
        if prompt_yes_no "Enable AWS CLI autocompletion?" "y"; then
            local config_content="complete -C '/usr/local/bin/aws_completer' aws"
            add_to_config "AWS" "$config_content"
            lecho "SUCCESS" "AWS autocompletion configured."
        else
            lecho "INFO" "Skipping AWS autocompletion."
        fi
    fi
}
