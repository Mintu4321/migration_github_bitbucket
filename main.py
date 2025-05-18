import os
import shutil
import time

import git  # GitPython
import tempfile
import logging
from fetch_gitRep import get_all_repos
from create_repo import create_bitbucket_repo


BITBUCKET_USERNAME = "maxbasumatary-admin"  # Not your email
BITBUCKET_APP_PASSWORD = os.getenv("PASSWORD")
BITBUCKET_WORKSPACE = "maxbasumatary"  # Often same as your username


REPO_NAMES = get_all_repos()

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("repo_migration.log"),
            logging.StreamHandler()
        ]
    )

BITBUCKET_USER = "maxbasumatary"
GITHUB_USER = "Mintu4321"

# Create bitbucket repo
create_bitbucket_repo(BITBUCKET_WORKSPACE, REPO_NAMES, BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD, is_private=True)

def mirror_repo_via_ssh(github_ssh_url, bitbucket_ssh_url):

    # Create a temporary directory for the mirrored clone
    temp_dir = tempfile.mkdtemp()
    logging.info(f"📁 Created temporary directory: {temp_dir}")

    try:
        logging.info(f"🔁 Cloning from GitHub via SSH: {github_ssh_url}")
        print(f"🔁 Cloning from GitHub via SSH: {github_ssh_url}")
        # Clone the GitHub repo as a mirror (includes all refs)
        repo = git.Repo.clone_from(github_ssh_url, temp_dir, mirror=True)
        logging.info(f"🔗 Adding Bitbucket remote: {bitbucket_ssh_url}")

        # Add Bitbucket as a remote
        print(f"🔗 Adding Bitbucket remote: {bitbucket_ssh_url}")
        logging.info("📤 Pushing all refs to Bitbucket...")
        repo.create_remote('bitbucket', bitbucket_ssh_url)

        logging.info("✅ Repository mirrored successfully from GitHub to Bitbucket.")


        # Push all refs (branches, tags, etc.) to Bitbucket
        print("📤 Pushing all refs to Bitbucket...")
        repo.remotes.bitbucket.push(mirror=True, force=True)
        time.sleep(3)


        print("✅ Repository mirrored successfully from GitHub to Bitbucket.")

    except Exception as e:
        logging.error(f"❌ Error during mirroring: {e}", exc_info=True)

    finally:
        # Cleanup temp directory
        shutil.rmtree(temp_dir)
        print("🧹 Temporary files cleaned up.")


# for bitbucket_repo, github_repo in REPOS_TO_MIRROR:



for repo in REPO_NAMES:
    repo_name = repo
    bitbucket_repo_name = repo_name.lower()

    github_ssh_url = f"git@github.com:{GITHUB_USER}/{repo_name}.git"
    bitbucket_ssh_url = f"git@bitbucket.org:{BITBUCKET_USER}/{bitbucket_repo_name}.git"

    mirror_repo_via_ssh(github_ssh_url, bitbucket_ssh_url)  # ✅ inside loop
