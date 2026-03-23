"""Sensor platform for Home Brief."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME, DEFAULT_NAME, DOMAIN
from .coordinator import HomeBriefCoordinator
from .entity import device_info_from_entry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HomeBriefCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            HomeBriefSummarySensor(entry, coordinator),
            HomeBriefInsightCountSensor(entry, coordinator),
        ]
    )


class HomeBriefBaseEntity(CoordinatorEntity[HomeBriefCoordinator], SensorEntity):
    """Base entity for Home Brief sensors."""

    def __init__(self, entry: ConfigEntry, coordinator: HomeBriefCoordinator) -> None:
        super().__init__(coordinator)
        name = entry.options.get(CONF_NAME, entry.data.get(CONF_NAME, DEFAULT_NAME))
        self._attr_extra_state_attributes = {
            "integration_name": name,
            "entry_id": entry.entry_id,
        }
        self._attr_device_info = device_info_from_entry(entry)


class HomeBriefSummarySensor(HomeBriefBaseEntity):
    """Primary human-readable summary sensor."""

    _attr_has_entity_name = True
    _attr_name = "Summary"
    _attr_icon = "mdi:text-box-outline"
    _attr_translation_key = "summary"

    def __init__(self, entry: ConfigEntry, coordinator: HomeBriefCoordinator) -> None:
        super().__init__(entry, coordinator)
        self._attr_unique_id = f"{entry.entry_id}_summary"

    @property
    def native_value(self) -> str:
        return self.coordinator.data.summary

    @property
    def extra_state_attributes(self) -> dict:
        attrs = dict(super().extra_state_attributes or {})
        attrs["insights"] = self.coordinator.data.insights
        attrs.update(self.coordinator.data.stats)
        return attrs


class HomeBriefInsightCountSensor(HomeBriefBaseEntity):
    """Count of active insights."""

    _attr_has_entity_name = True
    _attr_name = "Insight count"
    _attr_icon = "mdi:format-list-bulleted-square"
    _attr_translation_key = "insight_count"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry: ConfigEntry, coordinator: HomeBriefCoordinator) -> None:
        super().__init__(entry, coordinator)
        self._attr_unique_id = f"{entry.entry_id}_insight_count"

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data.insights)

    @property
    def extra_state_attributes(self) -> dict:
        attrs = dict(super().extra_state_attributes or {})
        attrs["insights"] = self.coordinator.data.insights
        return attrs
