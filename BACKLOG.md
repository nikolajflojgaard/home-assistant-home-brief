# Backlog

This repo needs an explicit iteration trail. Here it is.

## Done in 0.2.0

- Reworked the Lovelace card so it reads like a compact briefing instead of a single giant sentence.
- Added indoor temperature chips and preferred real-world autodetection for `sensor.bad_temperatur`.
- Added Household Chores next-3 support via `sensor.household_chores_next_3_tasks` with summary attributes and card rendering.
- Exposed chores metadata (`household_chores`, count, entity) on the summary sensor.

## Next up

### UX

- Add icons / semantic markers for each insight type so dense states scan even faster.
- Add an optional "quiet mode" card setting that suppresses low-priority insights when the house is calm.
- Ship real screenshots / demo GIFs instead of placeholders.

### Intelligence

- Group related insights into packs so one theme does not drown everything else out.
- Add stronger appliance heuristics from longer history instead of minute-by-minute state only.
- Add EV / charger-specific timing hints.

### Integration polish

- Add proper frontend tests or at least fixture-driven snapshots for card rendering states.
- Improve chores parsing for more custom sensor payload shapes if users expose richer task metadata.
- Consider optional per-home priority tuning once the default heuristics settle.
