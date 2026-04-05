# Changelog

All notable changes to this project will be documented in this file.

## 0.6.7

- Added a first-class imported `daily_brief_package` surface to Home Brief so the daily brief can populate a richer structured section instead of only feeding three flat Morning Brief lines.
- The Morning Brief panel can now show package rows for imported Nikolaj tasks, household tasks, and solar context when that data exists, creating a real home for the daily brief package inside the card.
- This is Task 1 of the split: create room for the daily brief package in Home Brief before wiring the final trigger/action path into it.

## 0.6.6

- Reworked the `Household focus` section so it now lists the actual household tasks with assignee names instead of leaning on a Nikolaj-specific summary path.
- Fixed `Today by slot` to use only chores due today, which removes the incorrect tomorrow leakage that made the section look polished but wrong.
- This is a correctness release: less personalized leakage, more literal household context, and slot grouping that matches the label on the card.

## 0.6.5

- Reduced overlap between Morning Brief, Suggested Move, Next up, and the leftover supporting signals by suppressing duplicate lines at the coordinator layer before they reach the card.
- Tightened the card hierarchy so Morning Brief remains primary, while Next up / action / slot context sit in a cleaner two-column follow-up structure instead of one long repeated stack.
- This is a product cleanup release: less repetition, clearer information density, and a better foundation for expanding the Morning Brief surface without turning the card into a noisy dump.

## 0.6.4

- Fixed the sensor platform to read coordinators from the new runtime registry shape instead of the old `hass.data[DOMAIN][entry_id]` dict path.
- This restores Home Brief entity creation after the runtime bookkeeping refactor, which is why the publish path could succeed while `sensor.home_brief_summary` still did not exist.
- Production hotfix: get the entities back so the morning-brief data can actually surface in the card.

## 0.6.3

- Reworked Home Brief runtime bookkeeping so loaded coordinators live in a dedicated runtime structure instead of sharing a loose dict with service/frontend registration flags.
- Hardened service-side coordinator resolution for `publish_morning_brief`, `get_brief`, `get_actions`, and `rescan`, which should stop live service calls from missing a loaded entry due to runtime state shape issues.
- This is a production hotfix aimed directly at the morning-brief publish loop failing even after the service was registered live.

## 0.6.1

- Added the first explicit person-profile foundation to Home Brief storage, seeded with a default `Nikolaj` profile instead of leaving personalization as an implicit coordinator assumption.
- Exposed active profile metadata on the summary sensor attributes so future preference/settings work has a real attachment point.
- This is intentionally a small foundation slice: behavior is mostly unchanged, but the product now has a proper profile model to build personalization on top of.

## 0.6.0

- Added a persisted structured morning-brief state to Home Brief storage plus a new `home_brief.publish_morning_brief` service, so schedulers can publish stable brief payloads directly into the integration instead of forcing the card to depend on a local runtime script.
- Changed coordinator loading order so published stored brief data wins, while the old local runtime bridge remains only as a fallback path.
- This establishes the intended architecture seam: brief generation can evolve independently from Home Brief rendering, which is what the scheduled brief pipeline needed to stop being brittle.

## 0.5.9

- Promoted the Morning brief block to a first-class card section instead of a flat appended list, with a lead priority, supporting follow-ups, and compact context chips for weather / freshness.
- Moved Morning brief above the generic focus stack so the scheduled brief data now drives the card hierarchy instead of reading like secondary metadata.
- Tightened the visual treatment of the Morning brief surface so it scans more like a productized briefing panel and less like debug output.

## 0.4.7

- Hardened household chore normalization so Home Brief now handles more real-world task payload shapes (`title`/`name`/`task`, alternate due-date fields, nested assignee objects) instead of leaking raw object text into the summary sensor and card.
- Cleaned Lovelace agenda rendering for chores by formatting ISO-style dates into human-readable labels and supporting richer assignee payloads, which should stop the ugly JSON-ish rows that slipped through in mixed chore integrations.
- Kept this release focused on boring stability: no new feature surface, just safer parsing and cleaner frontend output for existing installs.

## 0.4.6

- Fixed the Lovelace card frontend registration to use a versioned resource URL, so Home Assistant/browser caches pick up new card builds instead of serving stale JavaScript after upgrades.
- Made the card bootstrap idempotent by guarding both `customElements.define()` and `window.customCards.push()`, which avoids duplicate-registration failures when Home Assistant reloads frontend resources.
- This should restore reliable card discovery in the card picker and prevent post-upgrade configuration errors caused by stale or double-loaded frontend assets.

## 0.4.5

- Added an explicit HACS validation workflow so repository/release checks cover the current custom integration packaging expectations, including shipped `brand/` assets.
- Clarified the README to separate Home Assistant brand support from the still-open HACS dashboard icon gap, so the project docs match current real-world behavior.
- Confirmed the integration already ships the expected `custom_components/home_brief/brand/` files; blank HACS store branding is now documented as an upstream HACS limitation rather than a missing package asset.

## 0.4.4

- Reworked the Lovelace card visual design with stronger hierarchy, calmer spacing, larger headline typography, softer panel treatment, and a more product-like overall layout.
- Replaced the loose metric chip row with cleaner metric tiles and converted status pills into labeled attention rows so important signals scan faster without the developer-UI feel.
- Tightened agenda, signals, and sources presentation so chores, waste pickups, setup issues, and follow-up insights feel intentional instead of visually noisy.

## 0.4.3

- Fixed the packaged `custom_components/home_brief/brand/` set so Home Assistant 2026.3+ serves the actual landscape logo via the local brands API instead of a stale square asset.
- Added the missing high-DPI `@2x` brand files to the shipped integration directory so repo-native branding is complete for new Home Assistant brands-proxy consumers.
- Kept existing repo-root HACS branding assets intact.

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
