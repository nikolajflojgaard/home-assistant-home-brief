# FAQ

## What problem is Home Brief solving?

Most Home Assistant dashboards are dense and noisy. Home Brief compresses a few high-signal entity states into one readable summary and a short ranked list of useful insights.

## Does it talk to an external API?

No. Right now it derives everything from existing Home Assistant entity state.

## Why does setup prefill entities automatically?

Because manual setup is where good integrations usually die. Home Brief uses discovery heuristics to reduce friction, then lets you override everything.

## Is discovery perfect?

No. It is score-based and much better than a naive first-match lookup, but every Home Assistant install is different.

## Do I need all fields configured?

No. You can start with one or two useful signals and expand later.

## What if I rename source entities later?

Home Brief will still work for the remaining entities, but it will surface a missing-entity warning so you know the config needs cleanup.

## Why does the card open more-info when clicked?

Because that is the expected Home Assistant behavior. Custom cards that ignore that pattern feel broken.

## What should a bug report include?

At minimum:

- what you expected
- what happened instead
- your Home Assistant version
- the downloaded diagnostics bundle
- relevant logs from `custom_components.home_brief`
