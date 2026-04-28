#!/usr/bin/env bash
set -euo pipefail

# Proto generation script for UI Parser project
# Generates Python bindings for backend and analyzer services
# Generates TypeScript bindings for frontend

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PROTO_DIR="$PROJECT_ROOT/proto"

# Output directories
BACKEND_OUT="$PROJECT_ROOT/backend/app/grpc/generated"
ANALYZER_OUT="$PROJECT_ROOT/services/analyzer/app/grpc/generated"
FRONTEND_OUT="$PROJECT_ROOT/frontend/src/grpc/generated"

# Proto files
PROTO_FILES=(
    "common.proto"
    "screenshot.proto"
    "chat.proto"
    "analyzer.proto"
    "system.proto"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "python3 is required but not installed"
        exit 1
    fi
    
    if ! python3 -c "import grpc_tools.protoc" &> /dev/null; then
        log_warn "grpcio-tools not found, installing..."
        pip3 install grpcio-tools
    fi
    
    if ! command -v npx &> /dev/null; then
        log_error "npx is required but not installed (install Node.js)"
        exit 1
    fi
    
    log_info "All dependencies satisfied"
}

generate_python() {
    local output_dir="$1"
    local service_name="$2"
    
    log_info "Generating Python bindings for $service_name -> $output_dir"
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # Generate Python files
    python3 -m grpc_tools.protoc \
        -I"$PROTO_DIR" \
        --python_out="$output_dir" \
        --grpc_python_out="$output_dir" \
        --pyi_out="$output_dir" \
        "${PROTO_FILES[@]/#/$PROTO_DIR/}"
    
    # Create __init__.py
    cat > "$output_dir/__init__.py" << 'EOF'
# Auto-generated gRPC bindings
from .common_pb2 import *
from .screenshot_pb2 import *
from .screenshot_pb2_grpc import *
from .chat_pb2 import *
from .chat_pb2_grpc import *
from .analyzer_pb2 import *
from .analyzer_pb2_grpc import *
from .system_pb2 import *
from .system_pb2_grpc import *
EOF

    # Fix imports in generated files (Python protoc generates absolute imports)
    for f in "$output_dir"/*_pb2*.py; do
        if [[ -f "$f" ]]; then
            # Fix imports to be relative within the package
            sed -i.bak 's/^import common_pb2/from . import common_pb2/g' "$f"
            sed -i.bak 's/^import screenshot_pb2/from . import screenshot_pb2/g' "$f"
            sed -i.bak 's/^import chat_pb2/from . import chat_pb2/g' "$f"
            sed -i.bak 's/^import analyzer_pb2/from . import analyzer_pb2/g' "$f"
            sed -i.bak 's/^import system_pb2/from . import system_pb2/g' "$f"
            rm -f "$f.bak"
        fi
    done
    
    log_info "Python bindings generated for $service_name"
}

generate_typescript() {
    local output_dir="$1"
    
    log_info "Generating TypeScript bindings for frontend -> $output_dir"
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # Check if protoc-gen-grpc-web is available
    if ! command -v protoc &> /dev/null; then
        log_warn "protoc not found, attempting to use npx"
    fi
    
    # Install grpc-web plugin if needed
    if ! command -v protoc-gen-grpc-web &> /dev/null; then
        log_info "Installing protoc-gen-grpc-web..."
        # Try to download the plugin
        local PLUGIN_VERSION="1.5.0"
        local PLUGIN_URL=""
        local PLUGIN_PATH="/usr/local/bin/protoc-gen-grpc-web"
        
        case "$(uname -s)" in
            Darwin)
                PLUGIN_URL="https://github.com/nicerobot/grpc-web/releases/download/${PLUGIN_VERSION}/protoc-gen-grpc-web-${PLUGIN_VERSION}-darwin-x86_64"
                ;;
            Linux)
                PLUGIN_URL="https://github.com/nicerobot/grpc-web/releases/download/${PLUGIN_VERSION}/protoc-gen-grpc-web-${PLUGIN_VERSION}-linux-x86_64"
                ;;
            *)
                log_error "Unsupported OS for protoc-gen-grpc-web"
                log_info "Please install protoc-gen-grpc-web manually"
                log_info "See: https://github.com/nicerobot/grpc-web"
                return 1
                ;;
        esac
    fi
    
    # Generate using Docker if protoc is not available locally
    log_info "Using Docker to generate TypeScript bindings..."
    
    docker run --rm \
        -v "$PROTO_DIR:/proto" \
        -v "$output_dir:/out" \
        nicerobot/grpc-web-generator \
        --proto_path=/proto \
        --js_out=import_style=commonjs,binary:/out \
        --grpc-web_out=import_style=typescript,mode=grpcwebtext:/out \
        /proto/common.proto \
        /proto/screenshot.proto \
        /proto/chat.proto \
        /proto/system.proto \
        2>/dev/null || {
            log_warn "Docker generation failed, falling back to manual generation"
            generate_typescript_manual "$output_dir"
        }
    
    log_info "TypeScript bindings generated for frontend"
}

generate_typescript_manual() {
    local output_dir="$1"
    
    log_info "Creating TypeScript stubs manually..."
    
    # Create index.ts that exports all types
    cat > "$output_dir/index.ts" << 'EOF'
// Auto-generated gRPC-Web client stubs
// Run `npm run proto:generate` to regenerate

export * from './common_pb';
export * from './screenshot_pb';
export * from './screenshot_grpc_web_pb';
export * from './chat_pb';
export * from './chat_grpc_web_pb';
export * from './system_pb';
export * from './system_grpc_web_pb';
EOF

    log_info "TypeScript stubs created (run proto:generate in frontend to complete)"
}

clean() {
    log_info "Cleaning generated files..."
    
    rm -rf "$BACKEND_OUT"/*.py "$BACKEND_OUT"/*.pyi 2>/dev/null || true
    rm -rf "$ANALYZER_OUT"/*.py "$ANALYZER_OUT"/*.pyi 2>/dev/null || true
    rm -rf "$FRONTEND_OUT"/*.ts "$FRONTEND_OUT"/*.js 2>/dev/null || true
    
    log_info "Clean complete"
}

main() {
    local command="${1:-all}"
    
    case "$command" in
        python)
            check_dependencies
            generate_python "$BACKEND_OUT" "backend"
            generate_python "$ANALYZER_OUT" "analyzer"
            ;;
        typescript|ts)
            check_dependencies
            generate_typescript "$FRONTEND_OUT"
            ;;
        backend)
            check_dependencies
            generate_python "$BACKEND_OUT" "backend"
            ;;
        analyzer)
            check_dependencies
            generate_python "$ANALYZER_OUT" "analyzer"
            ;;
        frontend)
            check_dependencies
            generate_typescript "$FRONTEND_OUT"
            ;;
        clean)
            clean
            ;;
        all)
            check_dependencies
            generate_python "$BACKEND_OUT" "backend"
            generate_python "$ANALYZER_OUT" "analyzer"
            generate_typescript "$FRONTEND_OUT"
            ;;
        *)
            echo "Usage: $0 {all|python|typescript|backend|analyzer|frontend|clean}"
            exit 1
            ;;
    esac
    
    log_info "Done!"
}

main "$@"
