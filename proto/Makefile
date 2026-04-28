PROTO_DIR := $(shell pwd)
PROJECT_ROOT := $(shell dirname $(PROTO_DIR))
BACKEND_OUT := $(PROJECT_ROOT)/backend/app/grpc/generated
ANALYZER_OUT := $(PROJECT_ROOT)/services/analyzer/app/grpc/generated
FRONTEND_OUT := $(PROJECT_ROOT)/frontend/src/grpc/generated

PROTO_FILES := common.proto screenshot.proto chat.proto analyzer.proto system.proto

.PHONY: all python typescript backend analyzer frontend clean help

help:
	@echo "Proto generation targets:"
	@echo "  all        - Generate all bindings (Python + TypeScript)"
	@echo "  python     - Generate Python bindings for backend and analyzer"
	@echo "  typescript - Generate TypeScript bindings for frontend"
	@echo "  backend    - Generate Python bindings for backend only"
	@echo "  analyzer   - Generate Python bindings for analyzer only"
	@echo "  frontend   - Generate TypeScript bindings for frontend only"
	@echo "  clean      - Remove all generated files"

all: python typescript

python: backend analyzer

backend:
	@echo "Generating Python bindings for backend..."
	@mkdir -p $(BACKEND_OUT)
	python3 -m grpc_tools.protoc \
		-I$(PROTO_DIR) \
		--python_out=$(BACKEND_OUT) \
		--grpc_python_out=$(BACKEND_OUT) \
		--pyi_out=$(BACKEND_OUT) \
		$(addprefix $(PROTO_DIR)/,$(PROTO_FILES))
	@echo "Fixing imports..."
	@for f in $(BACKEND_OUT)/*_pb2*.py; do \
		sed -i.bak 's/^import common_pb2/from . import common_pb2/g' "$$f"; \
		sed -i.bak 's/^import screenshot_pb2/from . import screenshot_pb2/g' "$$f"; \
		sed -i.bak 's/^import chat_pb2/from . import chat_pb2/g' "$$f"; \
		sed -i.bak 's/^import analyzer_pb2/from . import analyzer_pb2/g' "$$f"; \
		sed -i.bak 's/^import system_pb2/from . import system_pb2/g' "$$f"; \
		rm -f "$$f.bak"; \
	done
	@echo "Backend bindings generated"

analyzer:
	@echo "Generating Python bindings for analyzer..."
	@mkdir -p $(ANALYZER_OUT)
	python3 -m grpc_tools.protoc \
		-I$(PROTO_DIR) \
		--python_out=$(ANALYZER_OUT) \
		--grpc_python_out=$(ANALYZER_OUT) \
		--pyi_out=$(ANALYZER_OUT) \
		$(addprefix $(PROTO_DIR)/,$(PROTO_FILES))
	@echo "Fixing imports..."
	@for f in $(ANALYZER_OUT)/*_pb2*.py; do \
		sed -i.bak 's/^import common_pb2/from . import common_pb2/g' "$$f"; \
		sed -i.bak 's/^import screenshot_pb2/from . import screenshot_pb2/g' "$$f"; \
		sed -i.bak 's/^import chat_pb2/from . import chat_pb2/g' "$$f"; \
		sed -i.bak 's/^import analyzer_pb2/from . import analyzer_pb2/g' "$$f"; \
		sed -i.bak 's/^import system_pb2/from . import system_pb2/g' "$$f"; \
		rm -f "$$f.bak"; \
	done
	@echo "Analyzer bindings generated"

typescript: frontend

frontend:
	@echo "Generating TypeScript bindings for frontend..."
	@mkdir -p $(FRONTEND_OUT)
	cd $(PROJECT_ROOT)/frontend && npm run proto:generate

clean:
	@echo "Cleaning generated files..."
	rm -f $(BACKEND_OUT)/*.py $(BACKEND_OUT)/*.pyi
	rm -f $(ANALYZER_OUT)/*.py $(ANALYZER_OUT)/*.pyi
	rm -f $(FRONTEND_OUT)/*.ts $(FRONTEND_OUT)/*.js
	@echo "Clean complete"
