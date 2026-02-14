"""API layer for HACS Template.

This is a placeholder where you would talk to a real device/cloud/local API.
Keep all IO in here and let the coordinator call it.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExampleData:
    """Data returned by the API."""

    value: int


class HacsTemplateApi:
    """Example API client."""

    async def async_get_data(self) -> ExampleData:
        # Replace with real IO. Keep it async.
        return ExampleData(value=1)

