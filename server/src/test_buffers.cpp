/*
test_buffers.cpp - Test circular buffer and position smoother

Compile: g++ -std=c++11 test_buffers.cpp -o test_buffers
Run: ./test_buffers

Author: [Instructor]
Project: Project 2 - Network Position Buffering
*/

#include <iostream>
#include <cassert>
#include <cmath>
#include "circular_buffer.h"
#include "position_smoother.h"
#include "jitter_buffer.h"

void test_circular_buffer() {
    std::cout << "Testing CircularBuffer...\n";
    
    CircularBuffer<int> buffer(3);
    
    // Test empty buffer
    assert(buffer.is_empty());
    assert(!buffer.is_full());
    assert(buffer.size() == 0);
    std::cout << "  ✓ Empty buffer\n";
    
    // Test enqueue
    assert(buffer.enqueue(10));
    assert(buffer.enqueue(20));
    assert(buffer.enqueue(30));
    assert(buffer.size() == 3);
    assert(buffer.is_full());
    std::cout << "  ✓ Enqueue to full\n";
    
    // Test enqueue when full
    assert(!buffer.enqueue(40));  // Should fail
    std::cout << "  ✓ Enqueue when full fails\n";
    
    // Test get
    assert(buffer.get(0) == 10);  // Oldest
    assert(buffer.get(1) == 20);
    assert(buffer.get(2) == 30);  // Newest
    std::cout << "  ✓ Get by index\n";
    
    // Test dequeue
    assert(buffer.dequeue() == 10);
    assert(buffer.dequeue() == 20);
    assert(buffer.size() == 1);
    std::cout << "  ✓ Dequeue\n";
    
    // Test wrap-around
    buffer.enqueue(40);
    buffer.enqueue(50);
    assert(buffer.get(0) == 30);
    assert(buffer.get(1) == 40);
    assert(buffer.get(2) == 50);
    std::cout << "  ✓ Wrap-around\n";
    
    std::cout << "CircularBuffer tests passed!\n\n";
}

void test_position_smoother() {
    std::cout << "Testing PositionSmoother...\n";
    
    PositionSmoother smoother(5);
    
    // Add positions simulating jittery network data
    smoother.add_position(100.0f, 100.0f);
    smoother.add_position(110.0f, 105.0f);
    smoother.add_position(105.0f, 110.0f);  // Jumped back (jitter)
    smoother.add_position(115.0f, 115.0f);
    smoother.add_position(120.0f, 120.0f);
    
    std::cout << "  Added 5 positions with jitter\n";
    
    // Test simple average
    Position avg = smoother.get_simple_average();
    std::cout << "  Simple average: (" << avg.x << ", " << avg.y << ")\n";
    assert(std::abs(avg.x - 110.0f) < 1.0f);  // Should be around 110
    assert(std::abs(avg.y - 110.0f) < 1.0f);
    std::cout << "  ✓ Simple average\n";
    
    // Test weighted average
    Position weighted = smoother.get_weighted_average();
    std::cout << "  Weighted average: (" << weighted.x << ", " << weighted.y << ")\n";
    assert(weighted.x > avg.x);  // Should favor newer (higher) positions
    assert(weighted.y > avg.y);
    std::cout << "  ✓ Weighted average (favors recent)\n";
    
    // Test latest
    Position latest = smoother.get_latest();
    assert(latest.x == 120.0f);
    assert(latest.y == 120.0f);
    std::cout << "  ✓ Get latest position\n";
    
    // Test variance
    float variance = smoother.get_variance();
    std::cout << "  Variance (jitter): " << variance << "\n";
    assert(variance > 0);  // Should have some variance
    std::cout << "  ✓ Variance calculation\n";
    
    std::cout << "PositionSmoother tests passed!\n\n";
}

void test_smoothing_effect() {
    std::cout << "Testing smoothing effect on jittery data...\n";
    
    PositionSmoother smoother(5);
    
    // Simulate very jittery network positions
    float positions[][2] = {
        {100, 100},
        {150, 105},  // Big jump
        {105, 150},  // Jump in Y
        {110, 110},
        {200, 115},  // Another big jump
        {115, 115},
        {120, 120}
    };
    
    std::cout << "\n  Position | Simple Avg | Weighted Avg | Latest (no smoothing)\n";
    std::cout << "  ---------|------------|--------------|-------------------\n";
    
    for (int i = 0; i < 7; i++) {
        smoother.add_position(positions[i][0], positions[i][1]);
        
        if (smoother.size() >= 3) {  // Need at least 3 positions for good average
            Position simple = smoother.get_simple_average();
            Position weighted = smoother.get_weighted_average();
            Position latest = smoother.get_latest();
            
            printf("  (%3.0f,%3.0f) | (%6.1f,%6.1f) | (%6.1f,%6.1f) | (%3.0f,%3.0f)\n",
                   positions[i][0], positions[i][1],
                   simple.x, simple.y,
                   weighted.x, weighted.y,
                   latest.x, latest.y);
        }
    }
    
    std::cout << "\n  Notice: Averaged positions are smoother than raw positions\n";
    std::cout << "          Weighted average responds faster to movement\n\n";
}

void test_jitter_buffer() {
    std::cout << "Testing JitterBuffer...\n";
    
    JitterBuffer jbuffer(10, 3);  // Capacity 10, min 3 positions
    
    // Initially not ready
    assert(!jbuffer.is_ready());
    std::cout << "  ✓ Initially not ready\n";
    
    // Add positions
    jbuffer.add_position(100.0f, 100.0f, 0);
    jbuffer.add_position(110.0f, 110.0f, 50);
    assert(!jbuffer.is_ready());  // Still need 1 more
    
    jbuffer.add_position(120.0f, 120.0f, 100);
    assert(jbuffer.is_ready());  // Now ready!
    std::cout << "  ✓ Ready after min positions\n";
    
    // Get positions in FIFO order
    Position p1 = jbuffer.get_current_position();
    assert(p1.x == 100.0f && p1.y == 100.0f);
    
    Position p2 = jbuffer.get_current_position();
    assert(p2.x == 110.0f && p2.y == 110.0f);
    std::cout << "  ✓ FIFO playback order\n";
    
    // Check latency
    int latency = jbuffer.get_latency_ms();
    std::cout << "  Current latency: " << latency << "ms\n";
    assert(latency > 0);
    std::cout << "  ✓ Latency calculation\n";
    
    std::cout << "JitterBuffer tests passed!\n\n";
}

void test_strategy_comparison() {
    std::cout << "Comparing Strategies: JitterBuffer vs PositionSmoother\n";
    std::cout << "=========================================================\n\n";
    
    // Simulate jittery network arrivals
    float jittery_positions[][3] = {
        // x, y, timestamp (ms)
        {100, 100, 0},
        {110, 110, 20},     // Arrived early (expected 50ms)
        {105, 105, 150},    // Arrived late! (big gap)
        {120, 120, 160},    // Arrived quickly after
        {125, 125, 170},
        {130, 130, 220},
        {135, 135, 230},
        {140, 140, 280}
    };
    
    JitterBuffer jbuffer(10, 3);
    PositionSmoother smoother(5);
    
    std::cout << "Input (jittery network):\n";
    std::cout << "  Time | Position  | Gap\n";
    std::cout << "  -----|-----------|-----\n";
    
    for (int i = 0; i < 8; i++) {
        int gap = (i > 0) ? (jittery_positions[i][2] - jittery_positions[i-1][2]) : 0;
        printf("  %4.0fms | (%3.0f,%3.0f) | %4dms\n",
               jittery_positions[i][2], 
               jittery_positions[i][0], 
               jittery_positions[i][1],
               gap);
        
        jbuffer.add_position(jittery_positions[i][0], jittery_positions[i][1], 
                             (long)jittery_positions[i][2]);
        smoother.add_position(jittery_positions[i][0], jittery_positions[i][1], 
                              (long)jittery_positions[i][2]);
    }
    
    std::cout << "\nStrategy Comparison:\n\n";
    std::cout << "  JitterBuffer (delay strategy):\n";
    std::cout << "    - Latency: ~" << jbuffer.get_latency_ms() << "ms\n";
    std::cout << "    - Buffer health: " << jbuffer.get_buffer_health() << "%\n";
    std::cout << "    - Trade-off: HIGH latency, PERFECT smoothness\n";
    std::cout << "    - Best for: Watching replays, spectating\n\n";
    
    std::cout << "  PositionSmoother (averaging strategy):\n";
    Position avg = smoother.get_simple_average();
    Position weighted = smoother.get_weighted_average();
    std::cout << "    - Simple avg: (" << avg.x << ", " << avg.y << ")\n";
    std::cout << "    - Weighted avg: (" << weighted.x << ", " << weighted.y << ")\n";
    std::cout << "    - Latency: ~" << (smoother.size() * 25) << "ms (estimated)\n";
    std::cout << "    - Trade-off: LOW latency, GOOD smoothness\n";
    std::cout << "    - Best for: Real-time gameplay\n\n";
    
    std::cout << "Recommendation: Use PositionSmoother for your game!\n\n";
}

int main() {
    std::cout << "========================================\n";
    std::cout << "Project 2: Buffer Tests\n";
    std::cout << "========================================\n\n";
    
    try {
        test_circular_buffer();
        test_position_smoother();
        test_smoothing_effect();
        test_jitter_buffer();
        test_strategy_comparison();
        
        std::cout << "========================================\n";
        std::cout << "✓ ALL TESTS PASSED!\n";
        std::cout << "========================================\n";
        
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "\n❌ TEST FAILED: " << e.what() << "\n";
        return 1;
    }
}
