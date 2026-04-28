/*
player.cpp - Player implementation with switchable buffering strategy

Works with both PositionSmoother and JitterBuffer based on header #define.

*/

#include "player.h"
#include <sys/time.h>
#include <iostream>

// Helper to get current timestamp in milliseconds
static long get_timestamp_ms() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000 + tv.tv_usec / 1000;
}

// Default constructor
Player::Player() {
    id = 0;
    name = "";
    x = 400.0;
    y = 300.0;
    socket = -1;
    connected = false;
    character_type = "";
    status = "down";
    
    // Initialize buffer based on strategy
    #ifdef USE_POSITION_SMOOTHER
        buffer = new PositionSmoother(5);  // Buffer size 5
        std::cout << "[BUFFER] Using PositionSmoother (low latency)\n";
    #else
        buffer = new JitterBuffer(10, 3);  // Capacity 10, min 3
        std::cout << "[BUFFER] Using JitterBuffer (high smoothness)\n";
    #endif
}

// Parameterized constructor
Player::Player(int id, std::string name, float x, float y, int socket) {
    this->id = id;
    this->name = name;
    this->x = x;
    this->y = y;
    this->socket = socket;
    this->connected = true;
    this->character_type = "";
    this->status = "down";
    
    // Initialize buffer based on strategy
    #ifdef USE_POSITION_SMOOTHER
        buffer = new PositionSmoother(5);
        std::cout << "[BUFFER] Player " << id << " using PositionSmoother\n";
    #else
        buffer = new JitterBuffer(10, 3);
        std::cout << "[BUFFER] Player " << id << " using JitterBuffer\n";
    #endif
    
    // Add initial position
    buffer->add_position(x, y, get_timestamp_ms());
}

// Destructor
Player::~Player() {
    delete buffer;
}

// Getters
int Player::get_id() const { return id; }
std::string Player::get_name() const { return name; }
float Player::get_x() const { return x; }
float Player::get_y() const { return y; }
int Player::get_socket() const { return socket; }
bool Player::is_connected() const { return connected; }
std::string Player::get_character_type() const { return character_type; }
std::string Player::get_status() const { return status; }

// Setters
void Player::set_position(float new_x, float new_y) {
    x = new_x;
    y = new_y;
}

void Player::set_name(std::string new_name) {
    name = new_name;
}

void Player::set_connected(bool status) {
    connected = status;
}

void Player::set_socket(int sock) {
    socket = sock;
}

void Player::set_character_type(std::string type) {
    character_type = type;
}

void Player::set_status(std::string new_status) {
    status = new_status;
}

// Add raw network position to buffer
void Player::add_raw_position(float new_x, float new_y) {
    buffer->add_position(new_x, new_y, get_timestamp_ms());
}

// Get smoothed position from buffer
Position Player::get_smoothed_position() {
    try {
        #ifdef USE_POSITION_SMOOTHER
            // PositionSmoother: Use weighted average
            return buffer->get_weighted_average();
        #else
            // JitterBuffer: Get current playback position
            if (buffer->is_ready()) {
                return buffer->get_current_position();
            } else {
                // Still buffering, return current position
                return Position(x, y);
            }
        #endif
    } catch (...) {
        // If buffer error, return current position
        return Position(x, y);
    }
}

// Equality operator
bool Player::operator==(const Player& other) const {
    return id == other.id;
}