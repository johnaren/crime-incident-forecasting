from crime_incident_forecasting.config import ROOT, USER_AGENT, config

from io import BytesIO
import requests
from pathlib import Path
from datetime import date
import time

import pandas as pd
from geopy.geocoders import Nominatim
from tqdm import tqdm


def get_events_archive(download: bool = False) -> pd.DataFrame:
    path = Path(ROOT, config.data.dir, config.data.events_archive.name)
    if not download and path.exists():
        return pd.read_parquet(path)
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
    df = df[columns]
    df.to_parquet(path, index=False)
    return df


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
    path = Path(ROOT, config.data.dir, config.data.regions.name)
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
    df = df[["Municipality", "County"]]
    df.to_csv(path, index=False)
    print(f"Saved to {path}")
    return df


def get_geodata(
        regions: list[str] = None,
        download: bool = False
        ) -> pd.DataFrame:
    path = Path(ROOT, config.data.dir, config.data.geodata.name)
    if not download and path.exists():
        return pd.read_csv(path)
    if regions is None:
        raise ValueError("Requires regions to download.")
    geolocator = Nominatim(user_agent=USER_AGENT)
    locations = []
    for name in tqdm(regions):
        _, location = geolocator.geocode(query=name)
        location = ",".join(str(x) for x in location)
        locations.append(location)
        time.sleep(1)
    df = pd.DataFrame({
        "name": regions,
        "gps": locations,
    })
    df.to_csv(path, index=False)
    return df


def get_weather_archive(
        coords: list[str] = None,
        names: list[str] = None,
        start: str = None,
        end: str = None,
        download: bool = False,
        ) -> list[pd.DataFrame]:
    path = Path(ROOT, config.data.dir, config.data.weather_archive.name)
    if not download and path.exists():
        return pd.read_parquet(path)
    if download and names and len(coords) != len(names):
        raise ValueError(
            f"Length {len(coords)} not equal to length {len(names)}."
        )
    lats = []
    lons = []
    for x in coords:
        lat, lon = x.split(",")
        lats.append(float(lat))
        lons.append(float(lon))
    if end is None:
        end = date.today()
    if start is None:
        start = end
    response = requests.get(
        url="https://archive-api.open-meteo.com/v1/archive",
        headers={
            "User-Agent": USER_AGENT,
        },
        params = {
            "latitude": lats,
            "longitude": lons,
            "start_date": start,
            "end_date": end,
            "daily": [
                "apparent_temperature_mean",
                "sunshine_duration",
                "precipitation_sum",
            ],
        },
    )
    response.raise_for_status()
    dfs = []
    data = response.json()
    for i, data in enumerate(data):
        df = pd.DataFrame(data["daily"])
        if names is not None:
            df["name"] = names[i]
        df["gps"] = coords[i]
        dfs.append(df)
    df: pd.DataFrame = pd.concat(dfs, ignore_index=True)
    df.to_parquet(path, index=False)
    return df
