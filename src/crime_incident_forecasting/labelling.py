from crime_incident_forecasting.config import config
from crime_incident_forecasting.data import get_labels
from crime_incident_forecasting.models import get_transformer


def map_event(
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
