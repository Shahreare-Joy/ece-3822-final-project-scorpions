/*
text_serializer.cpp - Text serialization implementation

Author: Kevin Le
Date: 2/4/2026
*/

#include "text_serializer.h"
#include <sstream>

std::string TextSerializer::serialize(const Player& player) {

    // Format: "id|name|x|y|socket"

    std::ostringstream oss;
    oss << player.get_id() << '|'
        << player.get_name() << '|'
        << player.get_x() << '|'
        << player.get_y() << '|'
        << player.get_socket(); 
  
    return oss.str();  
}

Player TextSerializer::deserialize(const std::string& data) {
    

    std::istringstream iss(data);
    std::string token;

    int id = 0;
    std::string name;
    float x = 0.0f; 
    float y = 0.0f;
    int socket = 0;    

    // ID
    std::getline(iss, token, '|');
    id = std::stoi(token);

    // Name
    std::getline(iss, name, '|');

    // X
    std::getline(iss, token, '|');
    x = std::stof(token);

    // Y
    std::getline(iss, token, '|');
    y = std::stof(token);

    // Socket
    std::getline(iss, token, '|');
    socket = std::stoi(token);

    return Player(id, name, x, y, socket);  
}

std::string TextSerializer::getName() const {
    return "Text";
}