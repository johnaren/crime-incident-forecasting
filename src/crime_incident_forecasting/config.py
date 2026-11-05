import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class Config(dict):
    def __getattr__(self, name):
        attr = self[name]
        if isinstance(attr, dict):
            return Config(attr)
        return attr


with open(ROOT / "pyproject.toml", "rb") as f:
    pyproject = Config(tomllib.load(f))


with open(ROOT / "config.toml", "rb") as f:
    config = Config(tomllib.load(f))


USER_AGENT = (
    f"{pyproject.project.name}/{pyproject.project.version} "
    "("
        f"{pyproject.urls.repository}"
        f"; contact: {pyproject.contact.email}"
    ")"
)