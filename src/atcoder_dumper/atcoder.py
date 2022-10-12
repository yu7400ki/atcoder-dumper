import dataclasses
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


@dataclass
class SubmissionFilter:
    result: List[str]
    language: List[str]


@dataclass
class AtCoder:
    username: str
    submissions: List[Submission] = dataclasses.field(default_factory=list, init=False)

    def fetch_submissions(self, epoch_second: int) -> List[Submission]:
        url = "https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions"
        payload = {"user": self.username, "from_second": f"{epoch_second}"}
        response = requests.get(url, params=payload).json()
        result = list(map(lambda x: Submission(**x), response))
        self.submissions = result
        return result

    def filter_submissions(self, submission_filter: SubmissionFilter) -> Iterable[Submission]:
        def result_filter(x: Submission) -> bool:
            if submission_filter.result == []:
                return True
            return x.result in submission_filter.result

        def language_filter(x: Submission) -> bool:
            if submission_filter.language == []:
                return True
            return x.language in submission_filter.language

        return filter(result_filter, filter(language_filter, self.submissions))
