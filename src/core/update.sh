
# Core: Update Logic
# Self-update mechanism

self_update() {
    print_header "Self Update"
    
    local repo="josemanuelps/myshell_rfd"
    local local_bin="/usr/local/bin/myshell_rfd"
    
    lecho "INFO" "Checking for updates..."
    
    # Simple strategy: Download 'latest' release artifact
    # Note: This assumes standard GitHub Releases structure. 
    # Since the user repo might differ, we verify with what we implemented in Ansible:
    # https://github.com/josemanuelps/myshell_rfd/releases/download/<version>/myshell_rfd
    
    # We will try to fetch the latest tag name first
    local latest_tag_url="https://api.github.com/repos/$repo/releases/latest"
    if ! check_binary curl || ! check_binary jq; then
         lecho "ERROR" "curl and jq are required for update."
         return 1
    fi
    
    local latest_version=$(curl -s "$latest_tag_url" | jq -r .tag_name)
    
    if [[ "$latest_version" == "null" || -z "$latest_version" ]]; then
        lecho "ERROR" "Failed to check for updates (API limit or network error)."
        return 1
    fi
    
    lecho "INFO" "Latest version: $latest_version"
    # We should compare version here, but for now we force update if requested or ask user
    
    if prompt_yes_no "Download and install version $latest_version?" "y"; then
        local download_url="https://github.com/$repo/releases/download/$latest_version/myshell_rfd-$latest_version"
        local temp_file="/tmp/myshell_rfd_update"
        
        lecho "INFO" "Downloading from $download_url..."
        if curl -L -o "$temp_file" "$download_url"; then
            lecho "INFO" "Installing (requires sudo)..."
            # We install it with the name 'myshell_rfd' for ease of use, even if the source has .sh
            if sudo cp "$temp_file" "$local_bin" && sudo chmod +x "$local_bin"; then
                lecho "SUCCESS" "Updated successfully to $latest_version."
            else
                lecho "ERROR" "Failed to copy bin to $local_bin."
            fi
            rm -f "$temp_file"
        else
             lecho "ERROR" "Download failed."
        fi
    fi
}
