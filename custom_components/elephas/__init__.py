"""Elephas Projector integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import ElephasCoordinator
from .protocol import ElephasProjector

PLATFORMS = [Platform.MEDIA_PLAYER, Platform.BUTTON]


@dataclass
class ElephasRuntimeData:
    """Runtime objects for an Elephas config entry."""

    client: ElephasProjector
    coordinator: ElephasCoordinator


type ElephasConfigEntry = ConfigEntry[ElephasRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: ElephasConfigEntry) -> bool:
    """Set up Elephas from a config entry."""
    client = ElephasProjector(entry.data["host"])
    coordinator = ElephasCoordinator(hass, client)
    await coordinator.async_refresh()
    entry.runtime_data = ElephasRuntimeData(client, coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ElephasConfigEntry) -> bool:
    """Unload an Elephas config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(hass: HomeAssistant, entry: ElephasConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
