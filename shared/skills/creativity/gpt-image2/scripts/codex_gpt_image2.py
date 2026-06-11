#!/usr/bin/env python3
"""Generate images through Codex's built-in imagegen path.

This script is meant to be called by non-Codex agents that need access to the
user's Codex image-generation capability. It drives local Codex through the
Codex Python SDK and asks Codex to use its built-in imagegen tool.

It intentionally does not call the OpenAI Images API directly and does not use
OPENAI_API_KEY.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any


DEFAULT_CODEX_IMAGEGEN_SKILL = (
    Path.home() / ".codex" / "skills" / ".system" / "imagegen" / "SKILL.md"
)

RESULT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "image_path": {"type": "string"},
        "final_prompt": {"type": "string"},
        "used_builtin_imagegen": {"type": "boolean"},
        "notes": {"type": "string"},
    },
    "required": ["image_path", "final_prompt", "used_builtin_imagegen", "notes"],
    "additionalProperties": False,
}


def die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def read_prompt(args: argparse.Namespace) -> str:
    provided = [args.prompt_arg is not None, args.prompt is not None, args.prompt_file is not None]
    if sum(provided) != 1:
        die("Provide exactly one of PROMPT, --prompt, or --prompt-file.")

    if args.prompt_file is not None:
        path = Path(args.prompt_file).expanduser()
        if not path.exists():
            die(f"Prompt file not found: {path}")
        prompt = path.read_text(encoding="utf-8").strip()
    else:
        prompt = args.prompt if args.prompt is not None else args.prompt_arg
        prompt = str(prompt).strip()

    if not prompt:
        die("Prompt cannot be empty.")
    return prompt


def resolve_cwd(raw: str) -> Path:
    cwd = Path(raw).expanduser().resolve()
    if not cwd.exists() or not cwd.is_dir():
        die(f"Working directory does not exist: {cwd}")
    return cwd


def resolve_existing_file(raw: str, *, label: str) -> Path:
    path = Path(raw).expanduser().resolve()
    if not path.exists():
        die(f"{label} not found: {path}")
    if not path.is_file():
        die(f"{label} is not a file: {path}")
    return path


def resolve_output_path(raw: str, cwd: Path) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = cwd / path
    return path.resolve()


def load_codex_sdk() -> dict[str, Any]:
    try:
        from openai_codex import (  # type: ignore[import-not-found]
            Codex,
            CodexConfig,
            LocalImageInput,
            Sandbox,
            SkillInput,
            TextInput,
        )
    except ImportError:
        die(
            "openai-codex is not installed in this Python environment. "
            "Install it in the shared agent Python with: "
            "`uv pip install --python \"$HOME/.local/share/agent-dotfiles/python/bin/python\" openai-codex`."
        )

    return {
        "Codex": Codex,
        "CodexConfig": CodexConfig,
        "LocalImageInput": LocalImageInput,
        "Sandbox": Sandbox,
        "SkillInput": SkillInput,
        "TextInput": TextInput,
    }


def sandbox_value(sdk: dict[str, Any], raw: str) -> Any:
    Sandbox = sdk["Sandbox"]
    return {
        "read-only": Sandbox.read_only,
        "workspace-write": Sandbox.workspace_write,
        "full-access": Sandbox.full_access,
    }[raw]


def build_codex_prompt(args: argparse.Namespace, prompt: str, out_path: Path) -> str:
    if args.mode == "edit":
        mode = (
            "Edit the attached image. Treat Image 1 as the edit target and any "
            "later images as references or supporting inputs."
        )
    else:
        mode = "Generate a new image."

    lines = [
        "Use Codex's built-in $imagegen / image_gen tool for this image task.",
        "Do not call the OpenAI Platform Images API directly.",
        "Do not use scripts/image_gen.py or any fallback CLI that requires OPENAI_API_KEY.",
        mode,
        f"Save the final selected image to this exact path: {out_path}",
        "If Codex saves the image under CODEX_HOME first, copy or move the selected final file to the requested path.",
        "Do not leave the deliverable only under CODEX_HOME/generated_images.",
    ]

    if args.size:
        lines.append(f"Requested size or aspect: {args.size}")
    if args.quality:
        lines.append(f"Requested quality or iteration level: {args.quality}")
    if args.style:
        lines.append(f"Style or medium: {args.style}")
    if args.composition:
        lines.append(f"Composition or framing: {args.composition}")
    if args.constraints:
        lines.append(f"Constraints: {args.constraints}")
    if args.avoid:
        lines.append(f"Avoid: {args.avoid}")
    if args.transparent:
        lines.append(
            "Transparent output requested. Follow the imagegen skill's built-in-first transparent workflow."
        )
    if args.force:
        lines.append("The caller allows overwriting the requested output path if necessary.")
    else:
        lines.append("Do not overwrite unrelated files.")

    if args.image:
        lines.append(
            f"{len(args.image)} local image(s) are attached. Refer to them as Image 1, Image 2, etc."
        )

    lines.extend(
        [
            "",
            "Image prompt:",
            prompt,
            "",
            "Return only a compact JSON object matching the provided schema.",
            "Set used_builtin_imagegen to true only if the built-in imagegen path was used.",
        ]
    )
    return "\n".join(lines)


def parse_json_object(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass

    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end <= start:
        return None

    try:
        parsed = json.loads(raw[start : end + 1])
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def build_inputs(args: argparse.Namespace, sdk: dict[str, Any], codex_prompt: str) -> Any:
    TextInput = sdk["TextInput"]
    LocalImageInput = sdk["LocalImageInput"]
    SkillInput = sdk["SkillInput"]

    inputs: list[Any] = []
    if not args.no_attach_imagegen_skill:
        skill_path = Path(args.imagegen_skill).expanduser().resolve()
        if not skill_path.exists():
            die(f"Codex imagegen skill not found: {skill_path}")
        inputs.append(SkillInput(name="imagegen", path=str(skill_path)))

    for image in args.image or []:
        inputs.append(LocalImageInput(path=str(resolve_existing_file(image, label="Image"))))

    inputs.append(TextInput(text=codex_prompt))
    return inputs if len(inputs) > 1 else codex_prompt


def result_summary(
    *,
    ok: bool,
    args: argparse.Namespace,
    out_path: Path,
    result: Any | None,
    final_payload: dict[str, Any] | None,
    error: str | None = None,
) -> dict[str, Any]:
    exists = out_path.exists()
    return {
        "ok": ok,
        "image_path": str(out_path),
        "exists": exists,
        "bytes": out_path.stat().st_size if exists else 0,
        "mode": args.mode,
        "codex_model": args.model,
        "status": str(getattr(result, "status", "")) if result is not None else None,
        "turn_id": getattr(result, "id", None) if result is not None else None,
        "duration_ms": getattr(result, "duration_ms", None) if result is not None else None,
        "codex_payload": final_payload,
        "codex_final_response": getattr(result, "final_response", None) if result is not None else None,
        "error": error,
    }


def print_summary(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return

    if payload["ok"]:
        print(f"Wrote image: {payload['image_path']}")
        if payload["bytes"]:
            print(f"Bytes: {payload['bytes']}")
        return

    print(f"Image generation did not produce the expected file: {payload['image_path']}")
    if payload.get("error"):
        print(f"Error: {payload['error']}")
    if payload.get("codex_final_response"):
        print("\nCodex final response:")
        print(payload["codex_final_response"])


def run(args: argparse.Namespace) -> int:
    cwd = resolve_cwd(args.cwd)
    prompt = read_prompt(args)
    out_path = resolve_output_path(args.out, cwd)

    if out_path.exists() and not args.force:
        die(f"Output already exists: {out_path} (use --force to overwrite).")

    codex_prompt = build_codex_prompt(args, prompt, out_path)

    if args.dry_run:
        payload = {
            "ok": True,
            "dry_run": True,
            "cwd": str(cwd),
            "image_path": str(out_path),
            "mode": args.mode,
            "codex_model": args.model,
            "sandbox": args.sandbox,
            "attached_images": [str(resolve_existing_file(p, label="Image")) for p in args.image or []],
            "imagegen_skill": None
            if args.no_attach_imagegen_skill
            else str(Path(args.imagegen_skill).expanduser()),
            "codex_prompt": codex_prompt,
            "output_schema": RESULT_SCHEMA,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sdk = load_codex_sdk()
    Codex = sdk["Codex"]
    CodexConfig = sdk["CodexConfig"]
    sandbox = sandbox_value(sdk, args.sandbox)
    codex_config = CodexConfig(codex_bin=args.codex_bin) if args.codex_bin else None
    inputs = build_inputs(args, sdk, codex_prompt)

    result = None
    try:
        with Codex(config=codex_config) as codex:
            thread = codex.thread_start(cwd=str(cwd), model=args.model, sandbox=sandbox)
            result = thread.run(inputs, output_schema=RESULT_SCHEMA, sandbox=sandbox)
    except Exception as exc:
        payload = result_summary(
            ok=False,
            args=args,
            out_path=out_path,
            result=result,
            final_payload=None,
            error=f"{exc.__class__.__name__}: {exc}",
        )
        print_summary(payload, as_json=args.json)
        return 1

    final_payload = parse_json_object(getattr(result, "final_response", None))

    if not out_path.exists() and final_payload:
        returned = final_payload.get("image_path")
        if isinstance(returned, str):
            returned_path = Path(returned).expanduser()
            if not returned_path.is_absolute():
                returned_path = cwd / returned_path
            returned_path = returned_path.resolve()
            if returned_path.exists() and returned_path != out_path:
                shutil.copy2(returned_path, out_path)

    ok = out_path.exists() and out_path.stat().st_size > 0
    payload = result_summary(
        ok=ok,
        args=args,
        out_path=out_path,
        result=result,
        final_payload=final_payload,
        error=None if ok else "Expected output file was not created or is empty.",
    )
    print_summary(payload, as_json=args.json)
    return 0 if ok else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate or edit an image through Codex's built-in imagegen tool."
    )
    parser.add_argument("prompt_arg", nargs="?", metavar="PROMPT")
    parser.add_argument("--prompt", help="Image prompt text.")
    parser.add_argument("--prompt-file", help="Read image prompt from a UTF-8 text file.")
    parser.add_argument("--out", required=True, help="Final image path to create.")
    parser.add_argument("--cwd", default=".", help="Workspace root for the Codex run.")
    parser.add_argument("--mode", choices=["generate", "edit"], default="generate")
    parser.add_argument("--image", action="append", help="Attach a local image. Repeat as needed.")
    parser.add_argument("--size", help="Requested size or aspect, for example 1024x1024 or 16:9.")
    parser.add_argument("--quality", choices=["low", "medium", "high", "auto"])
    parser.add_argument("--style", help="Style or medium guidance.")
    parser.add_argument("--composition", help="Composition or framing guidance.")
    parser.add_argument("--constraints", help="Must-keep requirements.")
    parser.add_argument("--avoid", help="Negative constraints.")
    parser.add_argument("--transparent", action="store_true", help="Request transparent output.")
    parser.add_argument("--force", action="store_true", help="Allow overwriting --out.")
    parser.add_argument("--model", help="Codex model to use. Defaults to Codex config.")
    parser.add_argument(
        "--sandbox",
        choices=["read-only", "workspace-write", "full-access"],
        default="workspace-write",
        help="Codex sandbox preset.",
    )
    parser.add_argument("--codex-bin", help="Optional Codex binary path for the SDK runtime.")
    parser.add_argument(
        "--imagegen-skill",
        default=str(DEFAULT_CODEX_IMAGEGEN_SKILL),
        help="Path to Codex's imagegen SKILL.md.",
    )
    parser.add_argument(
        "--no-attach-imagegen-skill",
        action="store_true",
        help="Do not attach Codex's imagegen skill explicitly.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the planned Codex prompt only.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable status JSON.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.mode == "edit" and not args.image:
        parser.error("--mode edit requires at least one --image.")
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
