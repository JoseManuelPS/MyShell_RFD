
# Module: Minikube

MODULES["Minikube"]="configure_minikube"

configure_minikube() {
    if check_binary minikube; then
        print_header "Minikube Configuration"
        
        if prompt_yes_no "Enable Minikube autocompletion?" "y"; then
            local config_content="source <(minikube completion zsh)"
            add_to_config "Minikube" "$config_content"
            lecho "SUCCESS" "Minikube autocompletion configured."
        else
            lecho "INFO" "Skipping Minikube autocompletion."
        fi
    fi
}
