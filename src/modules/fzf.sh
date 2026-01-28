
# Module: FZF

MODULES["FZF"]="configure_fzf"

configure_fzf() {
    local zsh_custom="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"
    local fzf_dir="$zsh_custom/fzf"

    if [[ ! -d "$fzf_dir" ]]; then
        print_header "FZF Configuration"
        
        if prompt_yes_no "Install FZF plugin?" "y"; then
            lecho "INFO" "Cloning FZF..."
            git clone --depth 1 https://github.com/junegunn/fzf.git "$fzf_dir"
            
            lecho "INFO" "Running FZF install script..."
            # Use --key-bindings --completion to generate .fzf.zsh
            # --no-update-rc prevents it from modifying .zshrc (we handle that)
            "$fzf_dir/install" --key-bindings --completion --no-update-rc
            
            # Clean up default bash install if it happened
            rm -f "$HOME/.fzf.bash"
            
            # Move .fzf.zsh from $HOME to fzf_dir for organization
            if [[ -f "$HOME/.fzf.zsh" ]]; then
                mv "$HOME/.fzf.zsh" "$fzf_dir/"
            fi
            
            # Add source line to myshell config
            add_to_config "FZF" "[ -f $fzf_dir/.fzf.zsh ] && source $fzf_dir/.fzf.zsh"
            
            lecho "SUCCESS" "FZF installed and configured."
        fi
    fi
}
