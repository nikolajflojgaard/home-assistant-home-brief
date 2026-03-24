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
- diagnostics output for setup and troubleshooting

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
- missing configured source entities

## Installation

### HACS

1. Add this repository to HACS as a custom repository.
2. Install **Home Brief**.
3. Restart Home Assistant.
4. Add the integration from **Settings → Devices & Services**.
5. Review the prefilled entity suggestions and adjust them if needed.

### Manual

1. Copy `custom_components/home_brief` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add **Home Brief** from **Settings → Devices & Services**.

## Onboarding and discovery

Home Brief tries to prefill likely entities automatically for:

- washer power / status
- dryer power / status
- power price
- solar power
- home power
- occupancy
- humidity
- a handful of likely high-signal lights

Discovery is now score-based rather than first-match. It prefers:

- available entities over unknown/unavailable ones
- power sensors with `W` / `kW` units and `power` device class
- humidity sensors with `%` and `humidity` device class
- names that actually look like washer, dryer, solar, occupancy, or price signals

Power sensors discovered in either `W` or `kW` are normalized internally before Home Brief evaluates thresholds or surplus logic.

That means setup is still best-effort, but much less random.

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
- `missing_entity_count`
- `missing_entities`
- `last_build_at`

## Lovelace card

```yaml
type: custom:home-brief-card
entity: sensor.home_brief_summary
max_items: 5
show_chips: true
show_secondary: true
```

Card behavior:

- opens more-info on click
- highlights warnings when configured source entities are missing
- shows compact chips for price / solar / home load / humidity
- keeps the top insight visually emphasized

## Diagnostics

Home Brief supports Home Assistant diagnostics.

Use **Settings → Devices & Services → Home Brief → Download diagnostics** when reporting a bug.
Configured entity IDs are redacted. The diagnostics dump includes:

- redacted config and options
- discovery match summary
- current summary / insights / stats
- coordinator success state and last exception string

## Service and websocket API

### Service

```yaml
service: home_brief.get_brief
data:
  entry_id: YOUR_ENTRY_ID
response_variable: brief
```

### Websocket commands

- `home_brief/list_entries`
- `home_brief/get_brief`

## Screenshots

Screenshot and demo placeholders live in `docs/screenshots/`.

Suggested assets for the next polish pass:

- `setup-flow.png`
- `lovelace-card-light.png`
- `lovelace-card-dark.png`
- `diagnostics-example.png`

## Development

```bash
./scripts/validate.sh
```

If Docker is installed, validation also runs `hassfest`.

## Design direction

Home Brief should feel like:

- simple
- clear
- useful in under 30 seconds
- opinionated, not over-configured
- more "house assistant" than dashboard builder

## Roadmap

Short-term:

- screenshots / demo GIFs
- notification packs
- EV-specific insights
- stronger appliance completion heuristics based on longer state history

Potential later:

- daily brief entity
- public Now page companion
- shareable house status pages
