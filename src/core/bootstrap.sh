
# Core: Bootstrap
# Checks and installs essential dependencies (curl, git, zsh).

check_and_install_essentials() {
    print_header "System Bootstrap"
    
    local missing_deps=0
    
    # Detect Pkg Manager
    local pkg_cmd=""
    if check_binary apk; then
        pkg_cmd="sudo apk add"
    elif check_binary apt; then
        pkg_cmd="sudo apt install -y"
    elif check_binary dnf; then
        pkg_cmd="sudo dnf install -y"
    else
        lecho "WARN" "Could not detect package manager (apt/dnf/apk). Automatic installation disabled."
    fi

    # Check curl
    if ! check_binary curl; then
        lecho "WARN" "curl not found."
        if [[ -n "$pkg_cmd" ]] && prompt_yes_no "Install curl?" "y"; then
            $pkg_cmd curl
        else
            missing_deps=1
        fi
    else
        lecho "SUCCESS" "curl detected."
    fi

    # Check git
    if ! check_binary git; then
        lecho "WARN" "git not found."
        if [[ -n "$pkg_cmd" ]] && prompt_yes_no "Install git?" "y"; then
            $pkg_cmd git
        else
            missing_deps=1
        fi
    else
        lecho "SUCCESS" "git detected."
    fi

    # Check zsh
    if ! check_binary zsh; then
        lecho "WARN" "zsh not found."
        if [[ -n "$pkg_cmd" ]] && prompt_yes_no "Install zsh?" "y"; then
            $pkg_cmd zsh
            if check_binary zsh; then
                # Skip chsh in non-interactive mode because it usually requires a password/interaction
                if [[ "$AUTO_YES" == "true" ]]; then
                    lecho "WARN" "Skipping 'chsh' in non-interactive mode."
                elif prompt_yes_no "Make zsh default shell?" "y"; then
                    chsh -s "$(which zsh)"
                fi
            fi
        else
            missing_deps=1
        fi
    else
        lecho "SUCCESS" "zsh detected."
    fi

    # Check Oh My Zsh
    if [[ ! -d "$HOME/.oh-my-zsh" ]]; then
        lecho "WARN" "Oh My Zsh not found."
        if prompt_yes_no "Install Oh My Zsh?" "y"; then
            lecho "INFO" "Installing Oh My Zsh..."
            sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
        fi
    else
        lecho "SUCCESS" "Oh My Zsh detected."
    fi

    if [[ "$missing_deps" -eq 1 ]]; then
        lecho "ERROR" "Some essential dependencies are missing. Script may malfunction."
        if ! prompt_yes_no "Continue anyway?" "n"; then
            exit 1
        fi
    fi
}
