"""Asynchronous implementation of the Elephas LAN remote protocol."""

from __future__ import annotations

import asyncio
import json
import socket
import time

from .const import CONTROL_PORT, DISCOVERY_PORT, HANDSHAKE_PORT, KEY_PORT

DISCOVERY_PAYLOAD = b"control\x14"


class ElephasProjector:
    """Control one Elephas projector."""

    def __init__(self, host: str) -> None:
        self.host = host
        self._counter = 0

    def _next_message_id(self) -> str:
        self._counter += 1
        return f"{int(time.time() * 1000)}_{self._counter}"

    async def async_send_key(self, key_code: int) -> None:
        """Send a complete remote key press."""
        loop = asyncio.get_running_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        try:
            handshake = json.dumps(
                {
                    "action": 20000,
                    "appid": "1",
                    "msg_id": self._next_message_id(),
                },
                separators=(",", ":"),
            ).encode()
            await loop.sock_sendto(sock, handshake, (self.host, HANDSHAKE_PORT))
            for state in (1, 0):
                payload = f"KEYSSTATUS:{key_code}+{state}".encode()
                await loop.sock_sendto(sock, payload, (self.host, KEY_PORT))
                await asyncio.sleep(0.1)
        finally:
            sock.close()

    async def async_is_online(self, timeout: float = 1.0) -> bool:
        """Return whether the projector's control server is reachable."""
        try:
            async with asyncio.timeout(timeout):
                _reader, writer = await asyncio.open_connection(self.host, CONTROL_PORT)
                writer.close()
                await writer.wait_closed()
        except (TimeoutError, OSError):
            return False
        return True


async def async_discover_projectors(timeout: float = 2.0) -> set[str]:
    """Discover projectors using the packet sent by the official phone app."""
    loop = asyncio.get_running_loop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setblocking(False)
    found: set[str] = set()
    try:
        try:
            sock.bind(("", DISCOVERY_PORT))
        except OSError:
            sock.bind(("", 0))
        await loop.sock_sendto(
            sock, DISCOVERY_PAYLOAD, ("255.255.255.255", DISCOVERY_PORT)
        )
        deadline = loop.time() + timeout
        while (remaining := deadline - loop.time()) > 0:
            try:
                async with asyncio.timeout(remaining):
                    _payload, address = await loop.sock_recvfrom(sock, 4096)
            except TimeoutError:
                break
            if _payload != DISCOVERY_PAYLOAD and address[0] != "0.0.0.0":
                found.add(address[0])
    finally:
        sock.close()
    return found
