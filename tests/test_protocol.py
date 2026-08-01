"""Tests for the dependency-free Elephas protocol client."""

import asyncio
import importlib.util
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1] / "custom_components" / "elephas"
package = types.ModuleType("elephas")
package.__path__ = [str(ROOT)]
sys.modules["elephas"] = package
for module_name in ("const", "protocol"):
    spec = importlib.util.spec_from_file_location(
        f"elephas.{module_name}", ROOT / f"{module_name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

protocol = sys.modules["elephas.protocol"]


class FakeSocket:
    def __init__(self, *_args):
        self.closed = False

    def setblocking(self, _value):
        pass

    def close(self):
        self.closed = True


class ProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def test_send_key_packet_sequence(self):
        sent = []
        fake_socket = FakeSocket()
        loop = asyncio.get_running_loop()
        original_sendto = loop.sock_sendto
        original_socket = protocol.socket.socket

        async def fake_sendto(sock, payload, address):
            sent.append((payload, address))

        loop.sock_sendto = fake_sendto
        protocol.socket.socket = lambda *_args: fake_socket
        try:
            await protocol.ElephasProjector("192.0.2.1").async_send_key(30)
        finally:
            loop.sock_sendto = original_sendto
            protocol.socket.socket = original_socket

        self.assertEqual(sent[0][1], ("192.0.2.1", 16750))
        self.assertIn(b'"action":20000', sent[0][0])
        self.assertEqual(sent[1], (b"KEYSSTATUS:30+1", ("192.0.2.1", 16735)))
        self.assertEqual(sent[2], (b"KEYSSTATUS:30+0", ("192.0.2.1", 16735)))
        self.assertTrue(fake_socket.closed)

    async def test_scan_returns_only_online_hosts(self):
        original = protocol.ElephasProjector.async_is_online

        async def fake_is_online(self, timeout=1.0):
            return self.host.endswith(".2")

        protocol.ElephasProjector.async_is_online = fake_is_online
        try:
            found = await protocol.async_scan_projectors(
                ["192.0.2.1", "192.0.2.2", "192.0.2.3"]
            )
        finally:
            protocol.ElephasProjector.async_is_online = original
        self.assertEqual(found, {"192.0.2.2"})


if __name__ == "__main__":
    unittest.main()
