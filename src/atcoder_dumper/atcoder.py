import json
import os
from dataclasses import dataclass
from typing import Iterable, List

import requests
from bs4 import BeautifulSoup

with open(os.path.join(os.path.dirname(__file__), "extensions.json"), mode="r", encoding="UTF-8") as file:
    extensions = json.load(file)


@dataclass
class Submission:
    id: int  # noqa
    epoch_second: int
    problem_id: str
    contest_id: str
    user_id: str
    language: str
    point: float
    length: int
    result: str
    execution_time: int

    def fetch_code(self) -> str:
        url = f"https://atcoder.jp/contests/{self.contest_id}/submissions/{self.id}"
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        code = soup.select_one("pre#submission-code")

        if code is None:
            raise Exception("Code not found.")

        return code.text

    def get_extension(self) -> str:
        for v in extensions:
            if self.language.startswith(v):
                return f".{extensions[v]}"
        return ""


def fetch_submissions(user: str, epoch_second: int = 0) -> List[Submission]:
    url = "https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions"
    payload = {"user": user, "from_second": f"{epoch_second}"}
    response = requests.get(url, params=payload).json()
    return list(map(lambda x: Submission(**x), response))


def filter_submissions(submissions: List[Submission], result: List[str], language: List[str]) -> Iterable[Submission]:
    def result_filter(submission: Submission) -> bool:
        if result == []:
            return True
        return submission.result in result

    def language_filter(submission: Submission) -> bool:
        if language == []:
            return True
        return submission.language in language

    return filter(lambda x: result_filter(x) and language_filter(x), submissions)
