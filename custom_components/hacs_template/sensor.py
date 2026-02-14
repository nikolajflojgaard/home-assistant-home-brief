"""Sensor platform for HACS Template."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME, DEFAULT_NAME, DOMAIN
from .coordinator import HacsTemplateCoordinator
from .entity import device_info_from_entry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HacsTemplateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([CounterSensor(entry, coordinator)])


class CounterSensor(CoordinatorEntity[HacsTemplateCoordinator], SensorEntity):
    """Example sensor exposing a stored counter."""

    _attr_has_entity_name = True
    _attr_name = "Counter"
    _attr_icon = "mdi:counter"
    _attr_translation_key = "counter"

    def __init__(self, entry: ConfigEntry, coordinator: HacsTemplateCoordinator) -> None:
        super().__init__(coordinator)
        name = entry.options.get(CONF_NAME, entry.data.get(CONF_NAME, DEFAULT_NAME))
        self._attr_unique_id = f"{entry.entry_id}_counter"
        self._attr_extra_state_attributes = {"integration_name": name, "entry_id": entry.entry_id}
        self._attr_device_info = device_info_from_entry(entry)

    @property
    def native_value(self) -> int:
        data = self.coordinator.data
        return int(getattr(data, "counter", 0) or 0)
