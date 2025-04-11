import os

from dotenv import load_dotenv
from github import Github

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_NAME = os.getenv('REPO_NAME')
github_client = Github(GITHUB_TOKEN)
repo = github_client.get_repo(REPO_NAME)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
