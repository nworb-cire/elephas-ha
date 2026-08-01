"""State coordinator for Elephas projectors."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .protocol import ElephasProjector

_LOGGER = logging.getLogger(__name__)


class ElephasCoordinator(DataUpdateCoordinator[bool]):
    """Poll the projector's network availability."""

    def __init__(self, hass: HomeAssistant, client: ElephasProjector) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=15),
        )
        self.client = client

    async def _async_update_data(self) -> bool:
        return await self.client.async_is_online()
