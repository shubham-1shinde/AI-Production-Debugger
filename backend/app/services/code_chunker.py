from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    Language
)


LANGUAGE_MAP = {

    ".py": Language.PYTHON,

    ".js": Language.JS,
    ".jsx": Language.JS,

    ".ts": Language.TS,
    ".tsx": Language.TS,

    ".java": Language.JAVA,

    ".cpp": Language.CPP,
    ".c": Language.C,

    ".go": Language.GO,

    ".rs": Language.RUST,

    ".php": Language.PHP,

    ".rb": Language.RUBY,

    ".swift": Language.SWIFT,

    ".kt": Language.KOTLIN,
}


def get_splitter(extension: str):

    language = LANGUAGE_MAP.get(
        extension.lower()
    )

    if language:

        return RecursiveCharacterTextSplitter.from_language(
            language=language,
            chunk_size=1500,
            chunk_overlap=200
        )

    return RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200
    )


def chunk_file(
    file_path: str,
    content: str,
    file_hash: str,
    commit: str
):
    extension = Path(file_path).suffix.lower()

    normalized_path = file_path.replace("\\", "/")

    document = Document(
        page_content=content,
        metadata={
            "path": normalized_path,
            "file_hash": file_hash,
            "commit": commit,
            "extension": extension
        }
    )

    splitter = get_splitter(extension)

    return splitter.split_documents(
        [document]
    )