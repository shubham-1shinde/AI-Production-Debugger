import os
import io
import zipfile
import requests


GITHUB_API = "https://api.github.com"


def get_headers():

    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def get_branch_commit(repo, branch):

    url = (
        f"{GITHUB_API}/repos/"
        f"{repo}/commits/{branch}"
    )

    response = requests.get(
        url,
        headers=get_headers(),
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    return data["sha"]


def download_repository(repo, commit_sha):

    print("\nDownloading repository archive...")

    url = (
        f"{GITHUB_API}/repos/"
        f"{repo}/zipball/{commit_sha}"
    )

    response = requests.get(
        url,
        headers=get_headers(),
        timeout=120
    )

    response.raise_for_status()
    print("Repository archive downloaded.")

    return zipfile.ZipFile(io.BytesIO(response.content))


def extract_repository_files(zip_file):

    files = {}
    names = zip_file.namelist()

    for name in names:

        # Ignore directories
        if name.endswith("/"):
            continue

        # GitHub ZIP contains a
        # root directory such as:
        #
        # shubham-1shinde-gstassistant-xxxx/

        parts = name.split("/", 1)

        if len(parts) != 2:
            continue

        relative_path = parts[1]

        try:
            content = zip_file.read(name).decode("utf-8", errors="ignore")

        except Exception:
            continue

        files[relative_path] = content

    return files