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
- indoor temperature comfort nudges
- grouped waste / recycling reminders with timeline metadata
- prioritized household chores next-up summary
- weather-aware leave-home and ventilation hints from auto-discovered weather entities
- missing configured source entities
- recommended action layer with top action + up to 3 suggested next moves

## Installation

### HACS

1. Add this repository to HACS as a custom repository.
2. Install **Home Brief**.
3. Restart Home Assistant.
4. Add the integration from **Settings → Devices & Services**.
5. Review the prefilled entity suggestions and adjust them if needed.

On Home Assistant 2026.3 and newer, the integration ships its own `custom_components/home_brief/brand/` assets, so the icon/logo should render on the Home Assistant **Integrations** page without needing a `home-assistant/brands` PR.

Important reality check: current HACS builds still have an open gap where some store/dashboard views fetch icons from HACS metadata instead of Home Assistant's local `/api/brands/...` endpoint. That means Home Brief can show correct branding inside Home Assistant while still appearing blank inside parts of the HACS UI until HACS ships a fallback/fix.

### Manual

1. Copy `custom_components/home_brief` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add **Home Brief** from **Settings → Devices & Services**.

## Self-updating discovery

Home Brief now keeps a discovery layer separate from explicit user config.

That matters because it lets the integration keep getting smarter without being annoying:

- on initial setup, likely entities and lights are prefilled
- on integration reload, discovery is re-scanned automatically
- on options save, the reload re-scans again
- `home_brief.rescan` lets you manually force discovery at any time
- explicit user picks still win
- blank / missing fields can be auto-filled from the latest discovery snapshot

This is deliberate. A separate Home Assistant automation is not needed here. Internal lifecycle hooks plus a manual rescan service are the cleaner design: less setup, fewer moving parts, and no risk of the integration fighting user intent.

### What discovery currently targets

Discovery is score-based rather than first-match. It prefers:

- available entities over unknown/unavailable ones
- power sensors with `W` / `kW` units and `power` device class
- humidity sensors with `%` and `humidity` device class
- names that actually look like washer, dryer, solar, occupancy, or price signals
- likely high-signal lights for away-mode checks

It currently tries to find useful signals for:

- washer power / status
- dryer power / status
- power price
- solar power
- home power
- occupancy
- humidity
- weather
- lights
- indoor temperature
- waste / affald countdown sensors
- household chores sensors

Power sensors discovered in either `W` or `kW` are normalized internally before Home Brief evaluates thresholds or surplus logic.

For this real-world setup, indoor temperature discovery explicitly prefers `sensor.bad_temperatur` when it exists.
Household chores are also auto-detected with a strong preference for `sensor.household_chores_next_3_tasks`.
If the upstream Household Chores integration provides explicit task `slot` values (`am|pm`), Home Brief uses those directly for timing pressure and household contention instead of relying on heuristics.
When solar output is `0 W`, the Solar metric tile is hidden instead of showing a dead/neutral tile.

## Entities created

- `sensor.<name>_summary`
- `sensor.<name>_insight_count`

The summary sensor exposes useful attributes including:

- `insights`
- `power_price`
- `solar_power`
- `home_power`
- `humidity`
- `indoor_temperature`
- `temperature_entity`
- `household_chores`
- `household_chores_count`
- `household_chores_entity`
- `household_chores_summary`
- `nikolaj_chores`
- `nikolaj_chores_count`
- `nikolaj_chores_entity`
- `nikolaj_chores_summary`
- `household_chore_slots`
- `household_overlap_signals`
- `household_overlap_count`
- `household_slot_pressure`
- `personal_slot_load`
- `weather_entity`
- `weather_state`
- `weather_temperature`
- `weather_forecast_summary`
- `source_details`
- `source_summary`
- `source_explicit_count`
- `source_autofilled_count`
- `waste_pickups`
- `waste_pickup_count`
- `waste_pickup_summary`
- `lights_on`
- `occupancy_home`
- `washer_done_minutes`
- `dryer_done_minutes`
- `solar_surplus`
- `top_action`
- `top_action_score`
- `top_action_category`
- `top_action_reason`
- `recommended_actions`
- action metadata inside `top_action` / `recommended_actions` now includes `why_now`, `confidence`, and `time_window` when available
- `recommended_action_count`
- `missing_entity_count`
- `missing_entities`
- `discovery_matched_count`
- `discovery_matched_fields`
- `discovery_autofilled_count`
- `discovery_autofilled_fields`
- `discovery_lights_count`
- `discovery_lights_autofilled`
- `discovery_scanned_at`
- `last_build_at`

## Services

### Get current brief

```yaml
service: home_brief.get_brief
data:
  entry_id: YOUR_ENTRY_ID
response_variable: brief
```

### Force a discovery rescan

```yaml
service: home_brief.rescan
data:
  entry_id: YOUR_ENTRY_ID # optional; omit to rescan all Home Brief entries
response_variable: result
```

## Lovelace card

```yaml
type: custom:home-brief-card
entity: sensor.home_brief_summary
max_items: 6
show_chips: true
show_secondary: true
```

Card behavior:

- opens more-info on click
- highlights warnings when configured source entities are missing
- shows a dedicated **Best move now** action block when `top_action` / `recommended_actions` exist
- presents price / solar / home load / indoor temperature / outdoor temperature / humidity as cleaner metric tiles instead of loose chip clutter
- gives the top insight stronger visual priority with clearer product-style spacing and typography
- groups chores and waste pickups into a dedicated agenda column with calmer nested panels
- turns secondary states into labeled attention rows so setup issues and household nudges are easier to scan
- renders remaining insights as a cleaner signal stack so the card stays useful when the house is noisy

## Diagnostics

Home Brief supports Home Assistant diagnostics.

Use **Settings → Devices & Services → Home Brief → Download diagnostics** when reporting a bug.
Configured entity IDs are redacted. The diagnostics dump includes:

- redacted config and options
- redacted effective config after discovery fallback is applied
- discovery match summary and stored discovery snapshot
- current summary / insights / stats
- coordinator success state and last exception string

## Websocket commands

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
