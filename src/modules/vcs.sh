
# Module: VCS

MODULES["GitHub"]="configure_github"
MODULES["GitLab"]="configure_gitlab"

configure_github() {
    if check_binary gh; then
        print_header "GitHub CLI Configuration"
        
        if prompt_yes_no "Enable GitHub CLI autocompletion?" "y"; then
            local config_content='source <(gh completion -s zsh); compdef _gh gh'
            add_to_config "GitHub" "$config_content"
            lecho "SUCCESS" "GitHub CLI autocompletion configured."
        else
             lecho "INFO" "Skipping GitHub CLI autocompletion."
        fi
    fi
}

configure_gitlab() {
    if check_binary glab; then
        print_header "GitLab CLI Configuration"
        
        if prompt_yes_no "Enable GitLab CLI autocompletion?" "y"; then
            local config_content='source <(glab completion -s zsh); compdef _glab glab'
            add_to_config "GitLab" "$config_content"
            lecho "SUCCESS" "GitLab CLI autocompletion configured."
        else
             lecho "INFO" "Skipping GitLab CLI autocompletion."
        fi
    fi
}
