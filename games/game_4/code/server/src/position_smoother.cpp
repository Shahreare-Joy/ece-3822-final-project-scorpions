/*
position_smoother.cpp - Implementation of PositionSmoother class

Author: Kevin Le
Date: 3/1/2026
Project: Project 2 - Network Position Buffering
*/

#include "position_smoother.h"
#include <stdexcept>
#include <cmath>

PositionSmoother::PositionSmoother(int buffer_size)
    : CircularBuffer<Position>(buffer_size) {}

void PositionSmoother::add_position(float x, float y, long timestamp) {
    Position new_pos = {x, y, timestamp};

    if (!enqueue(new_pos)) {
        dequeue();          // Remove oldest
        enqueue(new_pos);   // Add new position
    }
}

Position PositionSmoother::get_simple_average() const {
    if (is_empty()) {
        throw std::runtime_error("No positions to average");
    }

    float sum_x = 0.0f;
    float sum_y = 0.0f;
    int n = size();

    for (int i = 0; i < n; ++i) {
        Position p = get(i);
        sum_x += p.x;
        sum_y += p.y;
    }

    return Position{sum_x / n, sum_y / n, 0};
}

Position PositionSmoother::get_weighted_average() const {
    if (is_empty()) {
        throw std::runtime_error("Buffer is empty");
    }
    
    float sum_x = 0.0f;
    float sum_y = 0.0f;
    int total_weight = 0;
    int n = size(); 
    for (int i = 0; i < n; ++i) {
        int weight = i + 1;
        Position p = get(i);
        sum_x += p.x * weight;
        sum_y += p.y * weight;
        total_weight += weight;
    }
    return Position{sum_x / total_weight, sum_y / total_weight, 0}; 
}

Position PositionSmoother::get_exponential_smooth(float alpha) const {
    if (is_empty()) {
        throw std::runtime_error("Buffer is empty");
    }
    Position smoothed_pos = get(0);  // Start with oldest position as initial smoothed value
    
    for (int i = 1; i < size(); ++i) {
        Position pos = get(i);
        smoothed_pos.x = alpha * pos.x + (1 - alpha) * smoothed_pos.x;
        smoothed_pos.y = alpha * pos.y + (1 - alpha) * smoothed_pos.y;
    }
    return smoothed_pos;
}

Position PositionSmoother::get_latest() const {
    if (is_empty()) {
        throw std::runtime_error("Buffer is empty");
    }
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
