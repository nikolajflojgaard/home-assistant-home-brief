"""Coordinator for Home Brief."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_HOME, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_AWAY_POWER_THRESHOLD,
    CONF_DRYER_DONE_THRESHOLD,
    CONF_DRYER_POWER_ENTITY,
    CONF_DRYER_STATUS_ENTITY,
    CONF_HOME_POWER_ENTITY,
    CONF_HUMIDITY_ENTITY,
    CONF_HUMIDITY_THRESHOLD,
    CONF_LIGHTS,
    CONF_OCCUPANCY_ENTITY,
    CONF_POWER_PRICE_ENTITY,
    CONF_SOLAR_POWER_ENTITY,
    CONF_WASHER_DONE_THRESHOLD,
    CONF_WASHER_POWER_ENTITY,
    CONF_WASHER_STATUS_ENTITY,
    DEFAULT_AWAY_POWER_THRESHOLD,
    DEFAULT_DRYER_DONE_THRESHOLD,
    DEFAULT_HUMIDITY_THRESHOLD,
    DEFAULT_WASHER_DONE_THRESHOLD,
)
from .discovery import (
    discover_defaults,
    find_household_chores_entity,
    find_temperature_entity,
    find_waste_entities,
    summarize_discovery,
)
from .storage import ApplianceState, HomeBriefStore, StoredState

_LOGGER = logging.getLogger(__name__)

DONE_STATES = {"done", "completed", "complete", "finished", "idle", "clean"}
RUNNING_STATES = {"running", "on", "washing", "drying", "active"}
HOME_STATES = {STATE_HOME, STATE_ON, "true", "occupied"}
NOT_HOME_STATES = {"not_home", "away", "off", "false", "clear", "empty", "unoccupied"}
CONFIGURED_ENTITY_FIELDS: tuple[str, ...] = (
    CONF_WASHER_STATUS_ENTITY,
    CONF_WASHER_POWER_ENTITY,
    CONF_DRYER_STATUS_ENTITY,
    CONF_DRYER_POWER_ENTITY,
    CONF_POWER_PRICE_ENTITY,
    CONF_SOLAR_POWER_ENTITY,
    CONF_HOME_POWER_ENTITY,
    CONF_OCCUPANCY_ENTITY,
    CONF_HUMIDITY_ENTITY,
)


@dataclass(slots=True)
class BriefData:
    summary: str
    insights: list[str]
    stats: dict[str, Any]


class HomeBriefCoordinator(DataUpdateCoordinator[BriefData]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.store = HomeBriefStore(hass, entry.entry_id)
        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"home_brief_{entry.entry_id}",
            update_interval=timedelta(minutes=1),
        )

    def _get_option(self, key: str, default: Any = None) -> Any:
        return self.entry.options.get(key, self.entry.data.get(key, default))

    def _configured_entities(self) -> list[str]:
        entities = [
            entity_id
            for key in CONFIGURED_ENTITY_FIELDS
            if (entity_id := self._get_option(key))
        ]
        entities.extend(list(self._get_option(CONF_LIGHTS, [])))
        return entities

    def _missing_entities(self) -> list[str]:
        return [entity_id for entity_id in self._configured_entities() if self.hass.states.get(entity_id) is None]

    def _state_obj(self, entity_id: str | None):
        if not entity_id:
            return None
        return self.hass.states.get(entity_id)

    def _state(self, entity_id: str | None) -> str | None:
        state = self._state_obj(entity_id)
        if state is None:
            return None
        return state.state

    def _float_state(self, entity_id: str | None) -> float | None:
        raw = self._state(entity_id)
        if raw in (None, "unknown", "unavailable", "none", ""):
            return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    def _power_state_watts(self, entity_id: str | None) -> float | None:
        state = self._state_obj(entity_id)
        if state is None:
            return None

        raw = state.state
        if raw in (None, "unknown", "unavailable", "none", ""):
            return None

        try:
            value = float(raw)
        except (TypeError, ValueError):
            return None

        unit = str(state.attributes.get("unit_of_measurement", "")).strip().lower()
        if unit == "kw":
            return value * 1000
        if unit in {"w", ""}:
            return value
        return value

    def _status_value(self, entity_id: str | None) -> str:
        return (self._state(entity_id) or "").strip().lower()

    def _is_home(self, entity_id: str | None) -> bool | None:
        state = self._status_value(entity_id)
        if not state:
            return None
        if state in HOME_STATES:
            return True
        if state in NOT_HOME_STATES:
            return False
        return None

    def _done_minutes(self, done_at: str) -> int | None:
        if not done_at:
            return None
        try:
            dt = datetime.fromisoformat(done_at)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            return max(0, int((datetime.now(UTC) - dt).total_seconds() // 60))
        except Exception:  # noqa: BLE001
            return None

    def _waste_pickup_insights(self) -> list[tuple[int, str]]:
        scored: list[tuple[int, str]] = []
        for entity_id in find_waste_entities(self.hass):
            state = self._state_obj(entity_id)
            if state is None:
                continue
            raw = state.state
            if raw in (None, "unknown", "unavailable", "none", ""):
                continue
            try:
                days = int(float(raw))
            except (TypeError, ValueError):
                continue

            name = str(state.attributes.get("friendly_name") or state.name or entity_id)
            clean_name = name.replace("Affalddk Askeåsen 24 ", "").replace("Affald – ", "").strip()
            if days == 0:
                scored.append((94, f"Waste pickup today: {clean_name}."))
            elif days == 1:
                scored.append((88, f"Waste pickup tomorrow: {clean_name}."))
            elif days == 2:
                scored.append((72, f"Waste pickup in 2 days: {clean_name}."))
        return scored

    def _temperature_insights(self) -> tuple[list[tuple[int, str]], float | None, str | None]:
        entity_id = find_temperature_entity(self.hass)
        temperature = self._float_state(entity_id)
        scored: list[tuple[int, str]] = []
        if temperature is None:
            return scored, None, entity_id

        if temperature < 20:
            scored.append((82, f"It is getting cold inside ({temperature:.1f}°C). Might be time to turn on the furnace."))
        elif temperature > 24:
            scored.append((82, f"It is getting hot inside ({temperature:.1f}°C). Might be time to turn on the fans."))
        elif temperature < 21:
            scored.append((46, f"Indoor temperature is on the cool side ({temperature:.1f}°C)."))
        return scored, temperature, entity_id

    def _normalize_text_list(self, value: Any) -> list[str]:
        if isinstance(value, str):
            text = value.strip()
            if not text or text.lower() in {"unknown", "unavailable", "none"}:
                return []
            separators = ("\n", " • ", " · ", "|", ";")
            parts = [text]
            for separator in separators:
                if separator in text:
                    parts = [part.strip(" -•·") for part in text.split(separator)]
                    break
            return [part for part in parts if part]

        if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray, dict)):
            items: list[str] = []
            for item in value:
                text = str(item).strip(" -•·")
                if text and text.lower() not in {"unknown", "unavailable", "none"}:
                    items.append(text)
            return items

        return []

    def _household_chores(self) -> tuple[list[str], str | None]:
        entity_id = find_household_chores_entity(self.hass)
        state = self._state_obj(entity_id)
        if state is None:
            return [], entity_id

        candidates = [
            state.attributes.get("tasks"),
            state.attributes.get("items"),
            state.attributes.get("next_tasks"),
            state.attributes.get("next_3_tasks"),
            state.attributes.get("chores"),
            state.attributes.get("list"),
            state.attributes.get("entries"),
            state.state,
        ]
        for candidate in candidates:
            items = self._normalize_text_list(candidate)
            if items:
                return items[:3], entity_id
        return [], entity_id

    def _update_appliance_state(
        self,
        previous: ApplianceState,
        *,
        status_entity: str | None,
        power_entity: str | None,
        threshold: float,
    ) -> tuple[ApplianceState, int | None]:
        status = self._status_value(status_entity)
        power = self._power_state_watts(power_entity)

        running = previous.running
        done = previous.done
        done_at = previous.done_at

        explicit_running = status in RUNNING_STATES
        explicit_done = status in DONE_STATES
        power_running = power is not None and power > threshold
        power_done = power is not None and power <= threshold

        if explicit_running or power_running:
            running = True
            done = False
            done_at = ""
        elif running and (explicit_done or power_done):
            running = False
            done = True
            if not done_at:
                done_at = datetime.now(UTC).isoformat()
        elif explicit_done and not running:
            done = True
            if not done_at:
                done_at = datetime.now(UTC).isoformat()

        updated = ApplianceState(running=running, done=done, done_at=done_at, last_power=power)
        return updated, self._done_minutes(done_at)

    async def _async_update_data(self) -> BriefData:
        stored: StoredState = await self.store.async_load()
        scored: list[tuple[int, str]] = []

        washer_state, washer_done_minutes = self._update_appliance_state(
            stored.washer,
            status_entity=self._get_option(CONF_WASHER_STATUS_ENTITY),
            power_entity=self._get_option(CONF_WASHER_POWER_ENTITY),
            threshold=float(self._get_option(CONF_WASHER_DONE_THRESHOLD, DEFAULT_WASHER_DONE_THRESHOLD)),
        )
        dryer_state, dryer_done_minutes = self._update_appliance_state(
            stored.dryer,
            status_entity=self._get_option(CONF_DRYER_STATUS_ENTITY),
            power_entity=self._get_option(CONF_DRYER_POWER_ENTITY),
            threshold=float(self._get_option(CONF_DRYER_DONE_THRESHOLD, DEFAULT_DRYER_DONE_THRESHOLD)),
        )

        if washer_state.done:
            text = "Washer looks done."
            if washer_done_minutes is not None and washer_done_minutes >= 10:
                text = f"Washer has been done for {washer_done_minutes} min."
            scored.append((90 if (washer_done_minutes or 0) < 20 else 96, text))

        if dryer_state.done:
            text = "Dryer looks done."
            if dryer_done_minutes is not None and dryer_done_minutes >= 10:
                text = f"Dryer has been done for {dryer_done_minutes} min."
            scored.append((90 if (dryer_done_minutes or 0) < 20 else 96, text))

        price = self._float_state(self._get_option(CONF_POWER_PRICE_ENTITY))
        if price is not None:
            if price >= 3.0:
                scored.append((100, f"Power is expensive right now ({price:.2f})."))
            elif price <= 1.0:
                scored.append((65, f"Power is cheap right now ({price:.2f})."))

        solar = self._power_state_watts(self._get_option(CONF_SOLAR_POWER_ENTITY))
        home_power = self._power_state_watts(self._get_option(CONF_HOME_POWER_ENTITY))
        away_power_threshold = float(self._get_option(CONF_AWAY_POWER_THRESHOLD, DEFAULT_AWAY_POWER_THRESHOLD))

        if solar is not None and solar >= 1500:
            scored.append((70, f"Solar is strong right now ({solar:.0f} W). Good time to use power."))
        elif solar is not None and solar > 0:
            scored.append((35, f"Solar is producing ({solar:.0f} W)."))

        has_solar_surplus = solar is not None and home_power is not None and solar > home_power
        if has_solar_surplus:
            scored.append((80, "You appear to have solar surplus right now."))
            scored.append((72, "Good time to charge the car or run heavy appliances."))
        elif price is not None and price <= 1.0:
            scored.append((60, "Cheap power window. Good time to charge the car or run heavy loads."))

        is_home = self._is_home(self._get_option(CONF_OCCUPANCY_ENTITY))
        on_lights = sum(1 for light in list(self._get_option(CONF_LIGHTS, [])) if (self._state(light) or "").lower() == STATE_ON)
        if is_home is False and on_lights > 0:
            scored.append((95, f"Nobody is home, but {on_lights} light{'s are' if on_lights != 1 else ' is'} still on."))

        if is_home is False and home_power is not None and home_power >= away_power_threshold:
            scored.append((92, f"Nobody is home, but the house is still pulling {home_power:.0f} W."))

        humidity = self._float_state(self._get_option(CONF_HUMIDITY_ENTITY))
        if humidity is not None and humidity >= float(self._get_option(CONF_HUMIDITY_THRESHOLD, DEFAULT_HUMIDITY_THRESHOLD)):
            scored.append((75, f"Humidity is elevated ({humidity:.0f}%)."))

        temp_scored, indoor_temperature, temperature_entity = self._temperature_insights()
        scored.extend(temp_scored)
        scored.extend(self._waste_pickup_insights())

        household_chores, chores_entity = self._household_chores()
        if household_chores:
            top_task = household_chores[0]
            extra_count = max(0, len(household_chores) - 1)
            suffix = f" +{extra_count} more" if extra_count else ""
            scored.append((68, f"Household chores queued: {top_task}{suffix}."))

        missing_entities = self._missing_entities()
        if missing_entities:
            scored.append((85, f"{len(missing_entities)} configured Home Brief source entit{'ies are' if len(missing_entities) != 1 else 'y is'} missing."))

        if not scored:
            scored.append((10, "House looks calm right now."))

        await self.store.async_save_state(StoredState(washer=washer_state, dryer=dryer_state))

        scored.sort(key=lambda item: item[0], reverse=True)
        deduped: list[str] = []
        seen: set[str] = set()
        for _, text in scored:
            if text in seen:
                continue
            seen.add(text)
            deduped.append(text)

        discovery_defaults = discover_defaults(self.hass)
        discovery_summary = summarize_discovery(discovery_defaults)

        summary = deduped[0]
        stats = {
            "insight_count": len(deduped),
            "power_price": price,
            "solar_power": solar,
            "home_power": home_power,
            "humidity": humidity,
            "indoor_temperature": indoor_temperature,
            "temperature_entity": temperature_entity,
            "household_chores": household_chores,
            "household_chores_count": len(household_chores),
            "household_chores_entity": chores_entity,
            "lights_on": on_lights,
            "occupancy_home": is_home,
            "washer_power": washer_state.last_power,
            "dryer_power": dryer_state.last_power,
            "washer_running": washer_state.running,
            "washer_done": washer_state.done,
            "washer_done_minutes": washer_done_minutes,
            "dryer_running": dryer_state.running,
            "dryer_done": dryer_state.done,
            "dryer_done_minutes": dryer_done_minutes,
            "solar_surplus": has_solar_surplus,
            "configured_entities": len(self._configured_entities()),
            "missing_entities": missing_entities,
            "missing_entity_count": len(missing_entities),
            "discovery_matched_count": discovery_summary["matched_count"],
            "discovery_lights_count": discovery_summary["lights_count"],
            "last_build_at": datetime.now(UTC).isoformat(),
        }
        return BriefData(summary=summary, insights=deduped, stats=stats)
