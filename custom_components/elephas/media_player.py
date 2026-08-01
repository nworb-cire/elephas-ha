"""Media player platform for Elephas projectors."""

from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ElephasConfigEntry
from .const import KEY_MUTE, KEY_POWER, KEY_POWER_OFF, KEY_VOLUME_DOWN, KEY_VOLUME_UP
from .entity import ElephasEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ElephasConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ElephasMediaPlayer(entry)])


class ElephasMediaPlayer(ElephasEntity, MediaPlayerEntity):
    """Represent an Elephas projector."""

    _attr_name = None
    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
    )

    def __init__(self, entry: ElephasConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = entry.unique_id
        self._attr_is_volume_muted = False

    @property
    def state(self) -> MediaPlayerState:
        return MediaPlayerState.ON if self.coordinator.data else MediaPlayerState.OFF

    @property
    def available(self) -> bool:
        """Keep controls available while the projector is asleep or off."""
        return True

    async def async_turn_on(self) -> None:
        await self._entry.runtime_data.client.async_send_key(KEY_POWER)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        await self._entry.runtime_data.client.async_send_key(KEY_POWER_OFF)
        self.coordinator.async_set_updated_data(False)

    async def async_volume_up(self) -> None:
        await self._entry.runtime_data.client.async_send_key(KEY_VOLUME_UP)

    async def async_volume_down(self) -> None:
        await self._entry.runtime_data.client.async_send_key(KEY_VOLUME_DOWN)

    async def async_mute_volume(self, mute: bool) -> None:
        if mute != self._attr_is_volume_muted:
            await self._entry.runtime_data.client.async_send_key(KEY_MUTE)
            self._attr_is_volume_muted = mute
            self.async_write_ha_state()
