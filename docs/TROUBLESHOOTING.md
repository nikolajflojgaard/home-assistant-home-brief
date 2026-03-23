# Troubleshooting

## Integration won't load

- Check Home Assistant logs for `custom_components.home_brief`.
- Confirm the folder exists at `custom_components/home_brief/`.
- Run `./scripts/validate.sh` locally before packaging or releasing.

## Config flow shows weak or wrong suggestions

Discovery is heuristic-based. It now prefers available entities and sensible units / device classes, but it is still best-effort.

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
