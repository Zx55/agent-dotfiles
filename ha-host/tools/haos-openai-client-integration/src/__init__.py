from __future__ import annotations

from typing import Any

async def async_setup(hass: Any, config: dict[str, Any]) -> bool:
    del hass, config
    return True


async def async_setup_entry(hass: Any, entry: Any) -> bool:
    from homeassistant.const import Platform

    from .client import normalize_base_url
    from .const import CONF_BASE_URL

    normalized_base_url = normalize_base_url(entry.data.get(CONF_BASE_URL))
    if normalized_base_url != entry.data.get(CONF_BASE_URL):
        hass.config_entries.async_update_entry(
            entry,
            data={**entry.data, CONF_BASE_URL: normalized_base_url},
        )

    await hass.config_entries.async_forward_entry_setups(
        entry,
        (Platform.AI_TASK, Platform.BUTTON),
    )
    return True


async def async_unload_entry(hass: Any, entry: Any) -> bool:
    from homeassistant.const import Platform

    return await hass.config_entries.async_unload_platforms(
        entry,
        (Platform.AI_TASK, Platform.BUTTON),
    )
