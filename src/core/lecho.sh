
# Core: Logger (lecho)
# Standardized logging function.

lecho() {
    local type="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case "$type" in
        "INFO")
            echo -e "${BLUE}[INFO]${RESET} ${message}"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[OK]${RESET}   ${message}"
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${RESET} ${message}"
            ;;
        "ERROR")
            echo -e "${RED}[ERR]${RESET}  ${message}" >&2
            ;;
        "DEBUG")
            if [[ "$DEBUG_MODE" == "true" ]]; then
                echo -e "${MAGENTA}[DEBUG]${RESET} ${message}"
            fi
            ;;
        *)
            echo -e "${message}"
            ;;
    esac
}
