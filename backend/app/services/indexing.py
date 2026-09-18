from pathlib import Path
from .github_service import get_branch_commit, download_repository, extract_repository_files
from .file_hasher import get_file_hash
from .code_chunker import chunk_file
from .index_metadata import load_metadata, save_metadata
from .qdrant_service import add_documents, delete_file_vectors

SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
}

def is_supported_file(path: str) -> bool:
    return (
        Path(path)
        .suffix
        .lower()
        in SUPPORTED_EXTENSIONS
    )


def index_project(repo: str, branch: str):

    print("\nStarting project indexing...\n")

    metadata = load_metadata()

    print(f"Repository: {repo}")

    print(f"Branch: {branch}")


    current_commit = get_branch_commit(
        repo,
        branch
    )

    print(f"Current commit: {current_commit}")


    if (
        metadata.get("indexed")
        and metadata.get("repo") == repo
        and metadata.get("branch") == branch
        and metadata.get("commit") == current_commit
    ):

        print("\nProject already indexed.")

        print("No changes detected.")

        print("Skipping indexing.\n")

        return {
            "status": "unchanged",
            "message": "Project already indexed.",
            "commit": current_commit,
        }


    zip_file = download_repository(
        repo,
        current_commit
    )

    current_files = extract_repository_files(zip_file)
    zip_file.close()


    current_files = {
        path: content

        for path, content
        in current_files.items()

        if is_supported_file(path)
    }

    print(
        f"\nSupported files found: "
        f"{len(current_files)}"
    )


    old_files = metadata.get("files", {})

    changed_files = []
    deleted_files = []


    for path, content in current_files.items():

        file_hash = get_file_hash(content)

        old_file = old_files.get(path)

        if old_file is None:

            changed_files.append((
                path,
                content,
                file_hash,
                "added"
            ))

        elif (
            old_file.get("file_hash")
            != file_hash
        ):

            changed_files.append((
                path,
                content,
                file_hash,
                "modified"
            ))


    for path in old_files:
        if path not in current_files:
            deleted_files.append(path)

    print(
        f"Changed files: "
        f"{len(changed_files)}"
    )

    print(
        f"Deleted files: "
        f"{len(deleted_files)}"
    )


    if (
        not changed_files
        and not deleted_files
    ):

        metadata["repo"] = repo
        metadata["branch"] = branch
        metadata["commit"] = current_commit
        metadata["indexed"] = True
        save_metadata(metadata)

        print(
            "\nCommit changed but no "
            "supported source files changed."
        )

        return {
            "status": "unchanged_source",
            "commit": current_commit,
        }


    files_to_delete = {
        path
        for path, _, _, _
        in changed_files
    }

    files_to_delete.update(deleted_files)

    for path in files_to_delete:

        print(f"Removing old vectors: {path}")
        delete_file_vectors(path, repo)


    all_chunks = []

    for (path, content, file_hash, change_type) in changed_files:

        print(
            f"\nProcessing "
            f"{change_type}: {path}"
        )

        chunks = chunk_file(
            file_path=path,
            content=content,
            file_hash=file_hash,
            commit=current_commit
        )

        print(f"Created {len(chunks)} chunks")
        all_chunks.extend(chunks)

    if all_chunks:

        print(
            f"\nCreating embeddings "
            f"for {len(all_chunks)} chunks..."
        )

        add_documents(all_chunks, repo)
        print("Embeddings added to Qdrant.")

    new_file_metadata = {}

    for path, content in current_files.items():

        file_hash = get_file_hash(content)
        
        new_file_metadata[path] = {
            "file_hash": file_hash,
            "commit": current_commit,
        }

    metadata = {
        "indexed": True,
        "repo": repo,
        "branch": branch,
        "commit": current_commit,
        "files": new_file_metadata,
    }

    save_metadata(metadata)
    print("\nIndexing completed successfully.")

    return {
        "status": "updated",
        "commit": current_commit,
        "changed_files": len(changed_files),
        "deleted_files": len(deleted_files),
        "chunks": len(all_chunks),
    }