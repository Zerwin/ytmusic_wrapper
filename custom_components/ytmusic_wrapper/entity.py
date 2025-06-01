"""Base entity for Youtube Music Wrapper integration."""

from __future__ import annotations

import logging
from typing import TypedDict

from ytmusic_wrapper import ytmusic_wrapper  # type: ignore[import]
from ytmusic_wrapper.api_calls import QueueInfo, SongInfo  # type: ignore[import]

from homeassistant.components.media_player import MediaPlayerState, MediaType
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN

logger = logging.getLogger(__name__)


class PlayerInfo(TypedDict):
    """A TypedDict representing information about the current player state."""

    current_song: SongInfo
    current_queue: QueueInfo
    current_volume: int


class YoutubeMusicWrapperBaseEntity(Entity):
    """Base entity for Youtube Music Wrapper."""

    _attr_has_entity_name = True
    _attr_name = None
    _unavailable_logged = False

    def __init__(self, api: ytmusic_wrapper, config_entry: ConfigEntry) -> None:
        """Initialize the entity."""
        self._api = api
        self._host = config_entry.data[CONF_HOST]
        self._port = config_entry.data[CONF_PORT]
        self._name = config_entry.data[CONF_NAME]
        self._attr_unique_id = config_entry.entry_id
        self._attr_volume_level = None
        self._attr_media_content_type = None
        self._attr_media_title = None
        self._attr_media_artist = None
        self._attr_media_image_url = None
        self._attr_shuffle = False
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=f"http://{self._host}:{self._port}/swagger",
            name=self._name,
        )

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        await self._update_media_player_state()

    async def _update_media_player_state(self) -> None:
        """Update the current app information."""
        logger.debug("Updating media player state for %s", self._name)
        is_available = await self._api.api_calls.get_status()
        if is_available:
            await self._succesful_update()
        else:
            self._failed_update()
            return

    def _failed_update(self) -> None:
        """Handle failed update."""
        self._attr_state = MediaPlayerState.OFF
        self._attr_volume_level = None
        self._attr_media_content_type = None
        self._attr_media_title = None
        self._attr_media_artist = None
        self._attr_media_image_url = None
        self._attr_available = False
        self.async_write_ha_state()
        if not self._unavailable_logged:
            logger.info("Media player %s is unavailable", self._name)

    async def _succesful_update(self) -> None:
        """Handle successful update."""
        current_song = await self._api.api_calls.get_song()
        current_queue = await self._api.api_calls.get_queue()
        current_volume = await self._api.api_calls.get_volume()
        self._attr_available = True
        self._attr_volume_level = current_volume / 100
        self._attr_media_content_type = MediaType.MUSIC
        if not current_queue["items"]:
            # No current song, set to idle state
            self._attr_state = MediaPlayerState.IDLE
            self._attr_media_content_type = None
            self._attr_media_title = None
            self._attr_media_artist = None
            self._attr_media_image_url = None
        else:
            # There is a current song, update the state
            if current_song["isPaused"]:
                self._attr_state = MediaPlayerState.PAUSED
            else:
                self._attr_state = MediaPlayerState.PLAYING
                self._attr_shuffle = await self._api.api_calls.get_shuffle()
            self._attr_media_title = current_song["title"]
            self._attr_media_artist = current_song["artist"]
            self._attr_media_image_url = current_song["imageSrc"]
        self.async_write_ha_state()
        logger.debug("Successfully updated media player state for %s", self._name)
        if self._unavailable_logged:
            logger.debug("Media Player %s is back online", self._name)
