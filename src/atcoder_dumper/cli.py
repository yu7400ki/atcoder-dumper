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
    if not os.path.isfile(settings_file):
        raise FileNotFoundError(f"{settings_file} is not found.\nPlease run `atcoder-dumper init` first.")

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

    repo = git.Repo(".")
    repo.git.add(file_path)
    title = f"Add {language} code for {contest_id}/{problem_id}"
    description = json.dumps(submission.__dict__, indent=4)
    try:
        repo.git.commit("-m", title, "-m", description, "--date", submission.epoch_second)
        repo.git.rebase("HEAD^", "--committer-date-is-author-date")
    except git.GitCommandError:
        pass


def _extract_desc_from_commit(commit: str) -> str:
    try:
        return "".join(commit.split("\n")[2:])
    except IndexError:
        return ""


def _load_latest_submission_commit() -> atcoder.Submission:
    repo = git.Repo(".")
    for commit in repo.iter_commits():
        desc = _extract_desc_from_commit(str(commit.message))
        if desc != "":
            try:
                info = json.loads(desc)
                return atcoder.Submission(**info)
            except json.JSONDecodeError:
                continue
            except TypeError:
                continue

    raise ValueError("No submission found.")


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
        repo = git.Repo.init()
        repo.git.add(".")
        repo.git.commit("-m", "Initial commit")

    print("Initialized successfully.")


def dump() -> None:
    """Dump your submissions."""

    setting: Setting = _load_settings()["atcoder.jp"]

    if not os.path.isdir(".git"):
        raise NotADirectoryError("This directory is not a git repository.\nPlease run `git init` first.")

    if setting.username == "":
        raise ValueError("Username is empty.\nPlease set your username in settings.json.")

    try:
        latest_submission = _load_latest_submission_commit()
        epoch_time = latest_submission.epoch_second + 1
    except ValueError:
        epoch_time = 0

    submissions = atcoder.fetch_submissions(setting.username, epoch_time)
    filtered_submissions = atcoder.filter_submissions(submissions, setting.filter.result, setting.filter.language)

    for submission in tqdm(list(filtered_submissions)):
        _dump_code(submission)
        time.sleep(1.5)

    print("Dumped successfully.")


def main() -> None:
    Fire({"init": init, "dump": dump})
