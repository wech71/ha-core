"""Support for Edimax Smart Plug."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from pyedimax.smartplug import SmartPlug
import voluptuous as vol

from homeassistant.components.sensor import HomeAssistantError
from homeassistant.components.switch import (
    PLATFORM_SCHEMA as SWITCH_PLATFORM_SCHEMA,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.const import CONF_HOST, CONF_NAME, EntityCategory
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import EdimaxConfigEntry
from .const import DEFAULT_NAME
from .coordinator import EdimaxData, EdimaxDataUpdateCoordinator
from .entity import EdimaxEntity
from .hwmocking import HardwareApiFactory

PLATFORM_SCHEMA = SWITCH_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        # vol.Optional(CONF_PASSWORD, default=DEFAULT_PASSWORD): cv.string,
        # vol.Optional(CONF_USERNAME, default=DEFAULT_USERNAME): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Find and return Edimax Smart Plugs."""
    host = config.get(CONF_HOST)
    # auth = (config.get(CONF_USERNAME), config.get(CONF_PASSWORD))
    name = config.get(CONF_NAME)

    add_entities(
        [SmartPlugSwitch(HardwareApiFactory.create_smart_plug(host), name)], True
    )


@dataclass(frozen=True, kw_only=True)
class EdimaxSwitchEntityDescription(SwitchEntityDescription):
    """Class describing Edimax switch entities."""

    has_fn: Callable[[EdimaxData], bool] = lambda _: True
    is_on_fn: Callable[[EdimaxData], bool | None]
    set_fn: Callable[[SmartPlug, bool], Awaitable[Any]]


def set_switch_state(client: SmartPlug, on: bool):
    """Set SmartPlug state to ON or OFF based on value."""
    client.state = "ON" if on else "OFF"


SWITCHES = [
    EdimaxSwitchEntityDescription(
        key="onoff",
        translation_key="onoff",
        entity_category=EntityCategory.CONFIG,
        has_fn=lambda x: x.is_on is not None,
        is_on_fn=lambda x: x.is_on if x.is_on else None,
        set_fn=set_switch_state,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EdimaxConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Edimax switches based on a config entry."""
    coordinator = entry.runtime_data

    async_add_entities(
        EdimaxSwitchEntity(
            coordinator=coordinator,
            description=description,
        )
        for description in SWITCHES
        if description.has_fn(coordinator.data)
    )


class EdimaxSwitchEntity(EdimaxEntity, SwitchEntity):
    """Representation of an Edimax switch."""

    entity_description: EdimaxSwitchEntityDescription

    def __init__(
        self,
        coordinator: EdimaxDataUpdateCoordinator,
        description: EdimaxSwitchEntityDescription,
    ) -> None:
        """Initiate Edimax switch."""
        super().__init__(coordinator)

        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.data.info.serial_number}_{description.key}"
        )

    @property
    def is_on(self) -> bool | None:
        """Return state of the switch."""
        return self.entity_description.is_on_fn(self.coordinator.data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        try:
            await self.entity_description.set_fn(self.coordinator.client, True)
        except Exception as error:
            raise HomeAssistantError(
                "An error occurred while updating the Edimax Light"
            ) from error
        finally:
            await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        try:
            await self.entity_description.set_fn(self.coordinator.client, False)
        except Exception as error:
            raise HomeAssistantError(
                "An error occurred while updating the Edimax Light"
            ) from error
        finally:
            await self.coordinator.async_refresh()


class SmartPlugSwitch(SwitchEntity):
    """Representation an Edimax Smart Plug switch."""

    smartplug: SmartPlug
    _name: str
    _state: str
    _info: dict[str, Any]
    _mac: str

    def __init__(self, smartplug, name) -> None:
        """Initialize the switch."""
        self.smartplug = smartplug
        self._name = name
        # self._state = None
        # self._info = None
        # self._mac = None

    @property
    def unique_id(self) -> str:
        """Return the device's MAC address."""
        return str(self._mac)

    @property
    def name(self) -> str:
        """Return the name of the Smart Plug, if any."""
        return self._name

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self._state in ("ON", "OFF")

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self.smartplug.state = "ON"

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self.smartplug.state = "OFF"

    def set_on(self, on: bool):
        """Set state to on or off."""
        if on:
            self.turn_on()
        else:
            self.turn_off()

    def update(self) -> None:
        """Update edimax switch."""
        if not self._info:
            self._info = self.smartplug.info
            self._mac = self._info["mac"]

        self._state = self.smartplug.state == "ON"
