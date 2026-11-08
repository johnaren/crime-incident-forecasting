from crime_incident_forecasting.config import ROOT, USER_AGENT, config

from io import BytesIO
import requests
from pathlib import Path

import pandas as pd


def get_events_archive() -> pd.DataFrame:
    url = (
        "https://github.com/dnouri/polisen-se-events-history"
        "/releases/download/data-latest/events.parquet"
    )
    response = requests.get(
        url,
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


def get_regions(download: bool = False) -> pd.DataFrame:
    path = Path(ROOT, config.regions.dir, config.regions.name)
    if not download and path.exists():
        return pd.read_csv(path)
    url = (
        "https://scb.se"
        "/contentassets/6a74a52b28994e2bbe23dcdd6754987c/knkopplingar_2026.xlsx"
    )
    response = requests.get(
        url,
        headers={
            "User-Agent": USER_AGENT,
        },
    )
    response.raise_for_status()
    print(f"Downloaded from {url}")
    df = pd.read_excel(BytesIO(response.content))
    df.columns = df.iloc[8].values
    df = (
        df
        .dropna()
        .drop(index=[6, 8])
        .reset_index(drop=True)
    )
    df = df[["County", "Municipality"]]
    df.to_csv(path, index=False)
    print(f"Saved to {path}")
    return df
