# Makefile for Project 2 - Game Server with Position Buffering
#
# Directory structure:
#   include/  - Header files (.h)
#   src/      - Source files (.cpp)
#
# Usage:
#   make                                    # TEXT + PositionSmoother (defaults)
#   make SERIALIZER=TEXT BUFFER=SMOOTHER    # TEXT + PositionSmoother
#   make SERIALIZER=JSON BUFFER=SMOOTHER    # JSON + PositionSmoother
#   make SERIALIZER=BINARY BUFFER=JITTER    # BINARY + JitterBuffer
#   make test                               # Build and run buffer tests
#   make all                                # Build server + tests
#   make clean                              # Remove all compiled files
#   make help                               # Show all options

CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -I include

# ============================================
# SERIALIZER SELECTION (default: TEXT)
# ============================================
SERIALIZER ?= TEXT

ifeq ($(SERIALIZER), JSON)
    CXXFLAGS += -DUSE_JSON
    SER_SUFFIX = _json
else ifeq ($(SERIALIZER), BINARY)
    CXXFLAGS += -DUSE_BINARY
    SER_SUFFIX = _binary
else
    # Default to TEXT (no flag needed)
    SER_SUFFIX = _text
endif

# ============================================
# BUFFER STRATEGY SELECTION (default: SMOOTHER)
# ============================================
BUFFER ?= SMOOTHER

ifeq ($(BUFFER), JITTER)
    CXXFLAGS += -DUSE_JITTER_BUFFER
    BUF_SUFFIX = _jitter
else
    # Default to PositionSmoother
    CXXFLAGS += -DUSE_POSITION_SMOOTHER
    BUF_SUFFIX = _smoother
endif

# Combined suffix for executable name
SUFFIX = $(SER_SUFFIX)$(BUF_SUFFIX)

# Source and object directories (serializer+buffer-specific objects)
SRC_DIR = src
INC_DIR = include
OBJ_DIR = obj$(SUFFIX)

# Create obj directory if it doesn't exist
$(shell mkdir -p $(OBJ_DIR))

# Server object files
SERVER_OBJS = $(OBJ_DIR)/player.o $(OBJ_DIR)/text_serializer.o \
              $(OBJ_DIR)/json_serializer.o $(OBJ_DIR)/binary_serializer.o

# Buffer object files (shared between server and tests)
BUFFER_OBJS = $(OBJ_DIR)/position_smoother.o $(OBJ_DIR)/jitter_buffer.o

# Default target - build server
server: server$(SUFFIX)

# Build everything
all: server$(SUFFIX) test_buffers

# Link server with buffers
server$(SUFFIX): $(SRC_DIR)/server.cpp $(SERVER_OBJS) $(BUFFER_OBJS)
	$(CXX) $(CXXFLAGS) -o server$(SUFFIX) $(SRC_DIR)/server.cpp $(SERVER_OBJS) $(BUFFER_OBJS)
	@echo ""
	@echo "===================================="
	@echo "Server compiled successfully!"
	@echo "===================================="
	@echo "Serializer: $(SERIALIZER)"
	@echo "Buffer:     $(BUFFER)"
	@echo "Executable: server$(SUFFIX)"
	@echo ""
	@echo "Run with:"
	@echo "  ./server$(SUFFIX)"
	@echo "  ./server$(SUFFIX) --port 8005"
	@echo "===================================="
	@echo ""

# Build test program (no serializer dependency, buffer-specific)
test_buffers: $(SRC_DIR)/test_buffers.cpp $(BUFFER_OBJS) $(INC_DIR)/circular_buffer.h $(INC_DIR)/position_smoother.h $(INC_DIR)/jitter_buffer.h
	$(CXX) $(CXXFLAGS) -o test_buffers $(SRC_DIR)/test_buffers.cpp $(BUFFER_OBJS)
	@echo ""
	@echo "===================================="
	@echo "Buffer tests compiled successfully!"
	@echo "===================================="
	@echo "Run with: ./test_buffers"
	@echo "===================================="
	@echo ""

# Run buffer tests
test: test_buffers
	./test_buffers

# Compile server object files
$(OBJ_DIR)/player.o: $(SRC_DIR)/player.cpp $(INC_DIR)/player.h
	$(CXX) $(CXXFLAGS) -c $(SRC_DIR)/player.cpp -o $(OBJ_DIR)/player.o

$(OBJ_DIR)/text_serializer.o: $(SRC_DIR)/text_serializer.cpp $(INC_DIR)/text_serializer.h $(INC_DIR)/serializer.h $(INC_DIR)/player.h
	$(CXX) $(CXXFLAGS) -c $(SRC_DIR)/text_serializer.cpp -o $(OBJ_DIR)/text_serializer.o

$(OBJ_DIR)/json_serializer.o: $(SRC_DIR)/json_serializer.cpp $(INC_DIR)/json_serializer.h $(INC_DIR)/serializer.h $(INC_DIR)/player.h
	$(CXX) $(CXXFLAGS) -c $(SRC_DIR)/json_serializer.cpp -o $(OBJ_DIR)/json_serializer.o

$(OBJ_DIR)/binary_serializer.o: $(SRC_DIR)/binary_serializer.cpp $(INC_DIR)/binary_serializer.h $(INC_DIR)/serializer.h $(INC_DIR)/player.h
	$(CXX) $(CXXFLAGS) -c $(SRC_DIR)/binary_serializer.cpp -o $(OBJ_DIR)/binary_serializer.o

# Compile buffer object files
$(OBJ_DIR)/position_smoother.o: $(SRC_DIR)/position_smoother.cpp $(INC_DIR)/position_smoother.h $(INC_DIR)/circular_buffer.h
	$(CXX) $(CXXFLAGS) -c $(SRC_DIR)/position_smoother.cpp -o $(OBJ_DIR)/position_smoother.o

$(OBJ_DIR)/jitter_buffer.o: $(SRC_DIR)/jitter_buffer.cpp $(INC_DIR)/jitter_buffer.h $(INC_DIR)/circular_buffer.h
	$(CXX) $(CXXFLAGS) -c $(SRC_DIR)/jitter_buffer.cpp -o $(OBJ_DIR)/jitter_buffer.o

# Clean up
clean:
	rm -rf obj_* server_* test_buffers
	@echo "Cleaned up all compiled files and object directories"

# Help target
help:
	@echo "=========================================="
	@echo "Project 2 Makefile - Available Options"
	@echo "=========================================="
	@echo ""
	@echo "SERIALIZER options:"
	@echo "  TEXT    - Text serialization (human-readable)"
	@echo "  JSON    - JSON serialization"
	@echo "  BINARY  - Binary serialization (compact)"
	@echo ""
	@echo "BUFFER options:"
	@echo "  SMOOTHER - PositionSmoother (low latency, good smoothness)"
	@echo "  JITTER   - JitterBuffer (high latency, perfect smoothness)"
	@echo ""
	@echo "Examples:"
	@echo "  make                                    # Defaults (TEXT + SMOOTHER)"
	@echo "  make SERIALIZER=JSON                    # JSON + SMOOTHER"
	@echo "  make BUFFER=JITTER                      # TEXT + JITTER"
	@echo "  make SERIALIZER=BINARY BUFFER=JITTER    # BINARY + JITTER"
	@echo "  make test                               # Run buffer tests"
	@echo "  make clean                              # Remove all compiled files"
	@echo ""
	@echo "All combinations:"
	@echo "  server_text_smoother     - TEXT + PositionSmoother"
	@echo "  server_text_jitter       - TEXT + JitterBuffer"
	@echo "  server_json_smoother     - JSON + PositionSmoother"
	@echo "  server_json_jitter       - JSON + JitterBuffer"
	@echo "  server_binary_smoother   - BINARY + PositionSmoother"
	@echo "  server_binary_jitter     - BINARY + JitterBuffer"
	@echo "=========================================="

# Phony targets
.PHONY: all server test clean help