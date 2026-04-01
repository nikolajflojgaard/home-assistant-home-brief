# Home Brief Action Layer

## Purpose

Home Brief already explains what the house is doing.
The next step is making it say **what to do now**.

This layer should turn house state + chores + weather + energy context into:
- one **top action**
- a short list of **recommended actions**
- a cleaner sense of urgency

## Product goal

Move from:
- "Interesting home status"

to:
- "Do this now"

## Principles

- Max 1 top action
- Max 3 recommended actions
- No fake certainty
- If confidence is weak, say less
- Actions must be concrete
- Actions should prefer things the household can actually do now

## Example outputs

- Run dishwasher now while solar is covering it.
- Ventilate now — humidity is still elevated.
- Turn off downstairs lights — nobody is home.
- Take the trash when leaving — it is the cleanest bundled errand.
- Ignore chores for now — nothing is urgent.

## Inputs

### Existing Home Brief signals
- solar power
- home power
- solar surplus
- power price
- occupancy
- lights on
- humidity
- weather state / temperature / forecast summary
- waste pickups
- household chores

### Desired future inputs
- person-specific chores
- leave-home windows
- dishwasher / appliance state
- cheap-price time windows
- battery / EV context

## Output contract

Add these summary sensor attributes:

- `top_action`
- `top_action_score`
- `top_action_category`
- `top_action_reason`
- `recommended_actions`
- `recommended_action_count`

## Action shape

```json
{
  "title": "Run dishwasher now",
  "summary": "Solar is well above house load, so this is a cheap consumption window.",
  "category": "energy",
  "score": 91,
  "reason": "solar_surplus",
  "entity_id": null
}
```

## Action categories

- `energy`
- `chores`
- `waste`
- `comfort`
- `away`
- `weather`
- `maintenance`

## Candidate producers

### 1. Energy
Examples:
- Run heavy load now if solar surplus is strong
- Avoid flexible loads if power is expensive and solar is weak
- Good EV charge window

### 2. Chores
Examples:
- Do highest-priority household task now
- Surface Nikolaj-relevant next task when available
- Suggest a quick win first if nothing urgent exists

### 3. Waste
Examples:
- Take waste out today
- Put bins out tonight for tomorrow pickup

### 4. Comfort / indoor climate
Examples:
- Ventilate after humidity spike
- Open windows while weather is mild
- Close up if weather turns rough

### 5. Away / occupancy
Examples:
- Turn off lights if nobody is home
- Investigate unusual home draw when house is empty

## Scoring

Deterministic scoring first.

Base weighting:
- urgency: 0-40
- impact: 0-30
- time sensitivity: 0-15
- ease / agency: 0-10
- confidence modifier: 0.6x-1.0x

## Initial heuristics

### Strong action scores
- nobody home + lights on: very high
- nobody home + meaningful home load: very high
- waste pickup today: very high
- solar surplus > 1kW and house load low: high
- humidity above threshold: medium-high
- chores queue only: medium
- cheap power only: medium

## Selection rules

1. Build candidates
2. Sort by score descending
3. Deduplicate overlapping actions
4. Pick top 1 as `top_action`
5. Return up to 3 as `recommended_actions`

## UX behavior

### Summary sensor
Keep current summary text behavior for backward compatibility.
But expose action attributes so cards / automations / daily brief can use them.

### Lovelace card
Later enhancement:
- top action block above the signal stack
- recommended actions below the main insight
- simple verbs, not generic labels

### Daily brief
Use `top_action` and/or `recommended_actions` to sharpen the household section.

## Phase 1 implementation

- add action candidate builder in coordinator
- add action attributes to sensor
- use existing signals only
- no config UI changes yet
- no notifications yet

## Phase 2

- bring in person-specific chore signals
- add Telegram action surface
- add done/snooze feedback loop

## Success metric

When reading Home Brief, the user should think:

**"Right. That's the thing to do."**
