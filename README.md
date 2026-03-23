# Home Brief

Home Brief is a Home Assistant custom integration that turns a handful of entity states into a plain-English house summary.

Instead of staring at dashboards, you get a short brief like:

- "Power is expensive right now"
- "Washer has been done for 18 min"
- "You appear to have solar surplus right now"
- "Good time to charge the car or run heavy appliances"
- "Nobody is home, but 3 lights are still on"
- "House looks calm right now"

## What it does

Home Brief watches a small set of entities and creates:

- a human-readable summary sensor
- an insight count sensor
- a Lovelace card
- a response service / websocket endpoint for the current brief

It is intentionally opinionated. The goal is useful signal, not another bloated dashboard.

## Current insight packs

- washer done / washer stale
- dryer done / dryer stale
- expensive power now
- cheap power now
- solar strong now
- solar surplus now
- good time to charge EV or run heavy loads
- nobody-home + lights-left-on
- nobody-home + unusual house power draw
- humidity warning

## Installation

1. Add this repository to HACS as a custom repository.
2. Install **Home Brief**.
3. Restart Home Assistant.
4. Add the integration from **Settings → Devices & Services**.
5. Review the prefilled entity suggestions and adjust them if needed.

## Auto-discovery

Home Brief will try to prefill likely entities automatically for:

- washer power / status
- dryer power / status
- power price
- solar power
- home power
- occupancy
- humidity
- a handful of likely lights

This is best-effort only. It is meant to reduce setup friction, not pretend every home is the same.

## Entities created

- `sensor.<name>_summary`
- `sensor.<name>_insight_count`

The summary sensor exposes useful attributes including:

- `insights`
- `power_price`
- `solar_power`
- `home_power`
- `humidity`
- `lights_on`
- `occupancy_home`
- `washer_done_minutes`
- `dryer_done_minutes`
- `solar_surplus`

## Lovelace card

```yaml
type: custom:home-brief-card
entity: sensor.home_brief_summary
max_items: 5
```

## Design direction

Home Brief should feel like:

- simple
- clear
- useful in under 30 seconds
- opinionated, not over-configured
- more "house assistant" than dashboard builder

## Roadmap

Short-term:

- better auto-discovery heuristics
- better appliance state handling
- screenshots / demo GIFs
- notification packs
- EV-specific insights

Potential later:

- daily brief entity
- public Now page companion
- shareable house status pages
