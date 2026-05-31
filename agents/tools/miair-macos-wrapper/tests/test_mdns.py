"""Tests for macOS MiAir mDNS wrapper helpers."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from miair_macos_wrapper.cli import configured_hostname, export_hostname_env
from miair_macos_wrapper.mdns import (
    RaopRegistration,
    build_dns_sd_command,
    is_ipv4_address,
    preferred_ip,
)


class MdnsHelperTests(unittest.TestCase):
    def test_configured_hostname_reads_space_separated_arg(self) -> None:
        self.assertEqual(
            configured_hostname(["--conf-path", "/tmp/miair", "--hostname", "192.0.2.10"]),
            "192.0.2.10",
        )

    def test_configured_hostname_reads_equals_arg(self) -> None:
        self.assertEqual(
            configured_hostname(["--hostname=192.0.2.10"]),
            "192.0.2.10",
        )

    def test_export_hostname_env_sets_ipv4_hostname(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            export_hostname_env(["--hostname", "192.0.2.10"])
            self.assertEqual(os.environ["MIAIR_HOSTNAME"], "192.0.2.10")

    def test_is_ipv4_address(self) -> None:
        self.assertTrue(is_ipv4_address("192.0.2.10"))
        self.assertFalse(is_ipv4_address("192.0.2.10.local"))
        self.assertFalse(is_ipv4_address("not-an-ip"))
        self.assertFalse(is_ipv4_address("999.0.2.10"))

    def test_preferred_ip_uses_configured_ipv4(self) -> None:
        self.assertEqual(
            preferred_ip("192.0.2.10", lambda: "198.18.0.1"),
            "192.0.2.10",
        )

    def test_preferred_ip_falls_back_for_non_ip_hostname(self) -> None:
        self.assertEqual(
            preferred_ip("macbook.local", lambda: "192.0.2.10"),
            "192.0.2.10",
        )

    def test_dns_sd_command_contains_raop_registration(self) -> None:
        command = build_dns_sd_command(
            RaopRegistration(
                service_name="395701A989F6@小米智能音箱Pro",
                device_name="小米智能音箱Pro",
                device_id="39:57:01:A9:89:F6",
                rtsp_port=62505,
            )
        )

        self.assertEqual(command[:5], ["/usr/bin/dns-sd", "-R", "395701A989F6@小米智能音箱Pro", "_raop._tcp", "local"])
        self.assertIn("62505", command)
        self.assertIn("tp=UDP", command)
        self.assertIn("fn=小米智能音箱Pro", command)


if __name__ == "__main__":
    unittest.main()
