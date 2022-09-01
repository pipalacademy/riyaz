import yaml
from pathlib import Path


# path to sqlite database
database_path = "riyaz.db"
assets_path = "assets"


if (config_path := Path("riyaz.yml")).exists():
    with open(config_path, "r") as f:
        _yml_config = yaml.safe_load(f)

    if "database_path" in _yml_config:
        database_path = _yml_config["database_path"]

    if "assets_path" in _yml_config:
        assets_path = _yml_config["assets_path"]
