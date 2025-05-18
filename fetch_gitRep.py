import requests
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = "https://api.github.com"

def get_all_repos():
    url = f"{GITHUB_API_URL}/user/repos"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    params = {
        "visibility": "all",  # can be 'all', 'public', or 'private'
        "per_page": 100       # maximum per page
    }

    repos = []
    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            repos.extend(response.json())
            # Check if there is a "next" page
            url = response.links.get('next', {}).get('url')
            params = None  # Params only on first page
        else:
            print(f"Error {response.status_code}: {response.text}")
            break
    repository_name = []
    for repo in repos:
        repository_name.append(repo['name'])
    return repository_name
