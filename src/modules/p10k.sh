
# Module: PowerLevel10K

MODULES["PowerLevel10K"]="configure_p10k"

configure_p10k() {
    local zsh_custom="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"
    
    if [[ ! -d "$zsh_custom/themes/powerlevel10k" ]]; then
        print_header "PowerLevel10K Theme"
        
        if prompt_yes_no "Install PowerLevel10K theme?" "y"; then
             lecho "INFO" "Cloning PowerLevel10K..."
             git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$zsh_custom/themes/powerlevel10k"
             
             if prompt_yes_no "Configure P10K as default theme?" "y"; then
                 # Update ZSH_THEME in .zshrc
                 local zshrc="$HOME/.zshrc"
                 if grep -q "ZSH_THEME=" "$zshrc"; then
                     sed -i '/^ZSH_THEME=/s/^/# /' "$zshrc"
                     sed -i '/^# ZSH_THEME=/a ZSH_THEME="powerlevel10k/powerlevel10k"' "$zshrc"
                     lecho "SUCCESS" "Updated .zshrc theme to PowerLevel10K."
                 fi
                 
                 # Deploy P10K config from asset
                 if [[ -n "$P10K_ZSH_CONTENT_BASE64" ]]; then
                     echo "$P10K_ZSH_CONTENT_BASE64" | base64 -d > "$HOME/.p10k.zsh"
                     lecho "SUCCESS" "Deployed default .p10k.zsh configuration."
                 else
                     lecho "WARN" "P10K default config asset missing."
                 fi
                 
                 add_to_config "PowerLevel10K" "[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh"
             fi
        fi
    fi
}
