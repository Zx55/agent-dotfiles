from __future__ import annotations

import base64

from cursor_inline_img_loader.server import handle_request, load_image


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


def test_load_image_returns_mcp_image_content(tmp_path):
    image_path = tmp_path / "pixel.png"
    image_path.write_bytes(PNG_1X1)

    result = load_image({"path": str(image_path)})

    assert "structuredContent" not in result
    assert result["content"][0]["type"] == "text"
    assert result["content"][1]["type"] == "image"
    assert result["content"][1]["mimeType"] == "image/png"
    assert base64.b64decode(result["content"][1]["data"]) == PNG_1X1


def test_tools_list_exposes_load_image():
    response = handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})

    assert response is not None
    assert response["result"]["tools"][0]["name"] == "load_image"
