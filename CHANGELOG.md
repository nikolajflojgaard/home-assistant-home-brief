# Changelog

All notable changes to this project will be documented in this file.

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
