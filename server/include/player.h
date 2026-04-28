/*
player.h - Player class with CONFIGURABLE buffering strategy

Choose between PositionSmoother (low latency) or JitterBuffer (high smoothness)
by changing the #define below.

*/

#ifndef PLAYER_H
#define PLAYER_H

#include <string>

// ============================================
// BUFFERING STRATEGY (set by Makefile)
// ============================================
// The Makefile sets either:
//   -DUSE_POSITION_SMOOTHER (default)
//   -DUSE_JITTER_BUFFER (when BUFFER=JITTER)

#ifdef USE_JITTER_BUFFER
    #include "jitter_buffer.h"
    typedef JitterBuffer BufferStrategy;
#else
    // Default to PositionSmoother
    #include "position_smoother.h"
    typedef PositionSmoother BufferStrategy;
#endif

class Player {
private:
    int id;
    std::string name;
    float x, y;
    int socket;
    bool connected;
    std::string character_type;  // "cleric", "hobbit", "thief", "wizard"
    std::string status;          // "up", "down", "left", "right"
    
    // Buffer for smoothing (type depends on #define above)
    BufferStrategy* buffer;
    
public:
    // Constructors
    Player();
    Player(int id, std::string name, float x, float y, int socket);
    
    // Destructor
    ~Player();
    
    // Getters
    int get_id() const;
    std::string get_name() const;
    float get_x() const;
    float get_y() const;
    int get_socket() const;
    bool is_connected() const;
    std::string get_character_type() const;
    std::string get_status() const;
    
    // Setters
    void set_position(float new_x, float new_y);
    void set_name(std::string new_name);
    void set_connected(bool status);
    void set_socket(int sock);
    void set_character_type(std::string type);
    void set_status(std::string new_status);
    
    // Buffer management methods
    void add_raw_position(float new_x, float new_y);
    Position get_smoothed_position();
    
    // Operators
    bool operator==(const Player& other) const;
};

#endif