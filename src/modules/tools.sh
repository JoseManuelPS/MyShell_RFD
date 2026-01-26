
# Module: Tools (BatCat, PLS, Python)

MODULES["BatCat"]="configure_batcat"
MODULES["PLS"]="configure_pls"
MODULES["Python"]="configure_python"

configure_batcat() {
    if check_binary batcat || check_binary bat; then
        print_header "BatCat Configuration"
        
        # Determine actual binary name (bat vs batcat)
        local bat_cmd="bat"
        if check_binary batcat; then bat_cmd="batcat"; fi

        if prompt_yes_no "Alias 'cat' to '$bat_cmd'?" "y"; then
            add_to_config "BatCat" "alias cat='$bat_cmd'"
            lecho "SUCCESS" "Aliased cat to $bat_cmd."
        fi
    fi
}

configure_pls() {
    if check_binary sudo; then
        print_header "PLS (sudo) Alias"
        if prompt_yes_no "Enable 'pls' alias (sudo last command)?" "y"; then
            add_to_config "PLS" "function pls() { sudo \$(fc -ln -1) }"
            lecho "SUCCESS" "Added 'pls' alias."
        fi
    fi
}

configure_python() {
    if check_binary python3; then
        print_header "Python3 Configuration"
        
        # Check for default venv
        if prompt_yes_no "Activate default Python virtual environment?" "y"; then
             local venv_path="$HOME/.py-venv-default"
             local config_content="source $venv_path/bin/activate"
             
             if [[ ! -d "$venv_path" ]]; then
                 if prompt_yes_no "Virtual environment not found at $venv_path. Create it?" "y"; then
                     python3 -m venv "$venv_path"
                     add_to_config "Python3" "$config_content"
                     lecho "SUCCESS" "Created and configured default Python venv."
                 fi
             else
                 add_to_config "Python3" "$config_content"
                 lecho "SUCCESS" "Configured default Python venv."
             fi
        fi
    fi
}
