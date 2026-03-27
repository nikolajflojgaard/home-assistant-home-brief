# Changelog

All notable changes to this project will be documented in this file.

## 0.4.2

- Added packaged `custom_components/home_brief/brand/` assets so Home Assistant 2026.3+ can resolve the integration icon/logo from the local brands API.
- Kept existing root/HACS branding assets intact while fixing the in-product integration branding path.

## 0.4.1

- Fixed whole-home power discovery so auto-filled home load prefers credible whole-home/grid consumption sensors instead of latching onto generic power entities.
- Suppressed bogus `Home 0 W` presentation by treating zero/negative home load as non-meaningful for surplus logic and Lovelace chip rendering.
- Reworked household chores parsing/rendering to consume structured task objects and present clean title/date/assignee rows instead of raw JSON blobs.

## 0.4.0

- Added auto-discovered weather support so Home Brief can surface practical outside-condition and near-term forecast nudges without extra setup in typical Home Assistant installs.
- Exposed weather and source-attribution metadata on the summary sensor, including which signals are explicitly pinned versus auto-filled from discovery.
- Updated the Lovelace card with an outdoor temperature chip and a compact sources panel so installability stays simple while troubleshooting gets much clearer.

## 0.3.1

- Reworked household chores handling so chore lists are cleaned, lightly prioritized, and exposed with a clearer `household_chores_summary` attribute.
- Grouped waste / affald countdown sensors into a single higher-signal summary plus structured `waste_pickups` metadata for timeline-style rendering.
- Refined the Lovelace card UX with a dedicated agenda area for upcoming chores and waste pickups, while keeping the rest of the house state in a separate signals stack.
- Kept auto-discovery unchanged while expanding user-visible polish and sensor attributes.

## 0.3.0

- Added a persistent discovery layer so Home Brief can keep separate track of discovered defaults versus explicit user selections.
- Home Brief now re-scans Home Assistant automatically on setup and reload, which also covers options saves because Home Assistant reloads the entry after saving options.
- Added `home_brief.rescan`, a manual response service for forcing a discovery refresh without reinstalling or poking through the UI.
- Changed coordinator logic to use discovered entities and lights as fallback when config fields are blank, instead of requiring every useful signal to be pinned up front.
- Expanded diagnostics and summary stats with discovery metadata, autofill visibility, effective config details, and last discovery scan time.
- Updated onboarding copy and docs to explain the new self-updating discovery behavior.

## 0.2.0

- Reworked the Lovelace card into a denser briefing layout with a strong primary insight, metric chips, compact status pills, and separate signal / chores panels.
- Added indoor temperature chips to the card and changed temperature discovery to explicitly prefer `sensor.bad_temperatur` when available.
- Added Household Chores next-3 support with autodetection that prefers `sensor.household_chores_next_3_tasks`, plus new summary attributes for chores list / count / source entity.
- Added an explicit `BACKLOG.md` so iteration and next steps are visible in-repo.

## 0.1.6

- Added automatic indoor temperature insights: below 20°C warns that it is getting cold, above 24°C warns that it is getting hot.
- Added automatic waste pickup insights for today / tomorrow / in 2 days using detected AffaldDK-style countdown sensors.
- Improved signal density so the brief can surface more than just solar surplus when your home exposes richer entities.

## 0.1.5

- Replaced the placeholder brand assets with a cleaner Home Brief icon/logo set for HACS and Home Assistant surfaces.
- Added matching dark variants and high-DPI `@2x` assets for better rendering in brands-compatible contexts.

## 0.1.4

- Fixed config-flow handling for optional entity selectors so blank occupancy / humidity fields no longer break setup with `Entity None is neither a valid entity ID nor a valid UUID`.
- Fixed dev dependency constraints so the repo no longer points at a non-existent `pytest-homeassistant-custom-component>=0.13.0` release.

## 0.1.3

- Fixed a real-world unit handling bug where discovered `kW` power sensors were treated like watts, which could break appliance done detection, solar surplus insights, and away-load warnings.
- Clarified install and troubleshooting docs around score-based discovery and internal `W` / `kW` normalization.

## 0.1.2

- Improved config-flow onboarding with better descriptions, units, and basic validation.
- Reworked entity discovery to use scoring instead of naive first-match selection.
- Added missing-entity visibility to coordinator output and Lovelace card UX.
- Hardened diagnostics with redacted entity IDs plus discovery summaries.
- Expanded docs, troubleshooting, FAQ, screenshot placeholders, and CI validation workflow.

## 0.1.1

- Initial template release.
