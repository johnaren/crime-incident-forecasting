from crime_incident_forecasting.config import USER_AGENT, config

from io import BytesIO
import requests

import pandas as pd


def get_events_archive() -> pd.DataFrame:
    response = requests.get(
        url="https://github.com/dnouri/polisen-se-events-history/releases/download/data-latest/events.parquet",
        headers={
            "User-Agent": USER_AGENT,
        },
        params={},
    )
    response.raise_for_status()
    df = pd.read_parquet(BytesIO(response.content))
    df.rename(
        columns={
            "event_id": "id",
            "api_location_name": "location_name",
            "api_location_gps": "location_gps",
        },
        inplace=True,
    )
    columns = [
        "id",
        "datetime",
        "name",
        "summary",
        "url",
        "type",
        "location_name",
        "location_gps",
    ]
    return df[columns]


def get_events() -> pd.DataFrame:
    response = requests.get(
        url="https://polisen.se/api/events",
        headers={
            "User-Agent": USER_AGENT,
        },
        params={},
    )
    response.raise_for_status()
    events = response.json()
    for event in events:
        event["location_name"] = event["location"]["name"]
        event["location_gps"] = event["location"]["gps"]
        del event["location"]
    df = pd.DataFrame(events)
    return df


def get_labels() -> list[str]:
    return config.data.labels
