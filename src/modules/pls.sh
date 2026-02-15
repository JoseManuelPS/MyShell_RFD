MODULES["PLS"]="configure_pls"

configure_pls() {
    if check_binary sudo; then
        print_header "PLS (sudo) Alias"
        if prompt_yes_no "Enable 'pls' alias (sudo last command)?" "y"; then
            add_to_config "PLS" "function pls() { sudo \$(fc -ln -1) }"
            lecho "SUCCESS" "Added 'pls' alias."
        fi
    fi
}
