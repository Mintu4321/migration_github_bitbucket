import os
import time

import requests
from requests.auth import HTTPBasicAuth
from fetch_gitRep import get_all_repos
from dotenv import load_dotenv
load_dotenv()

BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_APP_PASSWORD = os.getenv("PASSWORD")
BITBUCKET_WORKSPACE = os.getenv("BITBUCKET_WORKSPACE")

REPO_NAMES = get_all_repos()

def create_bitbucket_repo(workspace, repo_slug, username, app_password, is_private=True):

    for repo in repo_slug:
        bit_bucket_repo = repo.lower()
        url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{bit_bucket_repo}"
        payload = {
            "mainbranch": {
                "name": "main"
                },
            "scm": "git",
            "is_private": is_private

        }
        print(f"🚀 Creating repository '{repo}' in workspace '{workspace}'...")
        response = requests.post(url, json=payload, auth=HTTPBasicAuth(username, app_password))
        time.sleep(2)
        if response.status_code == 201 or response.status_code == 201:
            print("✅ Repository created successfully!")
            # print("📎 Clone URL (SSH):", response.json().get("links", {}).get("clone", [])[1]["href"])
        else:
            print(f"❌ Failed to create repository: {response.status_code}")
            print(response.text)
            break

