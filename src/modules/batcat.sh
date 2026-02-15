MODULES["BatCat"]="configure_batcat"

configure_batcat() {
    if check_binary batcat || check_binary bat; then
        print_header "BatCat Configuration"
        
        # Determine actual binary name (bat vs batcat)
        local bat_cmd="bat"
        if check_binary batcat; then bat_cmd="batcat"; fi

        if prompt_yes_no "Alias 'bat' to '$bat_cmd'?" "y"; then
            add_to_config "BatCat" "alias bat='$bat_cmd'"
            lecho "SUCCESS" "Aliased bat to $bat_cmd."
        fi
    fi
}
