"""Button platform for Elephas projectors."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ElephasConfigEntry
from .const import KEY_HOME, KEY_MENU, KEY_SLEEP, KEY_SOURCE
from .entity import ElephasEntity


@dataclass(frozen=True, kw_only=True)
class ElephasButtonDescription(ButtonEntityDescription):
    key_code: int


BUTTONS = (
    ElephasButtonDescription(key="sleep", translation_key="sleep", key_code=KEY_SLEEP),
    ElephasButtonDescription(key="home", translation_key="home", key_code=KEY_HOME),
    ElephasButtonDescription(key="menu", translation_key="menu", key_code=KEY_MENU),
    ElephasButtonDescription(
        key="source", translation_key="source", key_code=KEY_SOURCE
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ElephasConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities(ElephasButton(entry, description) for description in BUTTONS)


class ElephasButton(ElephasEntity, ButtonEntity):
    entity_description: ElephasButtonDescription

    def __init__(
        self, entry: ElephasConfigEntry, description: ElephasButtonDescription
    ) -> None:
        super().__init__(entry)
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"

    async def async_press(self) -> None:
        await self._entry.runtime_data.client.async_send_key(
            self.entity_description.key_code
        )
