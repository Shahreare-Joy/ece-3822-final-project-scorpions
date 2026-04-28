# Enhanced Makefile Usage Guide

## Integration with Previous Projects

This builds on Project 1's Makefile:
- **Project 1:** Switch serializers (TEXT/JSON/BINARY)
- **Project 2:** Switch serializers AND buffers (SMOOTHER/JITTER)

---

## Quick Reference

```bash
# Default (TEXT + PositionSmoother)
make

# Choose serializer only (uses PositionSmoother)
make SERIALIZER=JSON
make SERIALIZER=BINARY

# Choose buffer only (uses TEXT)
make BUFFER=JITTER

# Choose both
make SERIALIZER=JSON BUFFER=JITTER
make SERIALIZER=BINARY BUFFER=SMOOTHER

# See all options
make help
```

---

## All Possible Combinations

The Makefile creates different executables based on your choices:

| Command | Executable | Serialization | Buffer Strategy |
|---------|-----------|---------------|-----------------|
| `make` | `server_text_smoother` | TEXT | PositionSmoother |
| `make BUFFER=JITTER` | `server_text_jitter` | TEXT | JitterBuffer |
| `make SERIALIZER=JSON` | `server_json_smoother` | JSON | PositionSmoother |
| `make SERIALIZER=JSON BUFFER=JITTER` | `server_json_jitter` | JSON | JitterBuffer |
| `make SERIALIZER=BINARY` | `server_binary_smoother` | BINARY | PositionSmoother |
| `make SERIALIZER=BINARY BUFFER=JITTER` | `server_binary_jitter` | BINARY | JitterBuffer |

---

## How It Works

### 1. Preprocessor Flags

The Makefile automatically sets C++ preprocessor flags:

```makefile
# For SERIALIZER=JSON
CXXFLAGS += -DUSE_JSON

# For BUFFER=JITTER
CXXFLAGS += -DUSE_JITTER_BUFFER
```

### 2. Conditional Compilation

In `player.h` (switchable version):
```cpp
#ifdef USE_JITTER_BUFFER
    #include "jitter_buffer.h"
    typedef JitterBuffer BufferStrategy;
#else
    #include "position_smoother.h"
    typedef PositionSmoother BufferStrategy;
#endif
```

In `server.cpp` (from Project 1):
```cpp
#ifdef USE_JSON
    #define SERIALIZER_TYPE JSONSerializer
#elif defined(USE_BINARY)
    #define SERIALIZER_TYPE BinarySerializer
#else
    #define SERIALIZER_TYPE TextSerializer
#endif
```

### 3. Separate Object Directories

Each combination gets its own object directory:
```
obj_text_smoother/      # TEXT + PositionSmoother
obj_text_jitter/        # TEXT + JitterBuffer
obj_json_smoother/      # JSON + PositionSmoother
obj_json_jitter/        # JSON + JitterBuffer
obj_binary_smoother/    # BINARY + PositionSmoother
obj_binary_jitter/      # BINARY + JitterBuffer
```

This prevents recompilation conflicts!

---

## Example Workflow

### Test All Buffer Strategies with JSON

```bash
# Build with PositionSmoother
make SERIALIZER=JSON BUFFER=SMOOTHER
./server_json_smoother &

# Build with JitterBuffer
make SERIALIZER=JSON BUFFER=JITTER
./server_json_jitter --port 8081 &

# Connect clients to each and compare!
```

### Side-by-Side Comparison

**Terminal 1:**
```bash
make SERIALIZER=TEXT BUFFER=SMOOTHER
./server_text_smoother
```

**Terminal 2:**
```bash
make SERIALIZER=TEXT BUFFER=JITTER
./server_text_jitter --port 8081
```

**Terminal 3:**
```bash
cd ../game
python main.py  # Port 8080 (PositionSmoother)
```

**Terminal 4:**
```bash
cd ../game
# Edit main.py to connect to port 8081
python main.py  # Port 8081 (JitterBuffer)
```

Move around and see the difference in latency/smoothness!

---

## What Students Experience

### Building Default
```bash
$ make
==================================
Server compiled successfully!
==================================
Serializer: TEXT
Buffer:     SMOOTHER
Executable: server_text_smoother

Run with:
  ./server_text_smoother
==================================
```

### Switching to JitterBuffer
```bash
$ make BUFFER=JITTER
==================================
Server compiled successfully!
==================================
Serializer: TEXT
Buffer:     JITTER
Executable: server_text_jitter

Run with:
  ./server_text_jitter
==================================
```

### Running the Server
```bash
$ ./server_text_smoother
======================================
Game Server Started
======================================
Port: 8080
Serializer: Text
======================================
[BUFFER] Using PositionSmoother (low latency)

Server running on port 8080
Using Text serialization
Waiting for clients...
```

---

## Clean Compilation

```bash
# Remove all compiled files
make clean

# Build fresh
make SERIALIZER=JSON BUFFER=JITTER
```

---

## Tips for Students

**To experiment with strategies:**
```bash
# Try low latency first
make BUFFER=SMOOTHER
./server_text_smoother

# Then compare with high smoothness
make BUFFER=JITTER
./server_text_jitter --port 8081

# Connect clients to both and compare movement!
```

**To test their buffer implementation:**
```bash
# Make sure tests pass first
make test

# Then build server with their code
make
```

**To see all options:**
```bash
make help
```
