
# Module: Kubectl

MODULES["Kubectl"]="configure_kubectl"

configure_kubectl() {
    if check_binary kubectl; then
        print_header "Kubectl Configuration"
        
        if prompt_yes_no "Enable Kubectl autocompletion and aliases?" "y"; then
            read -r -d '' config_content << EOM
source <(kubectl completion zsh); compdef _kubectl kubectl
compdef __start_kubectl k
alias k=kubectl
compdef __start_kubectl ka
alias ka='kubectl apply -f'
compdef __start_kubectl kc
alias kc='kubectl create'
compdef __start_kubectl kd
alias kd='kubectl describe'
compdef __start_kubectl kdc
alias kdc='kubectl config delete-context'
compdef __start_kubectl ke
alias ke='kubectl exec -ti'
compdef __start_kubectl kg
alias kg='kubectl get'
compdef __start_kubectl kgj
alias kgj='kubectl get -o json'
compdef __start_kubectl kgy
alias kgy='kubectl get -o yaml'
compdef __start_kubectl kl
alias kl='kubectl logs'
compdef __start_kubectl kn
alias kn='kubectl config set-context --current --namespace'
compdef __start_kubectl ku
alias ku='kubectl config use-context'
EOM
            add_to_config "Kubectl" "$config_content"
            lecho "SUCCESS" "Kubectl configured."
            
            # Krew Installation
            if prompt_yes_no "Install Krew (plugin manager)?" "n"; then
                 install_krew
            fi
        else
            lecho "INFO" "Skipping Kubectl configuration."
        fi
    fi
}

install_krew() {
    lecho "INFO" "Installing Krew..."
    local temp_dir="$(mktemp -d)"
    pushd "$temp_dir" > /dev/null
    
    local os="$(uname | tr '[:upper:]' '[:lower:]')"
    local arch="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/\(arm\)\(64\)\?.*/\1\2/' -e 's/aarch64$/arm64/')"
    local krew="krew-${os}_${arch}"

    if curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${krew}.tar.gz"; then
        tar zxvf "${krew}.tar.gz"
        ./"${krew}" install krew
        
        local krew_path='export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"'
        add_to_config "Krew" "$krew_path"
        
        export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"
        lecho "SUCCESS" "Krew installed."
        
        # Install default plugins

        lecho "INFO" "Installing specific krew plugins..."
        for plugin in ai ns keda; do
            if prompt_yes_no "Install krew plugin '$plugin'?" "y"; then
                kubectl krew install "$plugin" || lecho "WARN" "Failed to install $plugin."
            fi
        done
    else
        lecho "ERROR" "Failed to download Krew."
    fi
    
    popd > /dev/null
    rm -rf "$temp_dir"
}
