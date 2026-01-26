
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
            "$fzf_dir/install" --bin
            
            # Clean up default bash install if it happened
            rm -f "$HOME/.fzf.bash"
            
            # Move ZSH config if needed, or just source it
            # The original script moved .fzf.zsh to custom folder.
            if [[ -f "$HOME/.fzf.zsh" ]]; then
                 mv "$HOME/.fzf.zsh" "$fzf_dir/"
            fi
            
            add_to_config "FZF" "[ -f $fzf_dir/.fzf.zsh ] && source $fzf_dir/.fzf.zsh"
            
            # Remove system fzf from zshrc plugins if present to avoid conflicts
            # This is complex to do via sed reliably, simplified for now:
            # sed -i '/.*fzf.*/d' $HOME/.zshrc 
            
            lecho "SUCCESS" "FZF installed and configured."
        fi
    fi
}
