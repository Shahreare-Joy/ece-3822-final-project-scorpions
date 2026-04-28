/*
jitter_buffer.cpp - Implementation of JitterBuffer class

Author: Shahreare Joy
Date: 02/27/2026
Project: Project 2 - Network Position Buffering
*/

#include "jitter_buffer.h"
#include <stdexcept>

// Constructor
JitterBuffer::JitterBuffer(int buffer_capacity, int min_size)
    : CircularBuffer<Position>(buffer_capacity),
      min_buffer_size(min_size),
      playback_started(false),
      start_timestamp(0)
{
    if (min_buffer_size < 1) {
        min_buffer_size = 1;
    }
}

void JitterBuffer::add_position(float x, float y, long timestamp) {
    // TODO: Create Position object
    // TODO: Try to enqueue it
    // TODO: If buffer is full (enqueue returns false):
    //       - Dequeue oldest position to make room
    //       - Then enqueue the new position
    
    // TODO: If playback hasn't started yet AND buffer size >= min_buffer_size:
    //       - Set playback_started = true
    //       - Record start_timestamp = timestamp
    Position p(x, y, timestamp);

    // tries to add new position to buffer
    if (!enqueue(p)) {
        dequeue();  // Remove oldest
        enqueue(p); // Add new position
    }

    // checks if playback can start
    if (!playback_started && size() >= min_buffer_size) {
        playback_started = true;
        start_timestamp = timestamp;
    }
}

Position JitterBuffer::get_current_position() {
    // TODO: If playback hasn't started:
    //       - throw std::runtime_error("Buffering... waiting for minimum positions")
    
    // TODO: If buffer is empty:
    //       - throw std::runtime_error("Buffer underrun - no positions available")
    
    // TODO: Dequeue and return the oldest position
    //       This gives steady FIFO playback
    if (!playback_started) {
        throw std::runtime_error("Buffering... waiting for minimum positions");
    }

    if (is_empty()) {
        throw std::runtime_error("Buffer underrun - no positions available");
    }

    return dequeue();
}

bool JitterBuffer::is_ready() const {
    // TODO: Return true if playback_started OR size() >= min_buffer_size
    return playback_started || size() >= min_buffer_size;

}

int JitterBuffer::get_latency_ms() const {
    // TODO: If not started, return 0
    // TODO: Estimate latency as: size() * average_time_between_updates
    //       For simplicity, assume ~50ms between updates
    //       So latency ≈ size() * 50
    if (!playback_started) {
        return 0;
    }
    return size() * 50; // Approximate latency in ms
}

int JitterBuffer::get_buffer_health() const {
    // TODO: Return (size() * 100) / capacity
    return (size() * 100) / capacity;
}

void JitterBuffer::reset() {
    // TODO: Call clear() to empty buffer
    // TODO: Set playback_started = false
    // TODO: Set start_timestamp = 0
    clear();
    playback_started = false;
    start_timestamp = 0;
}
