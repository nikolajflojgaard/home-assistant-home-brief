# Backlog

This repo needs an explicit iteration trail. Here it is.

## Done in 0.3.0

- Added a persistent discovery/capabilities layer so Home Brief can separate explicit user config from best-effort auto-discovery.
- Hooked discovery refresh into integration setup and reload, which means new entity matches are picked up on initial install, reloads, and options saves.
- Added a manual `home_brief.rescan` service for force-refreshing discovery without needing a full reinstall dance.
- Exposed richer discovery metadata in diagnostics and sensor stats so fallback behavior is inspectable instead of magical.

## Next up

### UX

- Surface "auto-filled vs explicitly pinned" more clearly in the Lovelace card or more-info view instead of only in diagnostics/stats.
- Add icons / semantic markers for each insight type so dense states scan even faster.
- Ship real screenshots / demo GIFs instead of placeholders.

### Intelligence

- Expand discovery toward appliance state, weather, and power-price ecosystems that use richer integration metadata instead of mostly name scoring.
- Group related insights into packs so one theme does not drown everything else out.
- Add stronger appliance heuristics from longer history instead of minute-by-minute state only.
- Add EV / charger-specific timing hints.

### Integration polish

- Add tests covering discovery fallback precedence and rescan behavior.
- Add proper frontend tests or at least fixture-driven snapshots for card rendering states.
- Improve chores parsing for more custom sensor payload shapes if users expose richer task metadata.
- Consider optional per-home priority tuning once the default heuristics settle.
