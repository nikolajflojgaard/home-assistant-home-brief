"""Auto-discovery helpers for Home Brief."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State

from .const import (
    CONF_DRYER_POWER_ENTITY,
    CONF_DRYER_STATUS_ENTITY,
    CONF_HOME_POWER_ENTITY,
    CONF_HUMIDITY_ENTITY,
    CONF_LIGHTS,
    CONF_OCCUPANCY_ENTITY,
    CONF_POWER_PRICE_ENTITY,
    CONF_SOLAR_POWER_ENTITY,
    CONF_WASHER_POWER_ENTITY,
    CONF_WASHER_STATUS_ENTITY,
)

_DISCOVERY_KEYS: tuple[str, ...] = (
    CONF_WASHER_POWER_ENTITY,
    CONF_WASHER_STATUS_ENTITY,
    CONF_DRYER_POWER_ENTITY,
    CONF_DRYER_STATUS_ENTITY,
    CONF_POWER_PRICE_ENTITY,
    CONF_SOLAR_POWER_ENTITY,
    CONF_HOME_POWER_ENTITY,
    CONF_OCCUPANCY_ENTITY,
    CONF_HUMIDITY_ENTITY,
)


def _norm(text: str) -> str:
    return text.lower().replace("_", " ")


def _domain(state: State) -> str:
    return state.entity_id.split(".", 1)[0]


def _haystack(state: State) -> str:
    parts = [state.entity_id, state.name or "", str(state.attributes.get("friendly_name", ""))]
    return _norm(" ".join(parts))


def _is_available(state: State) -> bool:
    return state.state not in {STATE_UNKNOWN, STATE_UNAVAILABLE, "none", ""}


def _score_entity(
    state: State,
    *,
    domains: tuple[str, ...],
    include: tuple[str, ...],
    exclude: tuple[str, ...] = (),
    preferred_units: tuple[str, ...] = (),
    preferred_device_classes: tuple[str, ...] = (),
    preferred_state_classes: tuple[str, ...] = (),
) -> int | None:
    if _domain(state) not in domains:
        return None

    hay = _haystack(state)
    if include and not any(token in hay for token in include):
        return None
    if exclude and any(token in hay for token in exclude):
        return None

    score = 10
    if _is_available(state):
        score += 20

    entity_id = state.entity_id.lower()
    name = (state.name or "").lower()
    friendly_name = str(state.attributes.get("friendly_name", "")).lower()

    for token in include:
        token = token.lower()
        if token in entity_id:
            score += 10
        if token in name:
            score += 8
        if token in friendly_name:
            score += 5

    unit = str(state.attributes.get("unit_of_measurement", "")).lower()
    device_class = str(state.attributes.get("device_class", "")).lower()
    state_class = str(state.attributes.get("state_class", "")).lower()

    if preferred_units and unit in {value.lower() for value in preferred_units}:
        score += 12
    if preferred_device_classes and device_class in {value.lower() for value in preferred_device_classes}:
        score += 12
    if preferred_state_classes and state_class in {value.lower() for value in preferred_state_classes}:
        score += 6

    return score


def _find_best(
    states: Iterable[State],
    *,
    domains: tuple[str, ...],
    include: tuple[str, ...],
    exclude: tuple[str, ...] = (),
    preferred_units: tuple[str, ...] = (),
    preferred_device_classes: tuple[str, ...] = (),
    preferred_state_classes: tuple[str, ...] = (),
) -> str | None:
    ranked: list[tuple[int, str]] = []
    for state in states:
        score = _score_entity(
            state,
            domains=domains,
            include=include,
            exclude=exclude,
            preferred_units=preferred_units,
            preferred_device_classes=preferred_device_classes,
            preferred_state_classes=preferred_state_classes,
        )
        if score is not None:
            ranked.append((score, state.entity_id))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    return ranked[0][1] if ranked else None


def _find_lights(states: Iterable[State]) -> list[str]:
    ranked: list[tuple[int, str]] = []
    for state in states:
        if _domain(state) != "light":
            continue
        score = 0
        hay = _haystack(state)
        if _is_available(state):
            score += 10
        for token in ("kitchen", "living", "stue", "entre", "hall", "gang", "entry", "office"):
            if token in hay:
                score += 6
        if state.entity_id.startswith("light."):
            score += 3
        ranked.append((score, state.entity_id))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [entity_id for _, entity_id in ranked[:6]]


def discover_defaults(hass: HomeAssistant) -> dict[str, Any]:
    """Return best-effort defaults for common Home Brief fields."""
    states = list(hass.states.async_all())

    return {
        CONF_WASHER_POWER_ENTITY: _find_best(
            states,
            domains=("sensor",),
            include=("washer", "washing machine", "vaskemaskine"),
            exclude=("energy", "voltage", "current", "daily", "monthly"),
            preferred_units=("w", "kw"),
            preferred_device_classes=("power",),
            preferred_state_classes=("measurement",),
        ),
        CONF_WASHER_STATUS_ENTITY: _find_best(
            states,
            domains=("sensor", "binary_sensor", "select", "input_select"),
            include=("washer", "washing machine", "vaskemaskine"),
            exclude=("energy", "voltage", "current", "power"),
        ),
        CONF_DRYER_POWER_ENTITY: _find_best(
            states,
            domains=("sensor",),
            include=("dryer", "tumble dryer", "tørretumbler"),
            exclude=("energy", "voltage", "current", "daily", "monthly"),
            preferred_units=("w", "kw"),
            preferred_device_classes=("power",),
            preferred_state_classes=("measurement",),
        ),
        CONF_DRYER_STATUS_ENTITY: _find_best(
            states,
            domains=("sensor", "binary_sensor", "select", "input_select"),
            include=("dryer", "tumble dryer", "tørretumbler"),
            exclude=("energy", "voltage", "current", "power"),
        ),
        CONF_POWER_PRICE_ENTITY: _find_best(
            states,
            domains=("sensor",),
            include=("price", "tariff", "elpris", "energi data", "energy price", "spot"),
            exclude=("forecast", "tomorrow", "average"),
            preferred_device_classes=("monetary",),
            preferred_state_classes=("measurement",),
        ),
        CONF_SOLAR_POWER_ENTITY: _find_best(
            states,
            domains=("sensor",),
            include=("solar", "pv", "solax", "inverter", "produktion"),
            exclude=("yield", "energy", "today", "total", "forecast", "daily", "monthly"),
            preferred_units=("w", "kw"),
            preferred_device_classes=("power",),
            preferred_state_classes=("measurement",),
        ),
        CONF_HOME_POWER_ENTITY: _find_best(
            states,
            domains=("sensor",),
            include=("home power", "house power", "grid power", "load power", "power", "forbrug"),
            exclude=("washer", "dryer", "solar", "pv", "charger", "car", "battery", "humidity"),
            preferred_units=("w", "kw"),
            preferred_device_classes=("power",),
            preferred_state_classes=("measurement",),
        ),
        CONF_OCCUPANCY_ENTITY: _find_best(
            states,
            domains=("binary_sensor", "group", "person", "input_boolean"),
            include=("occup", "someone home", "anyone home", "presence", "home", "family"),
            exclude=("light", "charger", "power", "distance"),
        ),
        CONF_HUMIDITY_ENTITY: _find_best(
            states,
            domains=("sensor",),
            include=("humidity", "fugt"),
            preferred_units=("%",),
            preferred_device_classes=("humidity",),
            preferred_state_classes=("measurement",),
        ),
        CONF_LIGHTS: _find_lights(states),
    }


def summarize_discovery(defaults: dict[str, Any]) -> dict[str, Any]:
    """Return a small discovery summary suitable for diagnostics."""
    matched = [key for key in _DISCOVERY_KEYS if defaults.get(key)]
    return {
        "matched_count": len(matched),
        "matched_fields": matched,
        "lights_count": len(defaults.get(CONF_LIGHTS, [])),
    }
