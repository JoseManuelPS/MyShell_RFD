
# Main Execution

main() {
    clear
    
    # Parse CLI Arguments
    local command="$1"
    local arg="$2"

    case "$command" in
        c|clean)
            init_config
            clean_config
            exit 0
            ;;
        u|update)
            # Need to source dependencies first just in case
            # In compiled script, function is available.
            self_update
            exit 0
            ;;
        i|install)
            init_config
            # Bootstrap checks
            check_and_install_essentials
            
            if [[ -n "$arg" ]]; then
                run_single_module "$arg"
            else
                run_install_selector
            fi
            exit 0
            ;;
        v|version|--version|-v)
            echo "MyShell_RFD ${SCRIPT_VERSION:-unknown}"
            exit 0
            ;;
        h|help|--help|-h)
            show_help
            exit 0
            ;;
        "")
            # Default behavior (Interactive all)
            ;;
        *)
            lecho "ERROR" "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac

    # -- Default Interactive Flow --
    print_header "MyShell_RFD"
    lecho "INFO" "Starting interactive configuration..."

    init_config
    check_and_install_essentials
    ensure_zshrc_source

    run_all_modules
    
    print_footer
}

show_help() {
    echo "Usage: myshell_rfd [command] [args]"
    echo ""
    echo "Commands:"
    echo "  (no args)       Run interactive configuration for all modules."
    echo "  i, install      Select modules to install interactively."
    echo "  i, install <m>  Install a specific module (e.g., 'AWS', 'Kubectl')."
    echo "  c, clean        Remove existing configuration file."
    echo "  u, update       Update myshell_rfd to the latest version."
    echo "  v, version      Show script version."
    echo "  h, help         Show this help message."
}

run_single_module() {
    local target="$1"
    local found=0
    
    # Case insensitive search keys
    for mod_name in "${!MODULES[@]}"; do
        if [[ "${mod_name,,}" == "${target,,}" ]]; then
            local mod_func="${MODULES[$mod_name]}"
            lecho "INFO" "Running module: $mod_name"
            $mod_func
            found=1
            break
        fi
    done
    
    if [[ $found -eq 0 ]]; then
        lecho "ERROR" "Module '$target' not found."
        echo "Available modules: ${!MODULES[@]}"
        exit 1
    fi
}

run_install_selector() {
    print_header "Module Selector"
    lecho "INFO" "Select a module to install:"
    
    local sorted_modules=($(printf "%s\n" "${!MODULES[@]}" | sort))
    
    # Use select for menu
    PS3="Enter module number (or q to quit): "
    select mod in "${sorted_modules[@]}"; do
        if [[ -n "$mod" ]]; then
            local mod_func="${MODULES[$mod]}"
            lecho "INFO" "Running module: $mod"
            $mod_func
            break
        elif [[ "$REPLY" == "q" ]]; then
            break
        else
            echo "Invalid selection."
        fi
    done
}

run_all_modules() {
    local sorted_modules=($(printf "%s\n" "${!MODULES[@]}" | sort))
    
    if [[ ${#sorted_modules[@]} -eq 0 ]]; then
        lecho "WARN" "No modules loaded."
    else
        lecho "INFO" "Loading ${#sorted_modules[@]} modules..."
    fi

    for mod_name in "${sorted_modules[@]}"; do
        local mod_func="${MODULES[$mod_name]}"
        if declare -F "$mod_func" > /dev/null; then
            $mod_func
        else
            lecho "ERROR" "Module '$mod_name' link error."
        fi
    done
}

print_footer() {
    print_header "Execution Complete"
    lecho "SUCCESS" "MyShell_RFD has finished."
    lecho "INFO" "Please restart your shell or run 'source ~/.zshrc' to apply changes."
}

# Run Main
main "$@"
