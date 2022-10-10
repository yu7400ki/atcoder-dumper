import json
import os
from typing import Dict, List

import git
from fire import Fire

services = ["atcoder.jp"]
settings_file = "settings.json"


class Setting:
    def __init__(
        self,
        service: str,
        username: str = "",
        filter: Dict[str, List[str]] = {"status": [], "filter": []},  # noqa
    ):
        self.service = service
        self.username = username
        self.filter = filter


def _load_settings() -> Dict[str, Setting]:
    with open(settings_file, mode="r", encoding="UTF-8") as file:
        settings = json.load(file)

    for service in settings:
        settings[service] = Setting(**settings[service])

    return settings


def init() -> None:
    """Initialize the directory for the first time."""

    init_settings = {service: Setting(service) for service in services}

    for d in services:
        if not os.path.isdir(d):
            os.mkdir(d)

    if not os.path.isfile(settings_file):
        with open(settings_file, mode="w", encoding="UTF-8") as file:
            for s in services:
                username = input(f"Please enter your {s} username: ")
                init_settings[s].username = username
            json.dump({service: setting.__dict__ for service, setting in init_settings.items()}, file, indent=4)

    if not os.path.isdir(".git"):
        repo = git.Repo.init()
        repo.git.add(settings_file)
        repo.index.commit("Initial commit")


def main() -> None:
    Fire({"init": init})
