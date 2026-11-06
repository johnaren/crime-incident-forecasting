from crime_incident_forecasting.config import config, DEVICE, ROOT

from typing import Callable

from sentence_transformers import SentenceTransformer

import torch


def get_transformer() -> SentenceTransformer:
    return SentenceTransformer(
        model_name_or_path=config.models.transformer.name,
        cache_folder=ROOT / config.models.dir,
        device=DEVICE,
    )
