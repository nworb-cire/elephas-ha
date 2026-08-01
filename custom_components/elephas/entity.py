"""Base entity for the Elephas Projector integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ElephasConfigEntry
from .const import CONF_MAC, DOMAIN
from .coordinator import ElephasCoordinator


class ElephasEntity(CoordinatorEntity[ElephasCoordinator]):
    """Base class shared by Elephas entities."""

    _attr_has_entity_name = True

    def __init__(self, entry: ElephasConfigEntry) -> None:
        super().__init__(entry.runtime_data.coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
            manufacturer="Elephas",
            model="Network Projector",
            name=entry.title,
            connections=(
                {(CONNECTION_NETWORK_MAC, entry.data[CONF_MAC])}
                if entry.data.get(CONF_MAC)
                else set()
            ),
        )
