
# Module: K (Powerful LS, patched as 'z')
# Installs supercrabtree/k and patches it to respond to 'z' command.

MODULES["K_Plugin"]="configure_k_plugin"

configure_k_plugin() {
    local zsh_custom="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"
    local k_plugin_dir="$zsh_custom/plugins/k"

    if [[ ! -d "$k_plugin_dir" ]]; then
        print_header "K Plugin (Powerful LS as 'z')"
        
        if prompt_yes_no "Install 'k' plugin (accessible via 'z' command)?" "y"; then
            lecho "INFO" "Cloning k plugin..."
            git clone https://github.com/supercrabtree/k "$k_plugin_dir"
            
            # Professionally patch k to work as z
            lecho "INFO" "Patching k to respond to 'z' command..."
            # Using a more robust sed that handles potential spacing variations
            sed -i 's/^k\s*() {/z () {/g' "$k_plugin_dir/k.sh"
            
            # Add to our local config (self-contained)
            # This avoids touching the global .zshrc plugins list
            # We source the script directly and set the alias
            add_to_config "K" "[ -f \"$k_plugin_dir/k.sh\" ] && source \"$k_plugin_dir/k.sh\"
alias f='z -ha'"
            
            lecho "SUCCESS" "K Plugin installed successfully."
            lecho "INFO" "Commands: 'z' for powerful ls, 'f' for 'z -ha'"
        fi
    fi
}
