import json
import os
from typing import Dict, List

import git
from fire import Fire

from atcoder import atcoder

services = ["atcoder.jp"]
settings_file = "settings.json"


class Filter:
    def __init__(self, result: List[str] = [], language: List[str] = []) -> None:
        self.result: List[str] = result
        self.language: List[str] = language


class Setting:
    def __init__(
        self,
        service: str,
        username: str,
        filter: Filter = Filter(),  # noqa
    ):
        self.service = service
        self.username = username
        self.filter = filter


def _setting2json(setting: Setting) -> Dict[str, str | Dict[str, List[str]]]:
    return {
        "service": setting.service,
        "username": setting.username,
        "filter": {
            "result": setting.filter.result,
            "language": setting.filter.language,
        },
    }


def _load_settings() -> Dict[str, Setting]:
    with open(settings_file, mode="r", encoding="UTF-8") as file:
        settings = json.load(file)

    return {service: Setting(**setting) for service, setting in settings.items()}


def init() -> None:
    """Initialize the directory for the first time."""

    init_settings: Dict[str, Setting] = {}

    for service in services:
        if not os.path.isdir(service):
            os.mkdir(service)

    if not os.path.isfile(settings_file):
        with open(settings_file, mode="w", encoding="UTF-8") as file:
            for service in services:
                username = input(f"Please enter your {service} username: ")
                init_settings[service] = Setting(service, username)

            json.dump({service: _setting2json(setting) for service, setting in init_settings.items()}, file, indent=4)

    if not os.path.isdir(".git"):
        repo = git.Repo.init()
        repo.git.add(settings_file)
        repo.index.commit("Initial commit")


def dump() -> None:
    """Dump your submissions."""

    setting: Setting = _load_settings()["atcoder.jp"]

    submissions = atcoder.fetch_submissions(setting.username)

    for submission in submissions:
        print(submission.problem_id)


def main() -> None:
    Fire({"init": init, "dump": dump})
