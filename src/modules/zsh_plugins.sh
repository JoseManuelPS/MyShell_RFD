
# Module: ZSH Check_DependenciesPlugins using Oh My Zsh custom folder

MODULES["ZSH_Plugins"]="configure_zsh_plugins"

configure_zsh_plugins() {
    local zsh_custom="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"
    
    print_header "ZSH Plugins"
    
    # ZSH Autosuggestions
    configure_plugin "zsh-autosuggestions" "https://github.com/zsh-users/zsh-autosuggestions" "zsh-autosuggestions"

    # ZSH Completions
    configure_plugin "zsh-completions" "https://github.com/zsh-users/zsh-completions" "zsh-completions"

    # ZSH Syntax Highlighting
    configure_plugin "zsh-syntax-highlighting" "https://github.com/zsh-users/zsh-syntax-highlighting.git" "zsh-syntax-highlighting"
}

configure_plugin() {
    local name="$1"
    local repo="$2"
    local dir_name="$3"
    local zsh_custom="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"
    local target_dir="$zsh_custom/plugins/$dir_name"

    if [[ ! -d "$target_dir" ]]; then
        if prompt_yes_no "Install $name?" "y"; then
            lecho "INFO" "Cloning $name..."
            git clone "$repo" "$target_dir"
            enable_omz_plugin "$dir_name"
            lecho "SUCCESS" "$name installed."
        fi
    fi
}
