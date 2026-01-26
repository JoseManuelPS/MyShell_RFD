
# Module: NVM

MODULES["NVM"]="configure_nvm"

configure_nvm() {
    if [[ -d "$HOME/.nvm" ]]; then
        print_header "NVM Configuration"
        
        if prompt_yes_no "Configure NVM loading?" "y"; then
            read -r -d '' config_content << EOM
export NVM_DIR="\$HOME/.nvm"
[ -s "\$NVM_DIR/nvm.sh" ] && . "\$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "\$NVM_DIR/bash_completion" ] && . "\$NVM_DIR/bash_completion"  # This loads nvm bash_completion
if [ -d "\$HOME/.local/bin" ]; then
  . "\$HOME/.local/bin/env"
fi
EOM
            add_to_config "NVM" "$config_content"
            lecho "SUCCESS" "NVM configured."
        else
            lecho "INFO" "Skipping NVM configuration."
        fi
    fi
}
