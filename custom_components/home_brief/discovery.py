"""Auto-discovery helpers for Home Brief."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

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


def _norm(text: str) -> str:
    return text.lower().replace("_", " ")


def _domain(state: State) -> str:
    return state.entity_id.split(".", 1)[0]


def _haystack(state: State) -> str:
    parts = [state.entity_id, state.name or "", str(state.attributes.get("friendly_name", ""))]
    return _norm(" ".join(parts))


def _find_first(states: Iterable[State], *, domains: tuple[str, ...], include: tuple[str, ...], exclude: tuple[str, ...] = ()) -> str | None:
    for state in states:
        if _domain(state) not in domains:
            continue
        hay = _haystack(state)
        if include and not any(token in hay for token in include):
            continue
        if exclude and any(token in hay for token in exclude):
            continue
        return state.entity_id
    return None


def _find_lights(states: Iterable[State]) -> list[str]:
    preferred: list[str] = []
    for state in states:
        if _domain(state) != "light":
            continue
        hay = _haystack(state)
        if any(token in hay for token in ("kitchen", "living", "stue", "entre", "hall", "gang")):
            preferred.append(state.entity_id)
    return preferred[:6]


def discover_defaults(hass: HomeAssistant) -> dict[str, Any]:
    """Return best-effort defaults for common Home Brief fields."""
    states = list(hass.states.async_all())

    return {
        CONF_WASHER_POWER_ENTITY: _find_first(
            states,
            domains=("sensor",),
            include=("washer", "washing machine", "vaskemaskine"),
            exclude=("energy", "voltage", "current"),
        ),
        CONF_WASHER_STATUS_ENTITY: _find_first(
            states,
            domains=("sensor", "binary_sensor"),
            include=("washer", "washing machine", "vaskemaskine"),
        ),
        CONF_DRYER_POWER_ENTITY: _find_first(
            states,
            domains=("sensor",),
            include=("dryer", "tumble dryer", "tørretumbler"),
            exclude=("energy", "voltage", "current"),
        ),
        CONF_DRYER_STATUS_ENTITY: _find_first(
            states,
            domains=("sensor", "binary_sensor"),
            include=("dryer", "tumble dryer", "tørretumbler"),
        ),
        CONF_POWER_PRICE_ENTITY: _find_first(
            states,
            domains=("sensor",),
            include=("price", "tariff", "elpris", "energi data", "energy price"),
        ),
        CONF_SOLAR_POWER_ENTITY: _find_first(
            states,
            domains=("sensor",),
            include=("solar", "pv", "solax", "inverter"),
            exclude=("yield", "energy", "today", "total", "forecast"),
        ),
        CONF_HOME_POWER_ENTITY: _find_first(
            states,
            domains=("sensor",),
            include=("home power", "house power", "grid power", "load power", "power"),
            exclude=("washer", "dryer", "solar", "pv", "charger", "car"),
        ),
        CONF_OCCUPANCY_ENTITY: _find_first(
            states,
            domains=("binary_sensor", "group", "person", "input_boolean"),
            include=("occup", "someone home", "anyone home", "presence", "home"),
            exclude=("light", "charger", "power"),
        ),
        CONF_HUMIDITY_ENTITY: _find_first(
            states,
            domains=("sensor",),
            include=("humidity", "fugt"),
        ),
        CONF_LIGHTS: _find_lights(states),
    }
