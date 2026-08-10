#!/usr/bin/env python3
"""Shared run-directory and manifest helpers."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


SCHEMA_VERSION = 1
MARKER_NAME = ".bilibili-video-summary-run"
MANIFEST_NAME = "manifest.json"


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _refuse_broad_path(path: Path) -> None:
    broad_paths = {Path("/").resolve(), Path.home().resolve()}
    if path in broad_paths:
        raise SystemExit(f"Refusing unsafe run directory: {path}")


def ensure_run_dir(path: Path, *, create: bool) -> Path:
    run_dir = path.expanduser().resolve()
    _refuse_broad_path(run_dir)
    marker = run_dir / MARKER_NAME

    if create:
        run_dir.mkdir(parents=True, exist_ok=True)
        if marker.exists() and not marker.is_file():
            raise SystemExit(f"Run marker is not a file: {marker}")
        if not marker.exists():
            existing = list(run_dir.iterdir())
            if existing:
                raise SystemExit(
                    "Refusing to claim a non-empty directory without a run marker: "
                    f"{run_dir}"
                )
            marker.write_text(
                json.dumps(
                    {
                        "run_id": str(uuid4()),
                        "created_at": utc_now(),
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
    elif not marker.is_file():
        raise SystemExit(
            f"Not a bilibili-video-summary run directory: missing {marker}"
        )

    return run_dir


def load_manifest(run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / MANIFEST_NAME
    if not manifest_path.exists():
        return {
            "schema_version": SCHEMA_VERSION,
            "run_dir": str(run_dir),
            "source": {},
            "artifacts": {},
            "stages": {},
            "created_at": utc_now(),
        }

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("schema_version") != SCHEMA_VERSION:
        raise SystemExit(
            f"Unsupported manifest schema: {data.get('schema_version')}"
        )
    if Path(data.get("run_dir", "")).resolve() != run_dir:
        raise SystemExit("Manifest run_dir does not match the requested run directory.")
    return data


def save_manifest(run_dir: Path, data: dict[str, Any]) -> None:
    data["updated_at"] = utc_now()
    manifest_path = run_dir / MANIFEST_NAME
    temp_path = run_dir / f".{MANIFEST_NAME}.tmp"
    temp_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(manifest_path)


def relative_artifact_path(run_dir: Path, path: Path) -> str:
    resolved = path.expanduser().resolve()
    try:
        return str(resolved.relative_to(run_dir))
    except ValueError as exc:
        raise SystemExit(f"Artifact must be inside the run directory: {resolved}") from exc


def record_artifact(
    manifest: dict[str, Any],
    *,
    run_dir: Path,
    name: str,
    path: Path,
    kind: str,
    ephemeral: bool,
    details: dict[str, Any] | None = None,
) -> None:
    artifact: dict[str, Any] = {
        "path": relative_artifact_path(run_dir, path),
        "kind": kind,
        "ephemeral": ephemeral,
        "status": "ready",
    }
    if details:
        artifact.update(details)
    manifest.setdefault("artifacts", {})[name] = artifact


def resolve_artifact_path(
    run_dir: Path,
    manifest: dict[str, Any],
    name: str,
    *,
    require_ready: bool = True,
) -> Path:
    artifact = manifest.get("artifacts", {}).get(name)
    if not artifact:
        raise SystemExit(f"Missing manifest artifact: {name}")
    if require_ready and artifact.get("status") != "ready":
        raise SystemExit(f"Artifact is not ready: {name}")

    relative = Path(artifact["path"])
    if relative.is_absolute():
        raise SystemExit(f"Artifact path must be relative: {relative}")
    resolved = (run_dir / relative).resolve()
    try:
        resolved.relative_to(run_dir)
    except ValueError as exc:
        raise SystemExit(f"Artifact escapes the run directory: {relative}") from exc
    return resolved


def require_command(name: str) -> str:
    command = shutil.which(name)
    if not command:
        raise SystemExit(f"Missing required command: {name}")
    return command


def yt_dlp_command() -> list[str]:
    direct = shutil.which("yt-dlp")
    if direct:
        return [direct]

    uvx = shutil.which("uvx")
    if uvx:
        return [uvx, "--from", "yt-dlp", "yt-dlp"]

    raise SystemExit(
        "Missing yt-dlp. Install it or install uv so the script can use "
        "`uvx --from yt-dlp yt-dlp`."
    )


def mlx_whisper_command() -> list[str]:
    global_tool = Path.home() / ".local" / "bin" / "mlx_whisper"
    if global_tool.is_file():
        return [str(global_tool)]

    direct = shutil.which("mlx_whisper")
    if direct:
        return [direct]

    raise SystemExit(
        "Missing MLX Whisper. Install the global tool with "
        "`uv tool install mlx-whisper`."
    )
