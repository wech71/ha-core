"""Support for Edimax sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EdimaxConfigEntry
from .coordinator import EdimaxData, EdimaxDataUpdateCoordinator
from .entity import EdimaxEntity


@dataclass(frozen=True, kw_only=True)
class EdimaxSensorEntityDescription(SensorEntityDescription):
    """Class describing Edimax sensor entities."""

    has_fn: Callable[[EdimaxData], bool] = lambda _: True
    value_fn: Callable[[EdimaxData], float | int | None]


SENSORS = [
    EdimaxSensorEntityDescription(
        key="current_power",
        translation_key="current_power",
        entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
        has_fn=lambda x: x.now_power is not None,
        value_fn=lambda x: x.now_power if x.now_power else None,
    ),
    EdimaxSensorEntityDescription(
        key="total_power",
        translation_key="total_power",
        entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.ENERGY,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        has_fn=lambda x: x.now_energy_day is not None,
        value_fn=lambda x: x.now_energy_day if x.now_energy_day else None,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EdimaxConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Edimax sensor based on a config entry."""
    coordinator = entry.runtime_data

    async_add_entities(
        EdimaxSensorEntity(
            coordinator=coordinator,
            description=description,
        )
        for description in SENSORS
        if description.has_fn(coordinator.data)
    )


class EdimaxSensorEntity(EdimaxEntity, SensorEntity):
    """Representation of a Edimax sensor."""

    entity_description: EdimaxSensorEntityDescription

    def __init__(
        self,
        coordinator: EdimaxDataUpdateCoordinator,
        description: EdimaxSensorEntityDescription,
    ) -> None:
        """Initiate Edimax sensor."""
        super().__init__(coordinator)

        self.entity_description = description
        self._attr_unique_id = f"{coordinator.info.serial_number}_{description.key}"

    @property
    def native_value(self) -> float | int | None:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)
