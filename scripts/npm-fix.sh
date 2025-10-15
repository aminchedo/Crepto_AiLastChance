#!/bin/bash
# NPM Troubleshooting Script for Git Bash/WSL
# This script helps diagnose and fix common npm installation issues

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Default values
DRY_RUN=false
FORCE=false
CLEAN_ONLY=false
REINSTALL_ONLY=false
CHECK_ONLY=false
STRATEGY="standard"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --clean-only)
            CLEAN_ONLY=true
            shift
            ;;
        --reinstall-only)
            REINSTALL_ONLY=true
            shift
            ;;
        --check-only)
            CHECK_ONLY=true
            shift
            ;;
        --strategy)
            STRATEGY="$2"
            shift 2
            ;;
        -h|--help)
            echo "NPM Troubleshooting Script for Git Bash/WSL"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run          Show what would be done without making changes"
            echo "  --force            Use force flag during npm install"
            echo "  --clean-only       Only clean node_modules and cache, don't reinstall"
            echo "  --reinstall-only   Skip cleaning, just reinstall dependencies"
            echo "  --check-only       Only check system requirements and current state"
            echo "  --strategy STRAT   Use specific install strategy (standard|force|legacy|force-legacy|ci)"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                           # Standard clean and reinstall"
            echo "  $0 --dry-run                 # See what would be done"
            echo "  $0 --strategy force-legacy   # Use force and legacy peer deps"
            echo "  $0 --clean-only              # Only clean, don't reinstall"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Output functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

print_header() {
    echo -e "${MAGENTA}$1${NC}"
    echo -e "${MAGENTA}$(printf '=%.0s' {1..${#1}})${NC}"
}

# Check if running in WSL or Git Bash
detect_environment() {
    if [[ -f /proc/version ]] && grep -q Microsoft /proc/version; then
        echo "WSL"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "Git Bash"
    else
        echo "Linux/Unix"
    fi
}

# Kill any Node.js processes that might be locking files
stop_node_processes() {
    print_info "Checking for running Node.js processes..."
    
    local node_pids=$(pgrep -f node 2>/dev/null || true)
    if [[ -n "$node_pids" ]]; then
        local count=$(echo "$node_pids" | wc -l)
        print_warning "Found $count Node.js process(es) running"
        
        if [[ "$DRY_RUN" == "true" ]]; then
            print_info "Would stop Node.js processes (dry run)"
        else
            echo "$node_pids" | xargs kill -9 2>/dev/null || true
            print_success "Stopped Node.js processes"
        fi
    else
        print_success "No Node.js processes found"
    fi
}

# Check for file locks (simplified for Unix-like systems)
check_file_locks() {
    print_info "Checking for file locks in node_modules..."
    
    if [[ -d "node_modules" ]]; then
        # Try to access some common problematic directories
        local problematic_dirs=("node_modules/.cache" "node_modules/.bin" "node_modules/esbuild" "node_modules/msw")
        
        for dir in "${problematic_dirs[@]}"; do
            if [[ -d "$dir" ]]; then
                if [[ "$DRY_RUN" == "true" ]]; then
                    print_info "Would check $dir for locks (dry run)"
                else
                    if ! ls "$dir" >/dev/null 2>&1; then
                        print_warning "Potential file lock in $dir"
                    fi
                fi
            fi
        done
    fi
    
    print_success "File lock check completed"
}

# Clean npm cache
clear_npm_cache() {
    print_info "Clearing npm cache..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "Would clear npm cache (dry run)"
        return
    fi
    
    if npm cache clean --force 2>/dev/null; then
        print_success "NPM cache cleared"
    else
        print_error "Failed to clear npm cache"
    fi
}

# Remove node_modules and package-lock.json
remove_node_modules() {
    print_info "Removing node_modules and package-lock.json..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "Would remove node_modules and package-lock.json (dry run)"
        return
    fi
    
    # Remove node_modules
    if [[ -d "node_modules" ]]; then
        rm -rf node_modules
        print_success "Removed node_modules directory"
    fi
    
    # Remove package-lock.json
    if [[ -f "package-lock.json" ]]; then
        rm -f package-lock.json
        print_success "Removed package-lock.json"
    fi
    
    # Remove .npm directory if it exists
    if [[ -d ".npm" ]]; then
        rm -rf .npm
        print_success "Removed .npm directory"
    fi
}

# Install dependencies with different strategies
install_dependencies() {
    local strategy="$1"
    print_info "Installing dependencies with strategy: $strategy"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "Would install dependencies with strategy: $strategy (dry run)"
        return 0
    fi
    
    case "$strategy" in
        "standard")
            npm install
            ;;
        "force")
            npm install --force
            ;;
        "legacy")
            npm install --legacy-peer-deps
            ;;
        "force-legacy")
            npm install --force --legacy-peer-deps
            ;;
        "ci")
            npm ci
            ;;
        *)
            npm install
            ;;
    esac
    
    if [[ $? -eq 0 ]]; then
        print_success "Dependencies installed successfully"
        return 0
    else
        print_error "Failed to install dependencies"
        return 1
    fi
}

# Verify installation
test_installation() {
    print_info "Verifying installation..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "Would verify installation (dry run)"
        return 0
    fi
    
    # Check for missing dependencies
    local missing_deps=$(npm ls --depth=0 2>&1 | grep "UNMET DEPENDENCY" || true)
    if [[ -n "$missing_deps" ]]; then
        print_warning "Found missing dependencies:"
        echo "$missing_deps" | while read -r line; do
            print_warning "  $line"
        done
        return 1
    fi
    
    # Check for extraneous packages
    local extraneous=$(npm ls --depth=0 2>&1 | grep "extraneous" || true)
    if [[ -n "$extraneous" ]]; then
        print_warning "Found extraneous packages:"
        echo "$extraneous" | while read -r line; do
            print_warning "  $line"
        done
    fi
    
    print_success "Installation verification completed"
    return 0
}

# Check system requirements
test_system_requirements() {
    print_info "Checking system requirements..."
    
    # Check Node.js version
    if command -v node >/dev/null 2>&1; then
        local node_version=$(node --version)
        print_success "Node.js version: $node_version"
        
        # Extract version number for comparison
        local version_num=$(echo "$node_version" | sed 's/v//' | cut -d. -f1)
        if [[ "$version_num" -lt 18 ]]; then
            print_warning "Node.js version $node_version is older than recommended (18.0.0+)"
        fi
    else
        print_error "Node.js not found or not working"
        return 1
    fi
    
    # Check npm version
    if command -v npm >/dev/null 2>&1; then
        local npm_version=$(npm --version)
        print_success "NPM version: $npm_version"
    else
        print_error "NPM not found or not working"
        return 1
    fi
    
    # Check available disk space
    local available_space=$(df -h . | awk 'NR==2 {print $4}')
    print_info "Available disk space: $available_space"
    
    return 0
}

# Main execution
main() {
    print_header "NPM Troubleshooting Script for Git Bash/WSL"
    
    local env=$(detect_environment)
    print_info "Detected environment: $env"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_warning "DRY RUN MODE - No changes will be made"
    fi
    
    # System requirements check
    if ! test_system_requirements; then
        print_error "System requirements check failed"
        exit 1
    fi
    
    if [[ "$CHECK_ONLY" == "true" ]]; then
        print_info "Check-only mode - stopping after system check"
        exit 0
    fi
    
    # Stop Node processes
    stop_node_processes
    
    # Check for file locks
    check_file_locks
    
    if [[ "$CLEAN_ONLY" == "true" ]]; then
        print_info "Clean-only mode - stopping after cleanup"
        remove_node_modules
        clear_npm_cache
        exit 0
    fi
    
    # Clean installation
    if [[ "$REINSTALL_ONLY" != "true" ]]; then
        remove_node_modules
        clear_npm_cache
    fi
    
    # Install dependencies
    if install_dependencies "$STRATEGY"; then
        # Verify installation
        if test_installation; then
            print_success "NPM troubleshooting completed successfully!"
            print_info "You can now run: npm run dev"
        else
            print_warning "Installation completed but verification found issues"
            print_info "Try running with different strategy: --strategy force-legacy"
        fi
    else
        print_error "Installation failed. Try different strategies:"
        print_info "  $0 --strategy force"
        print_info "  $0 --strategy legacy"
        print_info "  $0 --strategy force-legacy"
        exit 1
    fi
}

# Run main function
main "$@"
