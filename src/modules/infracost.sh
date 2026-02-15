MODULES["Infracost"]="configure_infracost"

configure_infracost() {
    print_header "Infracost Configuration"
    if check_binary infracost; then
        if prompt_yes_no "Enable Infracost autocompletion?" "y"; then
            add_to_config "Infracost" "source <(infracost completion --shell zsh); compdef _infracost infracost"
            lecho "SUCCESS" "Infracost autocompletion enabled."
        fi
    fi
}
