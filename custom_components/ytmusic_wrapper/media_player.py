"""Media player support for Youtube Music Wrapper."""

from __future__ import annotations

from datetime import timedelta
import logging

from ytmusic_wrapper import ytmusic_wrapper  # type: ignore[import]

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import YoutubeMusicWrapperConfigEntry
from .entity import YoutubeMusicWrapperBaseEntity

logger = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=3)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: YoutubeMusicWrapperConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Youtube Music Wrapper media player entity based on a config entry."""
    api = entry.runtime_data
    async_add_entities([YoutubeMusicWrapperPlayerEntity(api, entry)])


class YoutubeMusicWrapperPlayerEntity(YoutubeMusicWrapperBaseEntity, MediaPlayerEntity):
    """Representation of a Youtube Music Wrapper media player entity."""

    _attr_app_name = "Youtube Music"
    _attr_app_icon = "mdi:youtube-music"
    _attr_media_image_remotely_accessible = True
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.CLEAR_PLAYLIST
        | MediaPlayerEntityFeature.SHUFFLE_SET
        | MediaPlayerEntityFeature.SEEK
    )

    def __init__(
        self, api: ytmusic_wrapper, entry: YoutubeMusicWrapperConfigEntry
    ) -> None:
        """Initialize the entity."""
        super().__init__(api, entry)

    async def async_update(self) -> None:
        """Update the current app information."""
        await self._update_media_player_state()

    async def _update_volume_info(self) -> None:
        """Update volume info."""
        volume_info = await self._api.api_calls.get_volume()
        self._attr_volume_level = volume_info / 100

    async def async_set_volume_level(self, volume: float) -> None:
        """Set the volume level."""
        await self._api.api_calls.set_volume(int(volume * 100))

    async def async_volume_up(self) -> None:
        """Turn volume up for media player."""
        volume = await self._api.api_calls.get_volume()
        await self._api.api_calls.set_volume(volume + 5)

    async def async_volume_down(self) -> None:
        """Turn volume up for media player."""
        volume = await self._api.api_calls.get_volume()
        await self._api.api_calls.set_volume(volume - 5)

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute or unmute the media player."""
        await self._api.api_calls.toggle_mute()

    async def async_media_play(self) -> None:
        """Send play command to media player."""
        await self._api.api_calls.play()

    async def async_media_pause(self) -> None:
        """Send pause command to media player."""
        await self._api.api_calls.pause()

    async def async_media_play_pause(self) -> None:
        """Send play/pause command to media player."""
        await self._api.api_calls.toggle_play_pause()

    async def async_media_previous_track(self) -> None:
        """Send previous track command to media player."""
        await self._api.api_calls.previous()

    async def async_media_next_track(self) -> None:
        """Send next track command to media player."""
        await self._api.api_calls.next()

    async def async_set_shuffle(self, shuffle: bool) -> None:
        """Enable/Disable shuffle mode. We can only shuffle the current playlist."""
        current_shuffle = await self._api.api_calls.get_shuffle()
        if current_shuffle != shuffle:
            await self._api.api_calls.set_shuffle()

    async def async_clear_playlist(self) -> None:
        """Clear the current playlist."""
        await self._api.api_calls.clear_queue()

    async def async_media_seek(self, position: float) -> None:
        """Clear the current playlist."""
        await self._api.api_calls.seek(position)

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        await super().async_added_to_hass()
        await self._update_volume_info()
