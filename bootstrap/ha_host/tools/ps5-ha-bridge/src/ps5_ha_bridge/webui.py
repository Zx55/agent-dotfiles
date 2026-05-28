from __future__ import annotations

import asyncio
import html
import logging
from typing import Protocol

from aiohttp import web

from .playstation import DeviceSnapshot


NPSSO_URL = "https://ca.account.sony.com/api/v1/ssocookie"
WEB_PORT = 8099
LOG = logging.getLogger(__name__)


class WebRuntime(Protocol):
    discovered_devices: list[DeviceSnapshot]
    snapshot: DeviceSnapshot | None
    pairing_mode: bool
    pairing_in_progress: bool
    message: str | None
    error: str | None
    _mqtt_task: asyncio.Task[None] | None

    async def enter_pairing_mode(self) -> None: ...

    async def pair(self, host: str, npsso: str, pin: str) -> None: ...

    async def refresh_snapshot(self) -> None: ...

    def request_snapshot_refresh(self) -> None: ...


async def run_web(runtime: WebRuntime) -> None:
    app = web.Application()
    app["runtime"] = runtime
    app.router.add_get("/", _handle_index)
    app.router.add_post("/pair", _handle_pair)
    app.router.add_post("/repair", _handle_repair)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", WEB_PORT)
    await site.start()
    await asyncio.Event().wait()


async def _handle_index(request: web.Request) -> web.Response:
    runtime: WebRuntime = request.app["runtime"]
    runtime.request_snapshot_refresh()
    return _page_response(runtime)


async def _handle_repair(request: web.Request) -> web.Response:
    runtime: WebRuntime = request.app["runtime"]
    await runtime.enter_pairing_mode()
    return _page_response(runtime)


async def _handle_pair(request: web.Request) -> web.Response:
    runtime: WebRuntime = request.app["runtime"]
    data = await request.post()
    if runtime.pairing_in_progress:
        runtime.error = "Pairing is already in progress."
        return _page_response(runtime)
    host = _optional_str(data.get("host"))
    npsso = _optional_str(data.get("npsso"))
    pin = _optional_str(data.get("pin"))
    if not host or not npsso or not pin:
        runtime.message = None
        runtime.error = "PS5, NPSSO, and PIN are required."
        runtime.pairing_mode = True
        return _page_response(runtime)
    try:
        await runtime.pair(host, npsso, pin)
    except Exception as exc:
        LOG.exception("Pairing failed.")
        runtime.message = None
        runtime.error = str(exc)
        runtime.pairing_mode = True
    return _page_response(runtime)


def _page_response(runtime: WebRuntime) -> web.Response:
    return web.Response(
        text=render_page(runtime),
        content_type="text/html",
        headers={"Cache-Control": "no-store"},
    )


def render_page(runtime: WebRuntime) -> str:
    body = _render_pair_form(runtime) if runtime.pairing_mode or runtime.snapshot is None else _render_status(runtime)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PS5 HA Bridge</title>
  <style>
    :root {{ color-scheme: light dark; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    body {{ margin: 0; padding: 28px; background: Canvas; color: CanvasText; }}
    main {{ max-width: 760px; margin: 0 auto; }}
    h1 {{ font-size: 28px; margin: 0 0 20px; }}
    h2 {{ font-size: 20px; margin-top: 28px; }}
    .panel {{ border: 1px solid color-mix(in srgb, CanvasText 18%, transparent); border-radius: 8px; padding: 20px; }}
    .row {{ display: grid; grid-template-columns: 160px 1fr; gap: 12px; padding: 8px 0; }}
    label {{ display: block; font-weight: 600; margin: 16px 0 6px; }}
    input, select {{ width: 100%; box-sizing: border-box; padding: 10px; border-radius: 6px; border: 1px solid color-mix(in srgb, CanvasText 24%, transparent); font: inherit; }}
    input:disabled, select:disabled, button:disabled {{ opacity: 0.55; cursor: wait; }}
    button, a.button {{ display: inline-block; margin-top: 16px; padding: 10px 14px; border: 0; border-radius: 6px; background: #0b84ff; color: white; font: inherit; text-decoration: none; cursor: pointer; }}
    .secondary {{ background: color-mix(in srgb, CanvasText 12%, transparent); color: CanvasText; }}
    .message {{ padding: 12px; border-radius: 6px; margin-bottom: 16px; background: color-mix(in srgb, #0b84ff 18%, transparent); }}
    .error {{ padding: 12px; border-radius: 6px; margin-bottom: 16px; background: color-mix(in srgb, #ff453a 18%, transparent); }}
    .help {{ color: color-mix(in srgb, CanvasText 70%, transparent); font-size: 14px; }}
  </style>
</head>
<body>
  <main>
    <h1>PS5 HA Bridge</h1>
    {_render_message(runtime)}
    {body}
  </main>
  <script>
    document.addEventListener("submit", (event) => {{
      const form = event.target;
      if (!(form instanceof HTMLFormElement) || form.id !== "pair-form") {{
        return;
      }}
      if (form.dataset.submitting === "true") {{
        event.preventDefault();
        return;
      }}
      form.dataset.submitting = "true";
      const button = form.querySelector('button[type="submit"]');
      if (button) {{
        button.disabled = true;
        button.textContent = "Pairing...";
      }}
      const status = document.getElementById("pair-status");
      if (status) {{
        status.hidden = false;
      }}
    }});
  </script>
</body>
</html>"""


def _render_message(runtime: WebRuntime) -> str:
    parts = []
    if runtime.message:
        parts.append(f'<div class="message">{html.escape(runtime.message)}</div>')
    if runtime.error:
        parts.append(f'<div class="error">{html.escape(runtime.error)}</div>')
    return "\n".join(parts)


def _render_status(runtime: WebRuntime) -> str:
    snapshot = runtime.snapshot
    if snapshot is None:
        return _render_pair_form(runtime)
    mqtt_state = "running"
    if runtime._mqtt_task is None:
        mqtt_state = "not started"
    elif runtime._mqtt_task.done():
        mqtt_state = "stopped"
    return f"""<section class="panel">
  <h2>Paired PS5</h2>
  <div class="row"><strong>Name</strong><span>{html.escape(snapshot.name)}</span></div>
  <div class="row"><strong>Host</strong><span>{html.escape(snapshot.ip)}</span></div>
  <div class="row"><strong>Device ID</strong><span>{html.escape(snapshot.device_id)}</span></div>
  <div class="row"><strong>Status</strong><span>{html.escape(snapshot.status)}</span></div>
  <div class="row"><strong>MQTT bridge</strong><span>{mqtt_state}</span></div>
  <form method="post" action="repair">
    <button class="secondary" type="submit">Re-pair</button>
  </form>
</section>"""


def _render_pair_form(runtime: WebRuntime) -> str:
    disabled = " disabled" if runtime.pairing_in_progress else ""
    button_text = "Pairing..." if runtime.pairing_in_progress else "Pair"
    ps5_options = _render_device_options(runtime)
    return f"""<section class="panel">
  <h2>Pair PS5</h2>
  <p class="help">Select a discovered PS5, then enter NPSSO and the current Link Device PIN.</p>
  <p><a class="button" href="{NPSSO_URL}" target="_blank" rel="noreferrer">Open this page to get NPSSO</a></p>
  <form id="pair-form" method="post" action="pair">
    <label for="host">Discovered PS5</label>
    <select id="host" name="host" required{disabled}>
      {ps5_options}
    </select>
    <label for="npsso">NPSSO</label>
    <input id="npsso" name="npsso" type="text" autocomplete="off" autocapitalize="none" spellcheck="false" required{disabled}>
    <label for="pin">Link Device PIN</label>
    <input id="pin" name="pin" type="text" inputmode="numeric" pattern="[0-9]{{8}}" autocomplete="off" required{disabled}>
    <p class="help">On PS5, open Settings &gt; System &gt; Remote Play &gt; Link Device.</p>
    <p id="pair-status" class="help" hidden>Pairing in progress. Keep this page open.</p>
    <button type="submit"{disabled}>{button_text}</button>
  </form>
</section>"""


def _render_device_options(runtime: WebRuntime) -> str:
    devices = [device for device in runtime.discovered_devices if device.device_type.upper() == "PS5"]
    if not devices:
        return '<option value="">No PS5 discovered</option>'
    return "\n".join(
        f'<option value="{html.escape(device.ip)}">{html.escape(device.name)} - {html.escape(device.ip)} - {html.escape(device.status)}</option>'
        for device in devices
    )


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
