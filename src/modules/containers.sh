
# Module: Containers

MODULES["Docker"]="configure_docker"
MODULES["Podman"]="configure_podman"

configure_docker() {
    if check_binary docker; then
        print_header "Docker Configuration"
        
        if prompt_yes_no "Enable Docker plugin for ZSH?" "y"; then
            enable_omz_plugin "docker"
            lecho "SUCCESS" "Docker plugin enabled."
        fi
    fi
}

configure_podman() {
    if check_binary podman; then
        print_header "Podman Configuration"
        
        if prompt_yes_no "Enable Podman autocompletion and aliases?" "y"; then
            local config_content="source <(podman completion zsh); compdef _podman podman"
            add_to_config "Podman" "$config_content"
            
            if prompt_yes_no "Alias docker to podman?" "y"; then
                add_to_config "PodmanAlias" "alias docker=podman"
            fi
            
            lecho "SUCCESS" "Podman configured."
        else
            lecho "INFO" "Skipping Podman configuration."
        fi
    fi
}
