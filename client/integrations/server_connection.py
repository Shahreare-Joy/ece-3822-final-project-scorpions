from __future__ import annotations

"""Small socket helper used by server mode.

Local mode does not need this class. In server mode it gives the arcade one
place to open a socket, send a request, receive a response, and close cleanly.
The protocol is deliberately simple: JSON mode sends newline-delimited JSON,
and text mode sends newline-delimited strings.
"""

from dataclasses import dataclass
import json
import socket
from typing import Any

from .cpp_server import ServerAvailability, normalize_serializer


@dataclass
class ServerRequestResult:
    ok: bool
    message: str
    response: Any = None


class ServerConnection:
    """Synchronous request/response socket wrapper for platform server mode."""

    def __init__(self, host: str, port: int, serializer: str = "text", timeout: float = 1.0, name: str = "Python Platform Server") -> None:
        self.host = host
        self.port = int(port)
        self.serializer = normalize_serializer(serializer)
        self.timeout = timeout
        self.name = name
        self.sock: socket.socket | None = None
        self.connected = False

    @property
    def endpoint(self) -> str:
        return f"{self.host}:{self.port}"

    def connect(self) -> bool:
        """Open the socket if possible; return False instead of raising."""

        if self.connected and self.sock is not None:
            return True
        try:
            print(f"[SERVER] Connecting to {self.name} at {self.endpoint}...")
            self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
            self.sock.settimeout(self.timeout)
        except OSError:
            print(f"[SERVER] Connection failed: {self.name} at {self.endpoint}")
            self.sock = None
            self.connected = False
            return False
        self.connected = True
        print(f"[SERVER] Connected: {self.name} at {self.endpoint}")
        return True

    def availability(self) -> ServerAvailability:
        """Probe the server and close immediately so status checks do not leak."""

        result = self.send_request({"type": "health"} if self.serializer == "json" else "HEALTH")
        ok = result.ok and (not isinstance(result.response, dict) or bool(result.response.get("ok", True)))
        return ServerAvailability(
            name=self.name,
            role="platform",
            host=self.host,
            port=self.port,
            reachable=ok,
            message=(f"{self.name} is reachable at {self.endpoint}." if ok else f"{self.name} is not reachable at {self.endpoint}. Local fallback remains available."),
            protocol="tcp",
        )

    def send_request(self, request: Any) -> ServerRequestResult:
        """Send one request and return a decoded response if the server replies."""

        if not self.connect():
            return ServerRequestResult(False, f"Could not connect to {self.name} at {self.endpoint}.")
        try:
            payload = self._encode(request)
            assert self.sock is not None
            self.sock.sendall(payload)
            if isinstance(request, dict):
                print(f"[SERVER] Sent {request.get('type', '<unknown>')} request to {self.endpoint}.")
            response = self.receive_response()
        except OSError as exc:
            self.close()
            return ServerRequestResult(False, f"Socket error talking to {self.name}: {exc}")
        finally:
            self.close()
        if response is None:
            return ServerRequestResult(False, f"No response from {self.name}.")
        return ServerRequestResult(True, "Server response received.", response=response)

    def receive_response(self) -> Any:
        """Read one newline-delimited response from the socket."""

        if self.sock is None:
            return None
        chunks: list[bytes] = []
        try:
            while True:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
                if b"\n" in chunk:
                    break
        except socket.timeout:
            return None
        except OSError:
            self.close()
            return None
        raw = b"".join(chunks).strip()
        if not raw:
            return None
        if self.serializer == "json":
            try:
                return json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                return None
        text = raw.decode("utf-8", errors="replace")
        if text.lstrip().startswith(("{", "[")):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
        return text

    def close(self) -> None:
        """Close the socket and clear connection state."""

        if self.sock is not None:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self.sock.close()
            except OSError:
                pass
        self.sock = None
        self.connected = False

    def _encode(self, request: Any) -> bytes:
        if self.serializer == "json":
            return (json.dumps(request) + "\n").encode("utf-8")
        if isinstance(request, bytes):
            return request + (b"" if request.endswith(b"\n") else b"\n")
        return (str(request) + "\n").encode("utf-8")
