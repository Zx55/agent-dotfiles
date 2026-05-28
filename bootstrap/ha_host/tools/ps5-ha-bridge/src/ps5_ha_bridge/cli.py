from __future__ import annotations

import argparse
import asyncio
import json
import logging
from dataclasses import asdict
from pathlib import Path

from .config import DEFAULT_CONFIG_PATH, AppConfig, load_config, write_example_config
from .mqtt_bridge import MqttBridge
from .playstation import PlayStationClient


def main() -> None:
    args = _build_parser().parse_args()
    logging.basicConfig(
        level=logging.DEBUG if getattr(args, "verbose", False) else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(_run(args))


async def _run(args: argparse.Namespace) -> None:
    if args.command == "init-config":
        write_example_config(args.path, overwrite=args.force)
        print(args.path.expanduser())
        return

    config = _effective_config(args)
    client = PlayStationClient(config.bridge.credential_storage_dir)

    if args.command == "discover":
        devices = await client.discover(timeout=args.timeout)
        print(json.dumps([asdict(device) for device in devices], ensure_ascii=False, indent=2))
        return

    if args.command == "pair":
        host = _require_host(args, config)
        snapshot = await client.pair(host, args.pin, args.npsso, timeout=args.timeout)
        print(json.dumps(asdict(snapshot), ensure_ascii=False, indent=2))
        return

    if args.command == "status":
        host = _require_host(args, config)
        snapshot = await client.status(host, timeout=args.timeout)
        print(json.dumps(asdict(snapshot) if snapshot else None, ensure_ascii=False, indent=2))
        return

    if args.command == "wake":
        host = _require_host(args, config)
        snapshot = await client.wake(host, args.device_id or config.ps5.device_id)
        print(json.dumps(asdict(snapshot), ensure_ascii=False, indent=2))
        return

    if args.command == "standby":
        host = _require_host(args, config)
        snapshot = await client.standby(host, args.device_id or config.ps5.device_id)
        print(json.dumps(asdict(snapshot), ensure_ascii=False, indent=2))
        return

    if args.command == "daemon":
        await MqttBridge(config).run()
        return

    raise ValueError(f"unsupported command: {args.command}")


def _effective_config(args: argparse.Namespace) -> AppConfig:
    path = getattr(args, "config", None)
    return load_config(path)


def _require_host(args: argparse.Namespace, config: AppConfig) -> str:
    host = getattr(args, "host", None) or config.ps5.host
    if not host:
        raise SystemExit("PS5 host is required. Pass --host or set ps5.host in config.")
    return host


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS5 Home Assistant MQTT bridge")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="config YAML/JSON path")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable debug logging")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_config = subparsers.add_parser("init-config", help="write an example config file")
    init_config.add_argument("--path", type=Path, default=DEFAULT_CONFIG_PATH)
    init_config.add_argument("--force", action="store_true")

    discover = subparsers.add_parser("discover", help="scan the LAN for PlayStation devices")
    discover.add_argument("--timeout", type=float, default=5.0)

    pair_cmd = subparsers.add_parser("pair", help="pair with a PS5 and save credentials")
    _add_host_arg(pair_cmd)
    pair_cmd.add_argument("--pin", required=True, help="8-digit Remote Play link-device PIN")
    pair_cmd.add_argument("--npsso", required=True, help="PSN NPSSO token")
    pair_cmd.add_argument("--timeout", type=float, default=30.0)

    status = subparsers.add_parser("status", help="read current PS5 status")
    _add_host_arg(status)
    status.add_argument("--timeout", type=float, default=5.0)

    wake_cmd = subparsers.add_parser("wake", help="wake PS5 from rest mode")
    _add_host_arg(wake_cmd)
    _add_device_arg(wake_cmd)

    standby_cmd = subparsers.add_parser("standby", help="put PS5 into rest mode")
    _add_host_arg(standby_cmd)
    _add_device_arg(standby_cmd)

    subparsers.add_parser("daemon", help="run the Home Assistant MQTT bridge")
    return parser


def _add_host_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", help="PS5 IPv4 address")


def _add_device_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--device-id", help="paired playdirector device id")
