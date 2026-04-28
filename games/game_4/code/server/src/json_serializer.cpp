/*
json_serializer.cpp - JSON serialization implementation

Author: Kevin Le    
Date: 2/5/2026
*/

#include "json_serializer.h"

std::string JSONSerializer::serialize(const Player& player) {
    
    std::ostringstream oss;
    oss << '{'
        << "\"id\":" << player.get_id() << ','
        << "\"name\":\"" << player.get_name() << "\","
        << "\"x\":" << player.get_x() << ','
        << "\"y\":" << player.get_y() << ','
        << "\"socket\":" << player.get_socket()
        << '}'; 

    // Return the serialized string
    return oss.str();  
}

Player JSONSerializer::deserialize(const std::string& data) {
    
    int id = extractInt(data, "id");
    std::string name = extractString(data, "name");
    float x = extractFloat(data, "x");
    float y = extractFloat(data, "y");
    int socket = extractInt(data, "socket");

    return Player(id, name, x, y, socket);
}

std::string JSONSerializer::getName() const {
    return "JSON";
}

// Helper function to extract integer from JSON
int JSONSerializer::extractInt(const std::string& json, const std::string& key) {
    
    size_t pos = json.find("\"" + key + "\":");
    if (pos == std::string::npos) return 0;

    pos = json.find(":", pos);
    if (pos == std::string::npos) return 0;

    size_t start = pos + 1;
    size_t end = json.find_first_of(",}", start);

    std::string value = json.substr(start, end - start);
    return std::stoi(value);
}

// Helper function to extract float from JSON
float JSONSerializer::extractFloat(const std::string& json, const std::string& key) {
    
    size_t pos = json.find("\"" + key + "\":");
    if (pos == std::string::npos) return 0.0f;

    pos = json.find(":", pos);
    if (pos == std::string::npos) return 0.0f;

    size_t start = pos + 1;
    size_t end = json.find_first_of(",}", start);

    std::string value = json.substr(start, end - start);
    return std::stof(value);
    }



// Helper function to extract string from JSON
std::string JSONSerializer::extractString(const std::string& json, const std::string& key) {

    std::string search_key = "\"" + key + "\":\"";
    size_t pos = json.find(search_key);
    if (pos == std::string::npos) {

        // Key not found 
        return "";         
    }
    
    // Move past the search string
    pos += search_key.length();
    
    // Find the closing quote
    size_t end_pos = json.find('"', pos);
    if (end_pos == std::string::npos) {

        // No closing quote found
        return "";  
    }
    
    // Extract the substring between quotes
    return json.substr(pos, end_pos - pos);
}