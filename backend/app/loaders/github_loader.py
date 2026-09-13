import os
from functools import lru_cache
from langchain_community.document_loaders import GithubFileLoader
from dotenv import load_dotenv

load_dotenv()

@lru_cache(maxsize=None)
def get_github_loader():
    try:
        loader = GithubFileLoader(
            repo="shubham-1shinde/gstassistant",
            branch="main",
            access_token=os.getenv("GITHUB_TOKEN"),
            github_api_url="https://api.github.com",

            # Load only source-code files
            file_filter=lambda path: path.endswith(
                (".py", ".js", ".ts", ".jsx", ".tsx")
            )
        )

        documents = list(loader.lazy_load())

        print("Repo fetched successfully.")
        return documents

    except Exception as e:
        print("Error fetching repo:", e)
        raise