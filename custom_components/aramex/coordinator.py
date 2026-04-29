import logging
from datetime import timedelta

import requests

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=15)

_URL = "https://www.aramex.com.au/umbraco/api/TrackingApi/GetTrackingData"
_HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/147.0.0.0 Safari/537.36"
    ),
    "x-requested-with": "XMLHttpRequest",
}


def _fetch(label_number: str) -> dict:
    """Blocking fetch — must be called via async_add_executor_job."""
    params = {"LabelNo": label_number, "dataFormat": "json"}
    headers = {
        **_HEADERS,
        "referer": f"https://www.aramex.com.au/tools/track?l={label_number}",
    }
    response = requests.get(_URL, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()
    return data.get("result", {})


class AramexCoordinator(DataUpdateCoordinator):
    """Coordinator that polls the Aramex tracking API."""

    def __init__(self, hass: HomeAssistant, label_number: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{label_number}",
            update_interval=UPDATE_INTERVAL,
        )
        self.label_number = label_number

    async def _async_update_data(self) -> dict:
        try:
            return await self.hass.async_add_executor_job(_fetch, self.label_number)
        except requests.RequestException as err:
            raise UpdateFailed(f"Error fetching Aramex data: {err}") from err
