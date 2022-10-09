import json
import os

import git
from fire import Fire

services = ["atcoder.jp"]
settings_file = "settings.json"


def init() -> None:
    """Initialize the directory for the first time."""

    init_settings = {
        service: {
            "username": "",
            "filter": {
                "status": [],
                "language": [],
            },
        }
        for service in services
    }

    for d in services:
        if not os.path.isdir(d):
            os.mkdir(d)

    if not os.path.isfile(settings_file):
        with open(settings_file, mode="w", encoding="UTF-8") as file:
            for s in services:
                username = input(f"Please enter your {s} username: ")
                init_settings[s]["username"] = username
            json.dump(init_settings, file, indent=4)

    if not os.path.exists(".git"):
        repo = git.Repo.init()
        repo.git.add(settings_file)
        repo.index.commit("Initial commit")


def main() -> None:
    Fire({"init": init})
