from crime_incident_forecasting.config import config
from crime_incident_forecasting.data import get_labels, get_regions
from crime_incident_forecasting.models import get_transformer


def map_label(
        type: list[str],
        description: list[str],
) -> dict[str, list]:
    transformer = get_transformer()
    map_fn = lambda x: transformer.encode(
        inputs=x,
        batch_size=config.models.transformer.batch_size,
        show_progress_bar=True,
        )
    labels = get_labels()
    label_embeddings = map_fn(labels)
    type_embeddings = map_fn(type)
    description_embeddings = map_fn(description)
    event_embeddings = type_embeddings + description_embeddings
    scores = transformer.similarity(event_embeddings, label_embeddings)
    result = scores.max(dim=1)
    return {
        "label": [labels[i] for i in result.indices],
        "similarity": result.values,
    }


def map_region(municipality: list[str]) -> list[str]:
    regions = get_regions()
    to_county = {
        str.lower(k): str.capitalize(v)
        for k, v in zip(regions["Municipality"], regions["County"])
    }
    out = []
    for name in municipality:
        name = name.lower()
        if name not in to_county:
            for county in regions["County"]:
                county = county.lower()
                if county in name:
                    to_county[name] = county.capitalize()
        out.append(to_county[name])
    return out
