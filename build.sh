#!/bin/bash
set -e

VERSION=$1
SRC_DIR="src"
BUILD_DIR="dist"
OUTPUT_FILE="$BUILD_DIR/myshell_rfd-$VERSION"

# Header
cat <<EOF > "$OUTPUT_FILE"
#!/bin/bash
###############################################################################
##        Name: MyShell_RFD                                                   #
## Description: Professional Configuration & Tooling for ZSH/Bash             #
##     Version: $VERSION                                                      #
##----------------------------------------------------------------------------#
##      Editor: José Manuel Plana Santos                                      #
##     Contact: dev.josemanuelps@gmail.com                                    #
###############################################################################

# Auto-generated build. Do not edit directly.
SCRIPT_VERSION="$VERSION"

EOF

# Embed Assets
echo "## Assets" >> "$OUTPUT_FILE"
if [ -f "$SRC_DIR/assets/p10k.zsh" ]; then
    echo "P10K_ZSH_CONTENT_BASE64=\"$(base64 "$SRC_DIR/assets/p10k.zsh" | tr -d '\n')\"" >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# Core Utilities
for file in "$SRC_DIR/core"/*.sh; do
    if [ -f "$file" ]; then
        echo "## Loading Core: $(basename "$file")" >> "$OUTPUT_FILE"
        cat "$file" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
done

# Modules
echo "## Loading Modules" >> "$OUTPUT_FILE"
echo "declare -A MODULES" >> "$OUTPUT_FILE" # Registry for modules
echo "" >> "$OUTPUT_FILE"

for file in "$SRC_DIR/modules"/*.sh; do
    if [ -f "$file" ]; then
        echo "### Module: $(basename "$file")" >> "$OUTPUT_FILE"
        cat "$file" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
done

# Main Entry Point
if [ -f "$SRC_DIR/main.sh" ]; then
    echo "## Loading Main" >> "$OUTPUT_FILE"
    cat "$SRC_DIR/main.sh" >> "$OUTPUT_FILE"
else
    echo "Error: Main entry point not found!"
    exit 1
fi

chmod +x "$OUTPUT_FILE"
echo "Build complete: $OUTPUT_FILE"
