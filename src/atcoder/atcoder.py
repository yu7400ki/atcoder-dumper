from typing import List

import requests
from bs4 import BeautifulSoup


class Submission:
    def __init__(
        self,
        id: int,  # noqa
        epoch_second: int,
        problem_id: str,
        contest_id: str,
        user_id: str,
        language: str,
        point: float,
        length: int,
        result: str,
        execution_time: int,
    ) -> None:
        self.id = id
        self.epoch_second = epoch_second
        self.problem_id = problem_id
        self.contest_id = contest_id
        self.user_id = user_id
        self.language = language
        self.point = point
        self.length = length
        self.result = result
        self.execution_time = execution_time


def fetch_submissions(user: str) -> List[Submission]:
    url = "https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions"
    payload = {"user": user, "from_second": "0"}
    response = requests.get(url, params=payload).json()
    return list(map(lambda x: Submission(**x), response))


def fetch_submission_code(contest_id: str, submission_id: int) -> str:
    url = f"https://atcoder.jp/contests/{contest_id}/submissions/{submission_id}"
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    code = soup.select_one("pre#submission-code")

    if code is None:
        raise Exception("Code not found.")

    return code.text
