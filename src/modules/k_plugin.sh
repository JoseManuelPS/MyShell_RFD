
# Module: K (Z Plugin)

MODULES["K_Plugin"]="configure_k_plugin"

configure_k_plugin() {
    local zsh_custom="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"
    local k_plugin_dir="$zsh_custom/plugins/k"

    if [[ ! -d "$k_plugin_dir" ]]; then
        print_header "K (Z) Plugin"
        
        if prompt_yes_no "Install 'k' (z - jump around) plugin?" "y"; then
            lecho "INFO" "Cloning k plugin..."
            git clone https://github.com/supercrabtree/k "$k_plugin_dir"
            
            # Patch k to work as z
            sed -i 's/^k[[:space:]]/z /g' "$k_plugin_dir/k.sh"
            
            # We don't need to add it to 'plugins=' array here because we handle that in a separate ZSH config step usually,
            # but the original script added it to a local 'plugins' variable.
            # We will handle plugin activation centrally or here.
            
            add_to_config "K" "alias f='z -ha'"
            
            # Mark for activation
            # Ideally, we should have a function to enable OMZ plugins.
            enable_omz_plugin "k"
            
            lecho "SUCCESS" "K plugin installed."
        fi
    fi
}


