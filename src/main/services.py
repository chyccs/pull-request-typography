from github import (
    Github,
    Repository,
)
from github.PullRequest import PullRequest


def fetch_github_repo(
    access_token: str,
    owner: str,
    repository: str,
) -> Repository.Repository:
    return Github(access_token).get_user(owner).get_repo(repository)


def fetch_pull_request(
    access_token: str,
    owner: str,
    repository: str,
    number: int,
) -> PullRequest:
    return fetch_github_repo(access_token, owner, repository).get_pull(number=number)


def update_pull_request(
    pull_request: PullRequest,
    title: str,
    body: str,
):
    pull_request.edit(title=title, body=body)
