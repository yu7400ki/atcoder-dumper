import json
import os
import time
from typing import Dict, List

import git
from fire import Fire
from tqdm import tqdm

from atcoder import atcoder

services = ["atcoder.jp"]
settings_file = "settings.json"


class SubmissionFilter:
    def __init__(self, result: List[str] = [], language: List[str] = []) -> None:
        self.result: List[str] = result
        self.language: List[str] = language


class Setting:
    def __init__(
        self,
        username: str,
        filter: SubmissionFilter = SubmissionFilter(),  # noqa
    ):
        self.username = username
        self.filter = filter


def _setting2dict(setting: Setting) -> Dict[str, str | Dict[str, List[str]]]:
    return {
        "username": setting.username,
        "filter": {
            "result": setting.filter.result,
            "language": setting.filter.language,
        },
    }


def _dict2setting(setting: Dict[str, str | Dict[str, List[str]]]) -> Setting:
    assert isinstance(setting["username"], str)
    assert isinstance(setting["filter"], dict)

    return Setting(
        str(setting["username"]),
        SubmissionFilter(**setting["filter"]),
    )


def _load_settings() -> Dict[str, Setting]:
    with open(settings_file, mode="r", encoding="UTF-8") as file:
        settings = json.load(file)

    return {service: _dict2setting(setting) for service, setting in settings.items()}


def _dump_code(submission: atcoder.Submission) -> None:
    language = submission.language
    contest_id = submission.contest_id
    problem_id = submission.problem_id
    code = submission.fetch_code()
    extension = submission.get_extension()

    dir_path = f"./atcoder.jp/{language}/{contest_id}/"
    file_path = f"{dir_path}{problem_id}{extension}"

    os.makedirs(dir_path, exist_ok=True)
    with open(file_path, mode="w", encoding="UTF-8", newline="") as f:
        f.write(code)


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
                init_settings[service] = Setting(username)

            json.dump({service: _setting2dict(setting) for service, setting in init_settings.items()}, file, indent=4)

    if not os.path.isfile(".gitignore"):
        with open(".gitignore", mode="w", encoding="UTF-8") as file:
            file.write(settings_file)

    if not os.path.isdir(".git"):
        git.Repo.init()

    print("Initialized successfully.")


def dump() -> None:
    """Dump your submissions."""

    setting: Setting = _load_settings()["atcoder.jp"]

    submissions = atcoder.fetch_submissions(setting.username)
    filtered_submissions = atcoder.filter_submissions(submissions, setting.filter.result, setting.filter.language)

    for submission in tqdm(list(filtered_submissions)):
        _dump_code(submission)
        time.sleep(2)


def main() -> None:
    Fire({"init": init, "dump": dump})
