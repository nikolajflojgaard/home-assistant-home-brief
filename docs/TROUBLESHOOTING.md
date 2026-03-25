# Troubleshooting

## Integration won't load

- Check Home Assistant logs for `custom_components.home_brief`.
- Confirm the folder exists at `custom_components/home_brief/`.
- Run `./scripts/validate.sh` locally before packaging or releasing.

## Config flow shows weak or wrong suggestions

Discovery is heuristic-based. It now prefers available entities and sensible units / device classes, and power sensors in either `W` or `kW` are handled correctly at runtime, but it is still best-effort.

If suggestions are wrong:

- open the integration options
- replace the guessed entities manually
- leave irrelevant fields empty instead of forcing bad matches

## Setup form refuses to submit

Home Brief requires at least one source signal or one light.

That means at least one of these should be configured:

- washer status or power
- dryer status or power
- price
- solar
- home power
- occupancy
- humidity
- lights

## Summary says configured entities are missing

At least one entity ID stored in the config no longer exists.

Typical reasons:

- entity was renamed
- device was removed
- integration providing the source entity is unavailable

Fix:

1. Open Home Brief options.
2. Re-select the missing entities.
3. Save and reload.

## Lovelace card not showing

- Make sure Home Assistant has been restarted after installation.
- Confirm the card resource auto-loaded from the integration.
- Verify the card entity points to the Home Brief summary sensor.
- Open browser dev tools if the custom card still fails.

## Diagnostics

Use **Settings → Devices & Services → Home Brief → Download diagnostics**.

The diagnostics bundle includes:

- redacted config and options
- discovery summary
- current coordinator output
- last exception string, if any

## Weather hints are missing

Home Brief only shows weather-aware insights when it can find a usable `weather.*` entity or when you explicitly pick one in options.

If weather hints are missing:

- open Home Brief options
- confirm a weather entity is suggested or select one manually
- make sure the weather entity is available and not `unavailable`
- run `home_brief.rescan` if you added weather after initial setup

## I cannot tell which sources are explicit vs auto-filled

Home Brief now exposes `source_details`, `source_summary`, `source_explicit_count`, and `source_autofilled_count` on the summary sensor.

Use those attributes or the Lovelace card sources panel to verify whether a signal is pinned by you or currently coming from discovery fallback.
