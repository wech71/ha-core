"""DataUpdateCoordinator for Elgato."""

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, SCAN_INTERVAL
from .hwmocking import HardwareApiFactory


@dataclass
class Info:
    """Info class containing serial_number."""

    serial_number: str
    product_name: str
    display_name: str
    version: str


@dataclass
class EdimaxData:
    """Edimax data stored in the DataUpdateCoordinator."""

    info: Info
    now_power: float
    now_energy_day: float
    is_on: bool


class EdimaxDataUpdateCoordinator(DataUpdateCoordinator[EdimaxData]):
    """Class to manage fetching Edimax data."""

    config_entry: ConfigEntry
    info: Info

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.config_entry = entry

        self.client = HardwareApiFactory.create_smart_plug(
            entry.data[CONF_HOST],
            # auth=(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
        )
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_{entry.data[CONF_HOST]}",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> EdimaxData:
        """Fetch data from the Edimax device."""
        try:
            self.info = Info(
                display_name="Edimax SmartPlug",
                serial_number=self.client.info["mac"],
                version=self.client.info["version"],
                product_name=self.client.info["model"],
            )

            return EdimaxData(
                info=self.info,
                now_power=self.client.now_power,
                now_energy_day=self.client.now_energy_day,
                is_on=self.client.state == "ON",
            )
        except ConnectionError as err:
            raise UpdateFailed(err) from err
