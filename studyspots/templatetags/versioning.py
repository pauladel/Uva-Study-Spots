import os

import git
from django import template
from django.utils.html import format_html
from git import InvalidGitRepositoryError


try:
    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha[:7]
    with open('studyspots/static/studyspots/git-hash.txt', 'w') as f:
        f.write(sha)
except InvalidGitRepositoryError:
    try:
        with open('studyspots/static/studyspots/git-hash.txt') as f:
            sha = f.read()
    except FileNotFoundError:
        try:
            with open('staticfiles/studyspots/git-hash.txt') as f:
                sha = f.read()
        except FileNotFoundError:
            sha = None

register = template.Library()


@register.simple_tag()
def git_hash():
    if sha:
        return format_html('<p class="mb-0 text-secondary footer-text">Hash {}</p>', str(sha))
    else:
        return ""
