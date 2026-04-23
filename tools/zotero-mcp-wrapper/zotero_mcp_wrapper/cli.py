"""CLI entrypoint for zotero-mcp-wrapper."""

from zotero_mcp_wrapper.config import load_config
from zotero_mcp_wrapper.proxy import Proxy


def main() -> int:
    """Run the stdio proxy."""
    config = load_config()
    proxy = Proxy(config)
    return proxy.run()


if __name__ == "__main__":
    raise SystemExit(main())

