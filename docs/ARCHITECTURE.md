# Architecture

## Current architecture

```mermaid
flowchart LR
  UI["Config Flow"] --> Entry["Config Entry"]
  Entry --> Coord["DataUpdateCoordinator"]
  Coord --> API["api.py (IO)"]
  Coord --> Store["storage.py (.storage)"]
  Coord --> Entities["entities (sensor.py)"]
  UI --> Services["services.py"]
  UI --> WS["websocket_api.py"]
  Entry --> Diagnostics["diagnostics.py (redacted)"]
```

Discovery now feeds both runtime fallback and source attribution, so the coordinator can explain not just *what* it inferred but also *where each signal came from*.

## Rework direction

The integration is now moving toward a stronger layered architecture documented in [`docs/REWORK-FOUNDATION.md`](./REWORK-FOUNDATION.md).

Target direction:

```mermaid
flowchart TD
  Sources["Signals / Producers"] --> Ingest["Ingestion"]
  Ingest --> Normalize["Normalization"]
  Normalize --> Personalize["Personalization"]
  Personalize --> Prioritize["Prioritization"]
  Prioritize --> ViewModel["View model"]
  ViewModel --> Sensor["Summary sensor"]
  ViewModel --> Card["Lovelace card"]
  ViewModel --> Briefs["Scheduled / chat briefs"]
  Settings["Profiles + preferences"] --> Personalize
  Settings --> Prioritize
  Store["Persisted storage"] --> Normalize
  Store --> ViewModel
```

That rework exists because Home Brief needs to become more personalized, more inspectable, and more configurable without keeping all business logic jammed directly into one coordinator path.

<!-- code-doc-pipeline:start -->

## Observed Structure

### Manifests

- `Makefile`
- `pyproject.toml`


### Entrypoints

- None detected


### Deployment Hints

- None detected


### Detected Frameworks

- None detected


## Diagrams

- [Context](diagrams/context.mmd)
- [Container or flow](diagrams/container-or-flow.mmd)
- [Critical sequence](diagrams/critical-sequence.mmd)
- [Data flow](diagrams/data-flow.mmd)
- [Deployment](diagrams/deployment.mmd)

## Detected Runtime Flows

- None detected


## Unknowns

- Confirm runtime boundaries with a service owner.
- Confirm whether detected interface hints are public APIs, internal routes, or framework conventions.
<!-- code-doc-pipeline:end -->
