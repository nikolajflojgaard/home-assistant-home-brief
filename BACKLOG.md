# Backlog

This repo needs an explicit iteration trail. Here it is.

## Done in 0.3.1

- Reworked household chores handling so Home Brief now cleans, prioritizes, and summarizes chore lists instead of dumping the first few raw strings.
- Grouped waste / affald countdown sensors into one cleaner upcoming-pickups summary plus timeline metadata for frontend rendering.
- Polished the Lovelace card into a more product-like layout with a dedicated agenda area for chores + waste and a cleaner separation between upcoming items and live signals.
- Kept the discovery architecture intact while exposing the new structured chore / waste metadata through sensor attributes.

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
- Tighten visual hierarchy further for the card's default mobile width now that it carries more agenda structure.

### Intelligence

- Expand discovery toward appliance state, weather, and power-price ecosystems that use richer integration metadata instead of mostly name scoring.
- Group related insights into packs so one theme does not drown everything else out.
- Add stronger appliance heuristics from longer history instead of minute-by-minute state only.
- Add EV / charger-specific timing hints.
- Teach chore parsing about richer structured task payloads (priority / due dates / assignee) when source sensors expose them.

### Integration polish

- Add tests covering discovery fallback precedence and rescan behavior.
- Add proper frontend tests or at least fixture-driven snapshots for card rendering states.
- Improve chores parsing for more custom sensor payload shapes if users expose richer task metadata.
- Consider optional per-home priority tuning once the default heuristics settle.
