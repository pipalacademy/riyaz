import yaml
from pathlib import Path


# path to sqlite database
database_path = "riyaz.db"
assets_path = "assets"


def load_config(path):
    global database_path, assets_path

    if path.exists():
        with open(path, "r") as f:
            yml_config = yaml.safe_load(f)

        if "database_path" in yml_config:
            # resolve relative path
            full_path = path.parent / Path(yml_config["database_path"])
            database_path = str(full_path.resolve())

        if "assets_path" in yml_config:
            # resolve relative path
            full_path = path.parent / Path(yml_config["assets_path"])
            assets_path = str(full_path.resolve())

    # TODO: implement config for extensions


load_config(Path("riyaz.yml"))
