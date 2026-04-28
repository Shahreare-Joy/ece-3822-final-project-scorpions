/*
jitter_buffer.h - Jitter buffer using delay strategy

Delays playback until buffer has minimum positions, then plays at steady rate.
Eliminates jitter but adds latency.

Author: Shahreare Joy
Date: 02/27/2026
Project: Project 2 - Network Position Buffering
*/

#ifndef JITTER_BUFFER_H
#define JITTER_BUFFER_H

#include "circular_buffer.h"
#include "position.h"  // Position struct

/**
 * Jitter buffer - delays playback for smoothness
 * 
 * Strategy: Wait until buffer has min_buffer_size positions,
 * then consume at steady rate (FIFO).
 * 
 * Trade-off: Smooth playback but adds latency.
 */
class JitterBuffer : public CircularBuffer<Position> {
private:
    int min_buffer_size;      // Minimum positions before starting playback
    bool playback_started;    // Has playback started?
    long start_timestamp;     // When playback started
    
public:
    /**
     * Constructor
     * 
     * @param buffer_capacity Total buffer capacity
     * @param min_size Minimum positions before starting playback (default: 3)
     */
    JitterBuffer(int buffer_capacity = 10, int min_size = 3);
    
    /**
     * Add a new position to the buffer
     * 
     * @param x X coordinate
     * @param y Y coordinate
     * @param timestamp Time when position was received
     */
    void add_position(float x, float y, long timestamp);
    
    /**
     * Get current position for playback
     * 
     * Returns the position that should be displayed now, based on
     * steady playback from the buffer.
     * 
     * @return Current position to display
     * @throws std::runtime_error if playback not started yet
     */
    Position get_current_position();
    
    /**
     * Check if ready for playback
     * 
     * @return true if buffer has enough positions to start
     */
    bool is_ready() const;
    
    /**
     * Get current latency (delay added by buffering)
     * 
     * @return Approximate latency in milliseconds
     */
    int get_latency_ms() const;
    
    /**
     * Get buffer health (how full is the buffer)
     * 
     * @return Percentage full (0-100)
     */
    int get_buffer_health() const;
    
    /**
     * Reset the buffer and playback state
     */
    void reset();
};

#endif // JITTER_BUFFER_H