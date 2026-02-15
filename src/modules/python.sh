MODULES["Python"]="configure_python"

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
