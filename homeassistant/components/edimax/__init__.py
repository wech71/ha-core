"""The edimax component."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import EdimaxDataUpdateCoordinator

PLATFORMS = [Platform.SENSOR, Platform.SWITCH]

type EdimaxConfigEntry = ConfigEntry[EdimaxDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: EdimaxConfigEntry) -> bool:
    """Set up Edimax SmartPlug from a config entry."""
    coordinator = EdimaxDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: EdimaxConfigEntry) -> bool:
    """Unload Edimax SmnartPlug config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
