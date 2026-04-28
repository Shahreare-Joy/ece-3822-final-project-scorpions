// Scorpions Arcade C++ multiplayer server entry point.
//
// This is a small demo-ready TCP state relay for Fruit Drop Rush. It is not
// the final authoritative game server, but it gives the current Python game a
// real connection path:
//
//   client sends: UPDATE|id|x|y|name|character_type|status
//   server sends: CONNECTED|id
//   server sends: STATE||id|name|x|y|socket|character_type|status||...
//
// TODO(C++ FINAL): Add real session validation, lobby management, chat relay,
// anti-cheat checks, and final score reporting back to the Python platform.

#include <algorithm>
#include <atomic>
#include <cerrno>
#include <csignal>
#include <ctime>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <map>
#include <mutex>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#ifdef _WIN32
#define NOMINMAX
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")
using SocketHandle = SOCKET;
using SockLen = int;
const SocketHandle INVALID_SOCKET_HANDLE = INVALID_SOCKET;
#else
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
using SocketHandle = int;
using SockLen = socklen_t;
const SocketHandle INVALID_SOCKET_HANDLE = -1;
#endif

namespace {

const int kAllowedPorts[] = {50068, 50069, 50075, 50082};
const int kDefaultPort = 50068;
const int kSocketPollTimeoutMs = 2000;
const int kStalePlayerTimeoutSeconds = 90;
std::atomic<bool> g_running(true);

struct PlayerState {
    int id = 0;
    int socket_number = 0;
    float x = 0.0f;
    float y = 0.0f;
    std::string name = "Player";
    std::string character_type = "";
    std::string status = "down";
};

std::mutex g_players_mutex;
std::map<int, PlayerState> g_players;
std::atomic<int> g_next_player_id(1);

bool is_allowed_port(int port) {
    for (int allowed : kAllowedPorts) {
        if (port == allowed) {
            return true;
        }
    }
    return false;
}

int normalize_port(int port) {
    return is_allowed_port(port) ? port : kDefaultPort;
}

std::vector<std::string> split_pipe(const std::string& text) {
    std::vector<std::string> parts;
    std::stringstream stream(text);
    std::string part;
    while (std::getline(stream, part, '|')) {
        parts.push_back(part);
    }
    return parts;
}

std::string player_to_wire(const PlayerState& player) {
    std::ostringstream out;
    out << player.id << "|"
        << player.name << "|"
        << player.x << "|"
        << player.y << "|"
        << player.socket_number << "|"
        << player.character_type << "|"
        << player.status;
    return out.str();
}

std::string build_state_message() {
    std::lock_guard<std::mutex> lock(g_players_mutex);
    std::ostringstream out;
    out << "STATE";
    for (const auto& entry : g_players) {
        out << "||" << player_to_wire(entry.second);
    }
    out << "\n";
    return out.str();
}

bool send_all(SocketHandle socket_handle, const std::string& message) {
    const char* data = message.c_str();
    int remaining = static_cast<int>(message.size());
    while (remaining > 0) {
        int sent = send(socket_handle, data, remaining, 0);
        if (sent <= 0) {
            return false;
        }
        data += sent;
        remaining -= sent;
    }
    return true;
}

void close_socket(SocketHandle socket_handle) {
#ifdef _WIN32
    closesocket(socket_handle);
#else
    close(socket_handle);
#endif
}

void set_socket_timeout(SocketHandle socket_handle) {
#ifdef _WIN32
    DWORD timeout_ms = kSocketPollTimeoutMs;
    setsockopt(socket_handle, SOL_SOCKET, SO_RCVTIMEO,
               reinterpret_cast<const char*>(&timeout_ms), sizeof(timeout_ms));
#else
    timeval timeout;
    timeout.tv_sec = kSocketPollTimeoutMs / 1000;
    timeout.tv_usec = (kSocketPollTimeoutMs % 1000) * 1000;
    setsockopt(socket_handle, SOL_SOCKET, SO_RCVTIMEO,
               reinterpret_cast<const char*>(&timeout), sizeof(timeout));
#endif
}

bool socket_timed_out() {
#ifdef _WIN32
    int error = WSAGetLastError();
    return error == WSAETIMEDOUT || error == WSAEWOULDBLOCK;
#else
    return errno == EAGAIN || errno == EWOULDBLOCK;
#endif
}

void update_player_from_message(int player_id, const std::string& line) {
    std::vector<std::string> parts = split_pipe(line);
    if (parts.size() < 5 || parts[0] != "UPDATE") {
        return;
    }

    std::lock_guard<std::mutex> lock(g_players_mutex);
    auto found = g_players.find(player_id);
    if (found == g_players.end()) {
        return;
    }

    try {
        found->second.x = std::stof(parts[2]);
        found->second.y = std::stof(parts[3]);
    } catch (...) {
        return;
    }

    if (parts.size() > 4 && !parts[4].empty()) {
        found->second.name = parts[4];
    }
    if (parts.size() > 5) {
        found->second.character_type = parts[5];
    }
    if (parts.size() > 6) {
        found->second.status = parts[6];
    }
}

void client_thread(SocketHandle client_socket) {
    set_socket_timeout(client_socket);
    int player_id = g_next_player_id.fetch_add(1);
    {
        std::lock_guard<std::mutex> lock(g_players_mutex);
        PlayerState player;
        player.id = player_id;
        player.socket_number = static_cast<int>(player_id);
        g_players[player_id] = player;
    }

    send_all(client_socket, "CONNECTED|" + std::to_string(player_id) + "\n");
    std::cout << "Player " << player_id << " connected." << std::endl;

    std::string buffer;
    char recv_buffer[4096];
    std::time_t last_seen = std::time(nullptr);
    while (g_running.load()) {
        int received = recv(client_socket, recv_buffer, sizeof(recv_buffer) - 1, 0);
        if (received <= 0) {
            if (socket_timed_out()) {
                if (std::time(nullptr) - last_seen > kStalePlayerTimeoutSeconds) {
                    break;
                }
                continue;
            }
            break;
        }
        last_seen = std::time(nullptr);

        recv_buffer[received] = '\0';
        buffer += recv_buffer;

        std::size_t newline_pos = std::string::npos;
        while ((newline_pos = buffer.find('\n')) != std::string::npos) {
            std::string line = buffer.substr(0, newline_pos);
            buffer.erase(0, newline_pos + 1);
            update_player_from_message(player_id, line);
            send_all(client_socket, build_state_message());
        }
    }

    {
        std::lock_guard<std::mutex> lock(g_players_mutex);
        g_players.erase(player_id);
    }

    close_socket(client_socket);
    std::cout << "Player " << player_id << " disconnected." << std::endl;
}

void handle_signal(int) {
    g_running.store(false);
}

}  // namespace

int main(int argc, char* argv[]) {
    int requested_port = kDefaultPort;
    if (argc >= 2) {
        requested_port = std::atoi(argv[1]);
    }
    int port = normalize_port(requested_port);
    if (port != requested_port) {
        std::cout << "Unsupported port " << requested_port
                  << "; using allowed default " << port << "." << std::endl;
    }

    std::signal(SIGINT, handle_signal);

#ifdef _WIN32
    WSADATA wsa_data;
    if (WSAStartup(MAKEWORD(2, 2), &wsa_data) != 0) {
        std::cerr << "WSAStartup failed." << std::endl;
        return 1;
    }
#endif

    SocketHandle server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == INVALID_SOCKET_HANDLE) {
        std::cerr << "Could not create server socket." << std::endl;
        return 1;
    }

    int option_value = 1;
    setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR,
               reinterpret_cast<const char*>(&option_value), sizeof(option_value));
    set_socket_timeout(server_socket);

    sockaddr_in address;
    std::memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(static_cast<unsigned short>(port));

    if (bind(server_socket, reinterpret_cast<sockaddr*>(&address), sizeof(address)) < 0) {
        std::cerr << "Could not bind to port " << port << "." << std::endl;
        close_socket(server_socket);
        return 1;
    }

    if (listen(server_socket, 16) < 0) {
        std::cerr << "Could not listen on port " << port << "." << std::endl;
        close_socket(server_socket);
        return 1;
    }

    std::cout << "Scorpions C++ demo multiplayer server running on port " << port << "." << std::endl;
    std::cout << "Allowed class ports: 50068, 50069, 50075, 50082." << std::endl;
    std::cout << "Press Ctrl+C to stop." << std::endl;

    while (g_running.load()) {
        sockaddr_in client_address;
        SockLen client_length = sizeof(client_address);
        SocketHandle client_socket = accept(
            server_socket,
            reinterpret_cast<sockaddr*>(&client_address),
            &client_length
        );
        if (client_socket == INVALID_SOCKET_HANDLE) {
            if (socket_timed_out()) {
                continue;
            }
            if (g_running.load()) {
                std::cerr << "Accept failed." << std::endl;
            }
            continue;
        }

        std::thread(client_thread, client_socket).detach();
    }

    close_socket(server_socket);
#ifdef _WIN32
    WSACleanup();
#endif
    return 0;
}
