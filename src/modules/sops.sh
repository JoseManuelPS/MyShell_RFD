MODULES["SOPS"]="configure_sops"

configure_sops() {
    print_header "SOPS Configuration"
    if check_binary sops; then
        if prompt_yes_no "Enable SOPS autocompletion?" "y"; then
            add_to_config "SOPS" "source <(sops completion zsh)"
            lecho "SUCCESS" "SOPS autocompletion enabled."
        fi
    fi
}
