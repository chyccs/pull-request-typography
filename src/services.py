from github import Github
from github import Repository
from github.PullRequest import PullRequest


def get_github_repo(access_token, repository_name) -> Repository:
    g = Github(access_token)
    return g.get_user().get_repo(repository_name)

def get_pull_request(repo: Repository, number) -> PullRequest:
    return repo.get_pull(number=number)

def update_pull_request(pull_request: PullRequest, title, body):
    pull_request.edit(title=title, body=body)
