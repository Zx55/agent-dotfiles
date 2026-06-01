from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ps5_ha_bridge.config import AppConfig, BridgeConfig, MqttConfig, Ps5Config
from ps5_ha_bridge.mqtt_bridge import MqttBridge
from ps5_ha_bridge.playstation import DeviceSnapshot


class FakePlayStationClient:
    def __init__(self, snapshot: DeviceSnapshot) -> None:
        self.snapshot = snapshot
        self.fallback_hosts: list[str | None] = []

    async def status_by_device_id(
        self,
        device_id: str,
        *,
        fallback_host: str | None = None,
        timeout: float = 8.0,
    ) -> DeviceSnapshot | None:
        del device_id, timeout
        self.fallback_hosts.append(fallback_host)
        return self.snapshot


class MqttBridgeHostPersistenceTest(unittest.IsolatedAsyncioTestCase):
    async def test_status_updates_runtime_host_and_state_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_path = root / "state.json"
            state_path.write_text(
                json.dumps(
                    {
                        "host": "192.168.71.96",
                        "device_id": "2840DD19496B",
                        "name": "PS5-685",
                        "device_type": "PS5",
                        "status": "standby",
                        "pairing_mode": False,
                    }
                ),
                encoding="utf-8",
            )
            snapshot = DeviceSnapshot(
                ip="192.168.71.67",
                name="PS5-685",
                device_id="2840DD19496B",
                device_type="PS5",
                status="standby",
                running_app_name=None,
                running_app_titleid=None,
            )
            bridge = MqttBridge(
                AppConfig(
                    ps5=Ps5Config(host="192.168.71.96", device_id="2840DD19496B"),
                    mqtt=MqttConfig(host="core-mosquitto"),
                    bridge=BridgeConfig(
                        credential_storage_dir=root / "credentials",
                        state_path=state_path,
                    ),
                )
            )
            fake_client = FakePlayStationClient(snapshot)
            bridge._ps = fake_client

            result = await bridge._status()

            self.assertEqual(result.ip, "192.168.71.67")
            self.assertEqual(bridge._ps5_host, "192.168.71.67")
            self.assertEqual(fake_client.fallback_hosts, ["192.168.71.96"])
            saved = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["host"], "192.168.71.67")
            self.assertEqual(saved["device_id"], "2840DD19496B")
            self.assertFalse(saved["pairing_mode"])


if __name__ == "__main__":
    unittest.main()
