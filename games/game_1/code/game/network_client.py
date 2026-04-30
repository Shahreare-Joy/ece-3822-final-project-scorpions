"""
network_client.py - Network client for multiplayer game

Handles connection to game server with support for three serialization formats:
- TEXT: Pipe-delimited (id|name|x|y|socket)
- JSON: {"id":1,"name":"Alice","x":100,"y":200,"socket":5}
- BINARY: Fixed 88-byte struct

Usage:
    client = NetworkClient("Alice", serializer='text')
    client = NetworkClient("Bob", serializer='json')
    client = NetworkClient("Charlie", serializer='binary')
"""

import socket
import threading
import json
import struct
import time
from threading import Event
from queue import Queue

try:
    from settings import DEFAULT_PORT, normalize_server_port
except Exception:
    DEFAULT_PORT = 50068

    def normalize_server_port(port):
        allowed = (50068, 50069, 50075, 50082)
        try:
            parsed_port = int(port)
        except (TypeError, ValueError):
            return DEFAULT_PORT
        return parsed_port if parsed_port in allowed else DEFAULT_PORT

class NetworkClient:
    def __init__(self, player_name, server_host='localhost', server_port=DEFAULT_PORT, serializer='text'):
        self.player_name = player_name
        self.server_host = server_host
        self.server_port = normalize_server_port(server_port)
        self.serializer = serializer.lower()  # 'text', 'json', or 'binary'
        
        if self.serializer not in ['text', 'json', 'binary']:
            raise ValueError(f"Invalid serializer: {serializer}. Must be 'text', 'json', or 'binary'")
        
        self.sock = None
        self.connected = False
        self.my_player_id = None
        self.disconnect_reason = ""
        
        self.update_queue = Queue()
        self.receiver_thread = None
        self.running = False
        self.handshake_received = Event()
        self.send_interval_seconds = 0.10
        self.last_send_at = 0.0
        self._send_count = 0
        self._receive_count = 0
        
        print(f"[NET] Network client using {self.serializer.upper()} serialization")
        
    def connect(self, handshake_timeout=2.0):
        """Connect to game server"""
        try:
            print(f"[NET] Connecting to gameplay server at {self.server_host}:{self.server_port}...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(1.0)
            self.sock.connect((self.server_host, self.server_port))
            self.sock.settimeout(0.5)
            self.connected = True
            self.running = True
            self.disconnect_reason = ""
            self.handshake_received.clear()
            
            self.receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receiver_thread.start()

            if not self.handshake_received.wait(handshake_timeout):
                self.disconnect_reason = f"Timed out waiting for CONNECTED handshake after {handshake_timeout:.1f}s"
                print(f"[NET] {self.disconnect_reason}")
                self.disconnect(self.disconnect_reason)
                return False
            
            print(f"[NET] Connection success: accepted CONNECTED handshake as player {self.my_player_id}.")
            return True
            
        except Exception as e:
            self.disconnect_reason = str(e)
            print(f"[NET] Failed to connect: {e}")
            self.connected = False
            return False
    
    def _receive_loop(self):
        """Background thread to receive messages from server"""
        buffer = ""
        
        while self.running and self.connected:
            try:
                data = self.sock.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    self.disconnect_reason = "Server closed the socket"
                    print(f"[NET] Disconnected: {self.disconnect_reason}")
                    self.connected = False
                    break
                
                buffer += data
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self._process_message(line)
                    
            except socket.timeout:
                continue
            except OSError as e:
                if self.running:
                    self.disconnect_reason = str(e)
                    print(f"[NET] Receive error: {e}")
                self.connected = False
                break
    
    def _process_message(self, msg):
        """Process a message from server"""
        msg = msg.strip()
        if not msg:
            return

        # First check message type (before any separator)
        if msg.startswith("CONNECTED|"):
            parts = msg.split('|')
            self.my_player_id = int(parts[1])
            self.handshake_received.set()
            print(f"[NET] Received handshake: {msg}")
            
        elif msg.startswith("STATE||"):
            # Game state update
            # Format: STATE||<serialized_player1>||<serialized_player2>||...
            # Players are separated by || (double pipe) to avoid conflicts with serialization formats
            parts = msg.split('||')
            self._receive_count += 1
            if self._receive_count <= 5 or self._receive_count % 30 == 0:
                print(f"[NET] Received STATE #{self._receive_count} with {len(parts)-1} player entries")
            players = {}
            
            for i in range(1, len(parts)):
                if parts[i]:
                    player_data = self._deserialize_player(parts[i])
                    if player_data:
                        players[player_data['id']] = player_data
            
            self.update_queue.put(players)
    
    def _deserialize_player(self, data):
        """Deserialize player data based on format"""
        try:
            # The current C++ demo relay broadcasts STATE frames as
            # pipe-delimited text even when the arcade was launched with
            # --serializer json for the platform layer. Accept that text frame
            # here so server-mode demos still show other players instead of
            # silently dropping updates.
            if '|' in data and not data.lstrip().startswith('{'):
                return self._deserialize_text(data)
            if self.serializer == 'text':
                return self._deserialize_text(data)
            elif self.serializer == 'json':
                return self._deserialize_json(data)
            elif self.serializer == 'binary':
                return self._deserialize_binary(data)
        except Exception as e:
            print(f"[ERROR] Deserialization error ({self.serializer} format): {e}")
            print(f"[ERROR] Data received: '{data[:100]}...'")
            print(f"[ERROR] This usually means server and client are using different serializers!")
            print(f"[ERROR] Server might be using a different format than '{self.serializer}'")
            return None
    
    def _deserialize_text(self, data):
        """Deserialize TEXT format: "id|name|x|y|socket|character_type|status" """
        parts = data.split('|')
        if len(parts) >= 5:
            try:
                result = {
                    'id': int(parts[0]),
                    'name': parts[1],
                    'x': float(parts[2]),
                    'y': float(parts[3])
                }
                # Add character_type and status if present
                if len(parts) >= 7:
                    result['character_type'] = parts[5]
                    result['status'] = parts[6]
                else:
                    result['character_type'] = ''
                    result['status'] = 'down'
                return result
            except (ValueError, IndexError) as e:
                print(f"Error parsing text data '{data}': {e}")
                return None
        return None
    
    def _deserialize_json(self, data):
        """Deserialize JSON format: {"id":1,"name":"Alice",...}"""
        player = json.loads(data)
        return {
            'id': player['id'],
            'name': player['name'],
            'x': player['x'],
            'y': player['y'],
            'character_type': player.get('character_type', ''),
            'status': player.get('status', 'down')
        }
    
    def _deserialize_binary(self, data):
        """Deserialize BINARY format: base64-encoded 88-byte struct"""
        import base64
        
        try:
            # Decode base64 to get raw bytes
            raw_bytes = base64.b64decode(data)
            
            # Struct format: int(4) + char[32] + float(4) + float(4) + int(4) + char[16] + char[8] + padding(16) = 88 bytes
            if len(raw_bytes) < 88:
                return None
            
            # Unpack: i = int, 32s = 32-byte string, f = float, f = float, i = int, 16s = 16-byte string, 8s = 8-byte string, 16x = 16 bytes padding
            unpacked = struct.unpack('i32sff i16s8s16x', raw_bytes[:88])
            
            player_id = unpacked[0]
            name = unpacked[1].decode('utf-8').rstrip('\x00')  # Remove null terminator
            x = unpacked[2]
            y = unpacked[3]
            character_type = unpacked[5].decode('utf-8').rstrip('\x00')  # Remove null terminator
            status = unpacked[6].decode('utf-8').rstrip('\x00')  # Remove null terminator
            
            return {
                'id': player_id,
                'name': name,
                'x': x,
                'y': y,
                'character_type': character_type,
                'status': status
            }
        except Exception as e:
            print(f"Binary deserialization error: {e}")
            return None
    
    def send_update(self, x, y, character_type="", status="down"):
        """Send our position, character type, and status to server (uses standard UPDATE format)"""
        if self.connected and self.my_player_id is not None:
            now = time.monotonic()
            if now - self.last_send_at < self.send_interval_seconds:
                return
            self.last_send_at = now

            msg = f"UPDATE|{self.my_player_id}|{x}|{y}|{self.player_name}|{character_type}|{status}\n"
            try:
                self.sock.sendall(msg.encode('utf-8'))
                self._send_count += 1
                if self._send_count <= 5 or self._send_count % 30 == 0:
                    print(f"[NET] Sent UPDATE #{self._send_count}: x={x}, y={y}, status={status}")
            except OSError as exc:
                self.disconnect(f"Send failed: {exc}")
    
    def get_updates(self):
        """Get most recent update from queue"""
        updates = []
        while not self.update_queue.empty():
            updates.append(self.update_queue.get())
        
        if updates:
            return updates[-1]
        return None
    
    def disconnect(self, reason="Client requested disconnect"):
        """Disconnect from server and stop send/receive loops."""
        if reason:
            self.disconnect_reason = reason
        if self.connected or self.running:
            print(f"[NET] Disconnecting: {self.disconnect_reason or reason}")
        self.running = False
        self.connected = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None
