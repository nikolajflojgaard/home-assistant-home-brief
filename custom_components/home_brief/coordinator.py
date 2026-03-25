"""Coordinator for Home Brief."""

from __future__ import annotations

import logging
from collections.abc import Iterable
import re
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
    CONF_WEATHER_ENTITY,
    DEFAULT_AWAY_POWER_THRESHOLD,
    DEFAULT_DRYER_DONE_THRESHOLD,
    DEFAULT_HUMIDITY_THRESHOLD,
    DEFAULT_WASHER_DONE_THRESHOLD,
)
from .discovery import (
    discover_defaults,
    effective_defaults,
    find_household_chores_entity,
    find_temperature_entity,
    find_waste_entities,
    summarize_discovery,
)
from .storage import ApplianceState, DiscoveryState, HomeBriefStore, StoredState

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
    CONF_WEATHER_ENTITY,
)

WEATHER_LABELS = {
    CONF_POWER_PRICE_ENTITY: "Power price",
    CONF_SOLAR_POWER_ENTITY: "Solar",
    CONF_HOME_POWER_ENTITY: "Home power",
    CONF_OCCUPANCY_ENTITY: "Occupancy",
    CONF_HUMIDITY_ENTITY: "Humidity",
    CONF_WEATHER_ENTITY: "Weather",
    CONF_WASHER_STATUS_ENTITY: "Washer status",
    CONF_WASHER_POWER_ENTITY: "Washer power",
    CONF_DRYER_STATUS_ENTITY: "Dryer status",
    CONF_DRYER_POWER_ENTITY: "Dryer power",
}

WEATHER_FRIENDLY_STATES = {
    "clear-night": "clear night",
    "exceptional": "rough weather",
    "fog": "fog",
    "hail": "hail",
    "lightning": "lightning",
    "lightning-rainy": "thunderstorms",
    "partlycloudy": "partly cloudy",
    "pouring": "heavy rain",
    "rainy": "rain",
    "snowy": "snow",
    "snowy-rainy": "sleet",
    "sunny": "sun",
    "windy": "wind",
    "windy-variant": "wind",
}


@dataclass(slots=True)
class BriefData:
    summary: str
    insights: list[str]
    stats: dict[str, Any]


class HomeBriefCoordinator(DataUpdateCoordinator[BriefData]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.store = HomeBriefStore(hass, entry.entry_id)
        self.discovery_defaults: dict[str, Any] = {}
        self.discovery_summary: dict[str, Any] = {}
        self.discovery_scanned_at: str = ""
        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"home_brief_{entry.entry_id}",
            update_interval=timedelta(minutes=1),
        )

    def _configured_value(self, key: str, default: Any = None) -> Any:
        return self.entry.options.get(key, self.entry.data.get(key, default))

    def _configured_payload(self) -> dict[str, Any]:
        payload = dict(self.entry.data)
        payload.update(self.entry.options)
        return payload

    def _effective_value(self, key: str, default: Any = None) -> Any:
        configured = self._configured_value(key)
        if key == CONF_LIGHTS:
            if configured:
                return list(configured)
            discovered = self.discovery_defaults.get(key)
            return list(discovered) if discovered else list(default or [])

        if configured not in (None, ""):
            return configured
        return self.discovery_defaults.get(key, default)

    async def async_refresh_discovery(self) -> dict[str, Any]:
        stored = await self.store.async_load()
        configured = self._configured_payload()
        defaults = discover_defaults(self.hass)
        summary = summarize_discovery(defaults, configured)
        scanned_at = datetime.now(UTC).isoformat()
        await self.store.async_save_state(
            StoredState(
                washer=stored.washer,
                dryer=stored.dryer,
                discovery=DiscoveryState(defaults=defaults, summary=summary, scanned_at=scanned_at),
            )
        )
        self.discovery_defaults = defaults
        self.discovery_summary = summary
        self.discovery_scanned_at = scanned_at
        return defaults

    async def async_load_discovery_state(self) -> None:
        stored = await self.store.async_load()
        self.discovery_defaults = dict(stored.discovery.defaults)
        self.discovery_summary = dict(stored.discovery.summary)
        self.discovery_scanned_at = stored.discovery.scanned_at

    def _effective_config(self) -> dict[str, Any]:
        return effective_defaults(configured=self._configured_payload(), discovered=self.discovery_defaults)

    def _configured_entities(self) -> list[str]:
        entities = [
            entity_id
            for key in CONFIGURED_ENTITY_FIELDS
            if (entity_id := self._effective_value(key))
        ]
        entities.extend(list(self._effective_value(CONF_LIGHTS, [])))
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

    def _clean_signal_name(self, value: str) -> str:
        cleaned = str(value or "").strip()
        for prefix in ("Affalddk Askeåsen 24 ", "Affald – ", "Affald-", "Waste – ", "Waste pickup "):
            cleaned = cleaned.replace(prefix, "")
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip(" -–—")

    def _bucket_waste_days(self, days: int) -> str:
        if days <= 0:
            return "today"
        if days == 1:
            return "tomorrow"
        if days == 2:
            return "soon"
        return "later"

    def _waste_pickups(self) -> list[dict[str, Any]]:
        pickups: list[dict[str, Any]] = []
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

            if days > 3:
                continue

            name = str(state.attributes.get("friendly_name") or state.name or entity_id)
            clean_name = self._clean_signal_name(name)
            pickups.append({
                "entity_id": entity_id,
                "name": clean_name or entity_id,
                "days": days,
                "bucket": self._bucket_waste_days(days),
            })

        pickups.sort(key=lambda item: (item["days"], item["name"]))
        return pickups

    def _waste_pickup_summary(self, pickups: list[dict[str, Any]]) -> tuple[int, str] | None:
        if not pickups:
            return None

        today = [item["name"] for item in pickups if item["days"] <= 0]
        tomorrow = [item["name"] for item in pickups if item["days"] == 1]
        soon = [item["name"] for item in pickups if item["days"] == 2]

        if today:
            head = ", ".join(today[:2])
            suffix = f" +{len(today) - 2} more" if len(today) > 2 else ""
            if tomorrow:
                return 95, f"Waste pickups today: {head}{suffix}. Tomorrow: {', '.join(tomorrow[:2])}."
            return 95, f"Waste pickups today: {head}{suffix}."

        if tomorrow:
            head = ", ".join(tomorrow[:2])
            suffix = f" +{len(tomorrow) - 2} more" if len(tomorrow) > 2 else ""
            if soon:
                return 86, f"Waste pickups tomorrow: {head}{suffix}. {', '.join(soon[:2])} follow in 2 days."
            return 86, f"Waste pickups tomorrow: {head}{suffix}."

        head = ", ".join(soon[:3])
        suffix = f" +{len(soon) - 3} more" if len(soon) > 3 else ""
        return 72, f"Waste pickups coming up in 2 days: {head}{suffix}."

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

    def _chore_priority(self, chore: str, index: int) -> int:
        text = chore.lower()
        score = 100 - min(index, 10)
        urgent_terms = ("overdue", "urgent", "asap", "today", "tonight", "now", "snarest", "i dag", "nu", "hurtigst")
        soon_terms = ("tomorrow", "this week", "soon", "weekend", "imorgen", "i morgen", "denne uge", "snart")
        routine_terms = ("sometime", "eventually", "later", "når", "senere")

        if any(term in text for term in urgent_terms):
            score += 40
        elif any(term in text for term in soon_terms):
            score += 18
        elif any(term in text for term in routine_terms):
            score -= 8

        if text.startswith(("!", "*")):
            score += 12
        return score

    def _household_chores(self) -> tuple[list[str], str | None, str | None]:
        entity_id = find_household_chores_entity(self.hass)
        state = self._state_obj(entity_id)
        if state is None:
            return [], entity_id, None

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
                cleaned = [self._clean_signal_name(item) for item in items]
                prioritized = sorted(
                    enumerate(cleaned),
                    key=lambda item: self._chore_priority(item[1], item[0]),
                    reverse=True,
                )
                chores = [item for _, item in prioritized if item][:5]
                if not chores:
                    return [], entity_id, None
                top_task = chores[0]
                extra_count = max(0, len(chores) - 1)
                suffix = f" +{extra_count} more" if extra_count else ""
                summary = f"Household focus: {top_task}{suffix}."
                return chores, entity_id, summary
        return [], entity_id, None

    def _weather_condition_label(self, condition: str | None) -> str:
        key = str(condition or "").strip().lower()
        return WEATHER_FRIENDLY_STATES.get(key, key.replace("-", " ") or "weather")

    def _weather_forecast(self, weather_entity: str | None) -> list[dict[str, Any]]:
        state = self._state_obj(weather_entity)
        if state is None:
            return []
        forecast = state.attributes.get("forecast")
        if not isinstance(forecast, list):
            return []
        return [item for item in forecast if isinstance(item, dict)][:6]

    def _weather_insights(self, weather_entity: str | None) -> tuple[list[tuple[int, str]], dict[str, Any]]:
        state = self._state_obj(weather_entity)
        weather_stats = {
            "weather_entity": weather_entity,
            "weather_state": None,
            "weather_temperature": None,
            "weather_apparent_temperature": None,
            "weather_humidity": None,
            "weather_wind_speed": None,
            "weather_forecast_summary": None,
        }
        if state is None:
            return [], weather_stats

        attrs = state.attributes
        condition = self._weather_condition_label(state.state)
        temperature = attrs.get("temperature")
        apparent = attrs.get("apparent_temperature")
        humidity = attrs.get("humidity")
        wind_speed = attrs.get("wind_speed")
        forecast = self._weather_forecast(weather_entity)
        scored: list[tuple[int, str]] = []

        weather_stats.update(
            {
                "weather_state": state.state,
                "weather_temperature": temperature,
                "weather_apparent_temperature": apparent,
                "weather_humidity": humidity,
                "weather_wind_speed": wind_speed,
            }
        )

        try:
            current_temp = float(apparent if apparent is not None else temperature)
        except (TypeError, ValueError):
            current_temp = None

        try:
            current_wind = float(wind_speed) if wind_speed is not None else None
        except (TypeError, ValueError):
            current_wind = None

        precip_soon = None
        hot_soon = None
        cold_soon = None
        for item in forecast:
            condition_next = str(item.get("condition") or "").lower()
            if precip_soon is None and condition_next in {"rainy", "pouring", "snowy", "snowy-rainy", "hail", "lightning-rainy"}:
                precip_soon = condition_next
            try:
                next_temp = float(item.get("temperature")) if item.get("temperature") is not None else None
            except (TypeError, ValueError):
                next_temp = None
            if hot_soon is None and next_temp is not None and next_temp >= 24:
                hot_soon = next_temp
            if cold_soon is None and next_temp is not None and next_temp <= 2:
                cold_soon = next_temp

        if current_temp is not None and current_temp <= 2:
            scored.append((84, f"It is near freezing outside ({current_temp:.0f}°C). Dress warm if you are heading out."))
        elif current_temp is not None and current_temp >= 24:
            scored.append((58, f"Warm weather outside ({current_temp:.0f}°C). Good time to air out the house if pollen is not an issue."))

        if state.state in {"rainy", "pouring", "lightning-rainy", "snowy", "snowy-rainy", "hail"}:
            scored.append((78, f"Outside weather looks rough right now ({condition})."))
        elif state.state in {"fog", "windy", "windy-variant"}:
            scored.append((54, f"Outside weather is {condition} right now."))

        if current_wind is not None and current_wind >= 10:
            scored.append((68, f"It is windy outside ({current_wind:.0f} m/s). Secure anything light before airing out rooms."))

        if precip_soon:
            forecast_text = f"Weather outlook turns to {self._weather_condition_label(precip_soon)} soon."
            weather_stats["weather_forecast_summary"] = forecast_text
            scored.append((66, forecast_text))
        elif hot_soon is not None:
            weather_stats["weather_forecast_summary"] = f"Weather outlook warms up to around {hot_soon:.0f}°C soon."
        elif cold_soon is not None:
            weather_stats["weather_forecast_summary"] = f"Weather outlook drops to around {cold_soon:.0f}°C soon."

        return scored, weather_stats

    def _source_details(self) -> dict[str, dict[str, Any]]:
        configured = self._configured_payload()
        details: dict[str, dict[str, Any]] = {}
        for key in CONFIGURED_ENTITY_FIELDS:
            entity_id = self._effective_value(key)
            if not entity_id:
                continue
            details[key] = {
                "label": WEATHER_LABELS.get(key, key),
                "entity_id": entity_id,
                "mode": "explicit" if configured.get(key) not in (None, "") else "autofilled",
            }

        lights = list(self._effective_value(CONF_LIGHTS, []))
        if lights:
            details[CONF_LIGHTS] = {
                "label": "Lights",
                "entity_ids": lights,
                "count": len(lights),
                "mode": "explicit" if configured.get(CONF_LIGHTS) else "autofilled",
            }
        return details

    def _source_summary(self, source_details: dict[str, dict[str, Any]]) -> tuple[list[str], int, int]:
        explicit = 0
        autofilled = 0
        lines: list[str] = []
        for key in sorted(source_details):
            item = source_details[key]
            mode = item.get("mode")
            if mode == "explicit":
                explicit += 1
            elif mode == "autofilled":
                autofilled += 1
            label = str(item.get("label") or key)
            if "entity_id" in item:
                lines.append(f"{label}: {item['entity_id']} ({mode})")
            else:
                lines.append(f"{label}: {item.get('count', 0)} entities ({mode})")
        return lines, explicit, autofilled

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
        if not self.discovery_defaults:
            self.discovery_defaults = dict(stored.discovery.defaults)
            self.discovery_summary = dict(stored.discovery.summary)
            self.discovery_scanned_at = stored.discovery.scanned_at

        if not self.discovery_defaults:
            await self.async_refresh_discovery()
            stored = await self.store.async_load()

        scored: list[tuple[int, str]] = []

        washer_state, washer_done_minutes = self._update_appliance_state(
            stored.washer,
            status_entity=self._effective_value(CONF_WASHER_STATUS_ENTITY),
            power_entity=self._effective_value(CONF_WASHER_POWER_ENTITY),
            threshold=float(self._configured_value(CONF_WASHER_DONE_THRESHOLD, DEFAULT_WASHER_DONE_THRESHOLD)),
        )
        dryer_state, dryer_done_minutes = self._update_appliance_state(
            stored.dryer,
            status_entity=self._effective_value(CONF_DRYER_STATUS_ENTITY),
            power_entity=self._effective_value(CONF_DRYER_POWER_ENTITY),
            threshold=float(self._configured_value(CONF_DRYER_DONE_THRESHOLD, DEFAULT_DRYER_DONE_THRESHOLD)),
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

        price = self._float_state(self._effective_value(CONF_POWER_PRICE_ENTITY))
        if price is not None:
            if price >= 3.0:
                scored.append((100, f"Power is expensive right now ({price:.2f})."))
            elif price <= 1.0:
                scored.append((65, f"Power is cheap right now ({price:.2f})."))

        solar = self._power_state_watts(self._effective_value(CONF_SOLAR_POWER_ENTITY))
        home_power = self._power_state_watts(self._effective_value(CONF_HOME_POWER_ENTITY))
        away_power_threshold = float(self._configured_value(CONF_AWAY_POWER_THRESHOLD, DEFAULT_AWAY_POWER_THRESHOLD))

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

        is_home = self._is_home(self._effective_value(CONF_OCCUPANCY_ENTITY))
        on_lights = sum(1 for light in list(self._effective_value(CONF_LIGHTS, [])) if (self._state(light) or "").lower() == STATE_ON)
        if is_home is False and on_lights > 0:
            scored.append((95, f"Nobody is home, but {on_lights} light{'s are' if on_lights != 1 else ' is'} still on."))

        if is_home is False and home_power is not None and home_power >= away_power_threshold:
            scored.append((92, f"Nobody is home, but the house is still pulling {home_power:.0f} W."))

        humidity = self._float_state(self._effective_value(CONF_HUMIDITY_ENTITY))
        if humidity is not None and humidity >= float(self._configured_value(CONF_HUMIDITY_THRESHOLD, DEFAULT_HUMIDITY_THRESHOLD)):
            scored.append((75, f"Humidity is elevated ({humidity:.0f}%)."))

        temp_scored, indoor_temperature, temperature_entity = self._temperature_insights()
        scored.extend(temp_scored)

        weather_scored, weather_stats = self._weather_insights(self._effective_value(CONF_WEATHER_ENTITY))
        scored.extend(weather_scored)

        waste_pickups = self._waste_pickups()
        waste_pickup_summary = self._waste_pickup_summary(waste_pickups)
        if waste_pickup_summary:
            scored.append(waste_pickup_summary)

        household_chores, chores_entity, chores_summary = self._household_chores()
        if chores_summary:
            scored.append((74, chores_summary))

        missing_entities = self._missing_entities()
        if missing_entities:
            scored.append((85, f"{len(missing_entities)} configured Home Brief source entit{'ies are' if len(missing_entities) != 1 else 'y is'} missing."))

        if not scored:
            scored.append((10, "House looks calm right now."))

        await self.store.async_save_state(
            StoredState(
                washer=washer_state,
                dryer=dryer_state,
                discovery=DiscoveryState(
                    defaults=self.discovery_defaults,
                    summary=self.discovery_summary,
                    scanned_at=self.discovery_scanned_at,
                ),
            )
        )

        scored.sort(key=lambda item: item[0], reverse=True)
        deduped: list[str] = []
        seen: set[str] = set()
        for _, text in scored:
            if text in seen:
                continue
            seen.add(text)
            deduped.append(text)

        source_details = self._source_details()
        source_summary, explicit_source_count, autofilled_source_count = self._source_summary(source_details)
        effective_config = self._effective_config()
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
            "household_chores_summary": chores_summary,
            "waste_pickups": waste_pickups,
            "waste_pickup_count": len(waste_pickups),
            "waste_pickup_summary": waste_pickup_summary[1] if waste_pickup_summary else None,
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
            "discovery_defaults": self.discovery_defaults,
            "discovery_matched_count": self.discovery_summary.get("matched_count", 0),
            "discovery_matched_fields": self.discovery_summary.get("matched_fields", []),
            "discovery_autofilled_count": self.discovery_summary.get("autofilled_count", 0),
            "discovery_autofilled_fields": self.discovery_summary.get("autofilled_fields", []),
            "discovery_lights_count": self.discovery_summary.get("lights_count", 0),
            "discovery_lights_autofilled": self.discovery_summary.get("lights_autofilled", False),
            "discovery_scanned_at": self.discovery_scanned_at,
            "effective_config": effective_config,
            "source_details": source_details,
            "source_summary": source_summary,
            "source_explicit_count": explicit_source_count,
            "source_autofilled_count": autofilled_source_count,
            "last_build_at": datetime.now(UTC).isoformat(),
        }
        stats.update(weather_stats)
        return BriefData(summary=summary, insights=deduped, stats=stats)
