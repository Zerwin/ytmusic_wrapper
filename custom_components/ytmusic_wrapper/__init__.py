"""The Youtube Music Wrapper integration."""

from __future__ import annotations

from asyncio import timeout

from ytmusic_wrapper import ytmusic_wrapper  # type: ignore[import]

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import Event, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER]

YoutubeMusicWrapperConfigEntry = ConfigEntry[ytmusic_wrapper]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Youtube Music Wrapper."""
    # Initialize the Youtube Music Wrapper API and store it in the entry's runtime data
    ytmusic_wrapper_api = ytmusic_wrapper(entry.data[CONF_HOST], entry.data[CONF_PORT])
    entry.runtime_data = ytmusic_wrapper_api

    # Try to connect to the Youtube Music API Server
    try:
        async with timeout(5.0):
            await ytmusic_wrapper_api.async_setup()
    except ConnectionError as exc:
        raise ConfigEntryNotReady from exc

    # On Home Assistant stop, close the API connection
    async def on_hass_stop(event: Event) -> None:
        """Stop push updates when hass stops."""
        await ytmusic_wrapper_api.async_close()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, on_hass_stop)
    )

    await ytmusic_wrapper_api.api_calls.get_status()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(ytmusic_wrapper_api.async_close)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
