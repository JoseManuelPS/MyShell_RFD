
# Core: UI
# User Interface helpers.

# Prints a section header
print_header() {
    local title="$1"
    echo -e "\n${BOLD}${BLUE}###############################################################################${RESET}"
    echo -e "${BOLD}${BLUE}# ${CYAN}${title}${RESET}"
    echo -e "${BOLD}${BLUE}###############################################################################${RESET}\n"
}

# Prompt user for yes/no input
# Usage: prompt_yes_no "Question?" default_value(y/n)
# Returns 0 for yes, 1 for no
prompt_yes_no() {
    local question="$1"
    local default="${2:-n}"
    local prompt_text=""

    if [[ "$default" == "y" ]]; then
        prompt_text="[Y/n]"
    else
        prompt_text="[y/N]"
    fi

    echo -ne "${BOLD}${question} ${prompt_text}: ${RESET}"
    read -r response

    # If empty, use default
    if [[ -z "$response" ]]; then
        response="$default"
    fi

    # Check response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

# Catch interrupt signal
trap_cleanup() {
    echo -e "\n${RED}Execution interrupted by user.${RESET}"
    exit 130
}

trap trap_cleanup SIGINT
