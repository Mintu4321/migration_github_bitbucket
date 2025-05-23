import os
import shutil
import time
import requests

import git  # GitPython
import tempfile
import logging
from fetch_gitRep import get_all_repos
from create_repo import create_bitbucket_repo


BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")  # Not your email
BITBUCKET_APP_PASSWORD = os.getenv("PASSWORD")
BITBUCKET_WORKSPACE = os.getenv("BITBUCKET_WORKSPACE") # Often same as your username
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# fetch all the repo details from the github
REPO_NAMES = get_all_repos()

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("repo_migration.log"),
            logging.StreamHandler()
        ]
    )


BITBUCKET_USER = os.getenv("BITBUCKET_USER")
GITHUB_USER = os.getenv("GITHUB_USER")

# Create bitbucket repo with the fetch repo details from github
create_bitbucket_repo(BITBUCKET_WORKSPACE, REPO_NAMES, BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD, is_private=True)


def mirror_repo_via_ssh(github_ssh_url, bitbucket_ssh_url):

    # Create a temporary directory for the mirrored clone
    temp_dir = tempfile.mkdtemp()
    logging.info(f"📁 Created temporary directory: {temp_dir}")

    try:
        safe_github_url = github_ssh_url.replace(GITHUB_TOKEN, "****")
        safe_bitbucket_url = bitbucket_ssh_url.replace(BITBUCKET_APP_PASSWORD, "****")

        logging.info(f"🔁 Cloning from GitHub via SSH: {safe_github_url}")
        print(f"🔁 Cloning from GitHub via SSH: {safe_github_url}")

        # Clone the GitHub repo as a mirror (includes all refs)
        repo = git.Repo.clone_from(github_ssh_url, temp_dir, mirror=True)
        logging.info(f"🔗 Adding Bitbucket remote: {safe_bitbucket_url}")

        # Add Bitbucket as a remote
        print(f"🔗 Adding Bitbucket remote: {safe_bitbucket_url}")
        logging.info("📤 Pushing all refs to Bitbucket...")
        repo.create_remote('bitbucket', bitbucket_ssh_url)

        logging.info("✅ Repository mirrored successfully from GitHub to Bitbucket.")

        # Push all refs (branches, tags, etc.) to Bitbucket
        print("📤 Pushing all refs to Bitbucket...")
        repo.remotes.bitbucket.push(mirror=True, force=True)
        time.sleep(1)

        print("✅ Repository mirrored successfully from GitHub to Bitbucket.")

    except Exception as e:
        logging.error(f"❌ Error during mirroring: {e}", exc_info=True)

    finally:
        # Cleanup temp directory
        shutil.rmtree(temp_dir)
        print("🧹 Temporary files cleaned up.")


# check for new commits in both GitHub and bitbucket
def get_latest_commit_sha_from_url(git_url):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = git.Repo.clone_from(git_url, tmpdir)
            return repo.head.commit.hexsha
    except Exception as e:
        logging.warning(f"Could not fetch commit SHA from {git_url}: {e}")
        return None
            

# check if repo is empty or already contains data and proceed accordingly
def is_bitbucket_repo_empty_api(workspace, repo_slugs, username, app_password):

    empty_status = {}

    for slug in repo_slugs:
        url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{slug}/commits"
        try:
            response = requests.get(url, auth=(username, app_password))
            if response.status_code == 200:
                data = response.json()
                empty_status[slug] = len(data.get("values", [])) == 0
            else:
                # If repo doesn't exist or some error, assume it's empty
                empty_status[slug] = True
        except Exception:
            empty_status[slug] = True

    return empty_status


repo_status_map = is_bitbucket_repo_empty_api(
    BITBUCKET_WORKSPACE,
    [repo.lower() for repo in REPO_NAMES],
    BITBUCKET_USERNAME,
    BITBUCKET_APP_PASSWORD
)

for repo in REPO_NAMES:
    repo_name = repo
    bitbucket_repo_name = repo_name.lower()

    github_ssh_url = f"https://{GITHUB_USER}:{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{repo_name}.git"

    bitbucket_ssh_url = f"https://{BITBUCKET_USERNAME}:{BITBUCKET_APP_PASSWORD}@bitbucket.org/{BITBUCKET_WORKSPACE}/{bitbucket_repo_name}.git"
    github_sha = get_latest_commit_sha_from_url(github_ssh_url)
    bitbucket_sha = get_latest_commit_sha_from_url(bitbucket_ssh_url)
    
    if repo_status_map.get(bitbucket_repo_name, True):  # True means it's empty
        print(f"🚀 Pushing {repo_name} to Bitbucket (empty repo)...")
        mirror_repo_via_ssh(github_ssh_url, bitbucket_ssh_url)  # ✅ inside loop

    elif github_sha != bitbucket_sha:
        print(f"🗂️New file {repo_name} detected, hence mirroring the file")
        mirror_repo_via_ssh(github_ssh_url, bitbucket_ssh_url)  # ✅ inside loop

    else:
        print(f"⏭️ Skipping {repo_name}: Bitbucket repo already has data.")






