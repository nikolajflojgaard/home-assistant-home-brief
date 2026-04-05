# Backlog

This repo needs an explicit iteration trail. Here it is.

## Done in 0.4.0

- Added auto-discovered weather awareness so Home Brief can surface practical outside-condition nudges without requiring a separate weather config ritual.
- Added weather and source-attribution attributes to the summary sensor, including explicit-vs-autofilled breakdown for easier troubleshooting and trust.
- Updated the Lovelace card to show outdoor temperature plus a lightweight sources panel so users can see what Home Brief is actually reading.

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

## Rework track

Home Brief is now moving from iterative feature additions into a broader rework track. The source-of-truth doc for that is `docs/REWORK-FOUNDATION.md`.

### Foundation

- Move scheduled brief publishing fully onto the persisted `home_brief.publish_morning_brief` path.
- Normalize published morning-brief payload structure and freshness metadata.
- Keep render paths stable even when runtime generators are unavailable.

### Personalization

- Add explicit person profile storage instead of scattering `Nikolaj` assumptions through the coordinator.
- Add basic focus modes and category visibility preferences.
- Add per-person weighting for personal vs household vs ambient context.

### View-model + UI

- Move card-facing ranking/section ordering into a dedicated view-model layer.
- Rebuild the card around personal focus, household context, and controllable density.
- Tighten visual hierarchy further for the card's default mobile width once the new model is in place.

### Intelligence

- Expand discovery toward appliance state and power-price ecosystems that use richer integration metadata instead of mostly name scoring.
- Make weather hints smarter by considering forecast timing, precipitation probability, and seasonality when that metadata is exposed.
- Group related insights into packs so one theme does not drown everything else out.
- Add stronger appliance heuristics from longer history instead of minute-by-minute state only.
- Add EV / charger-specific timing hints.
- Teach chore parsing about richer structured task payloads (priority / due dates / assignee) when source sensors expose them.

### Integration polish

- Add tests covering discovery fallback precedence and rescan behavior.
- Add proper frontend tests or at least fixture-driven snapshots for card rendering states.
- Improve chores parsing for more custom sensor payload shapes if users expose richer task metadata.
- Consider optional per-home priority tuning once the default heuristics settle.
- Ship real screenshots / demo GIFs instead of placeholders.
