/*
position_smoother.cpp - Implementation of PositionSmoother class

Author: Shahreare Joy
Date: 02/27/2026
Project: Project 2 - Network Position Buffering
*/

#include "position_smoother.h"
#include <stdexcept>
#include <cmath>

// Constructor
PositionSmoother::PositionSmoother(int buffer_size)
    : CircularBuffer<Position>(buffer_size) {}

void PositionSmoother::add_position(float x, float y, long timestamp) {
    // TODO: Create a Position object with x, y, timestamp
    // TODO: Try to enqueue it
    // TODO: If buffer is full (enqueue returns false):
    //       - Dequeue the oldest position to make room
    //       - Then enqueue the new position
    
    // creating position object
    Position p(x, y, timestamp);
    
    if (!enqueue(p)) {
        dequeue();  // Remove oldest
        enqueue(p); // Add new position
    }
}

Position PositionSmoother::get_simple_average() const {
    // TODO: Check if buffer is empty
    // TODO: If empty, throw std::runtime_error("No positions to average")
    // TODO: Initialize sum_x = 0, sum_y = 0
    // TODO: Loop through all positions (use size() and get(i)):
    //       - sum_x += position.x
    //       - sum_y += position.y
    // TODO: Calculate average: avg_x = sum_x / size(), avg_y = sum_y / size()
    // TODO: Return Position(avg_x, avg_y)
    if (is_empty()) {
        throw std::runtime_error("No positions to average");
    }

    double sum_x = 0.0;
    double sum_y = 0.0;

    // number of stored positions
    int n = size();

    // loops through all stored positions
    for (int i = 0; i < n; i++) {
        Position p = get(i);
        sum_x += p.x;
        sum_y += p.y;
    }

    // calculates average
    Position avg;
    avg.x = static_cast<float>(sum_x / n);
    avg.y = static_cast<float>(sum_y / n);
    avg.timestamp = get_latest().timestamp; // Use timestamp of latest position for average
    
    return avg;
}

Position PositionSmoother::get_weighted_average() const {
    // TODO: Check if buffer is empty
    // TODO: Initialize sum_x = 0, sum_y = 0, total_weight = 0
    // TODO: Loop through positions with index i from 0 to size()-1:
    //       - weight = i + 1 (oldest gets 1, newest gets size())
    //       - Position p = get(i)
    //       - sum_x += p.x * weight
    //       - sum_y += p.y * weight
    //       - total_weight += weight
    // TODO: Calculate weighted average:
    //       - avg_x = sum_x / total_weight
    //       - avg_y = sum_y / total_weight
    // TODO: Return Position(avg_x, avg_y)
    if (is_empty()) {
        throw std::runtime_error("No positions to average");
    }

    int n = size();
    double sum_x = 0.0;
    double sum_y = 0.0;
    double total_weight = 0.0;

    // loops through all stored positions
    for (int i = 0; i < n; i++) {
        Position p = get(i);
        double weight = static_cast<double>(i + 1); // Oldest gets weight 1, newest gets weight n
        sum_x += p.x * weight;
        sum_y += p.y * weight;
        total_weight += weight;
    }

    // calculates weighted average
    Position avg;
    avg.x = static_cast<float>(sum_x / total_weight);
    avg.y = static_cast<float>(sum_y / total_weight);
    avg.timestamp = get_latest().timestamp; // Use timestamp of latest position for average

    return avg;
}

Position PositionSmoother::get_exponential_smooth(float alpha) const {
    // BONUS: Implement exponential smoothing
    // TODO: Check if buffer is empty
    // TODO: Start with first position as initial smooth value
    // TODO: For each subsequent position:
    //       - smooth_x = alpha * pos.x + (1-alpha) * smooth_x
    //       - smooth_y = alpha * pos.y + (1-alpha) * smooth_y
    // TODO: Return final smoothed position
    
    if (is_empty()) {
        throw std::runtime_error("No positions available");
    }

    // starting ref for smoothing
    Position smoothed = get(0);

    // loops through all positions starting from index 1
    for (int i = 1; i < size(); i++) {
        Position p = get(i);
        smoothed.x = alpha * p.x + (1.0f - alpha) * smoothed.x;
        smoothed.y = alpha * p.y + (1.0f - alpha) * smoothed.y;
    }
    return smoothed;
}

Position PositionSmoother::get_latest() const {
    // TODO: Check if empty
    // TODO: Return get(size() - 1)  (last/newest position)
    if (is_empty()) {
        throw std::runtime_error("No positions available");
    }

    // newest position is at index size() - 1
    return get(size() - 1);
}

float PositionSmoother::get_variance() const {
    if (is_empty()) {
        return 0.0f;
    }
    
    // Calculate mean
    Position mean = get_simple_average();
    
    // Calculate variance: average of squared distances from mean
    float sum_sq_dist = 0.0f;
    for (int i = 0; i < size(); i++) {
        Position p = get(i);
        float dx = p.x - mean.x;
        float dy = p.y - mean.y;
        sum_sq_dist += (dx*dx + dy*dy);
    }
    
    return std::sqrt(sum_sq_dist / size());
}
