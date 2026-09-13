import os
from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda,
)
from langchain_core.output_parsers import StrOutputParser

from .qdrant_service import (
    get_documents_by_file,
    get_semantic_documents,
)


def format_docs(documents):
    if not documents:
        return "NO_REPOSITORY_CONTEXT"

    formatted = []

    seen = set()

    for i, doc in enumerate(documents, 1):

        path = doc.metadata.get(
            "path",
            "UNKNOWN_FILE"
        )

        chunk_id = (
            path,
            doc.page_content
        )

        if chunk_id in seen:
            continue

        seen.add(chunk_id)

        formatted.append(
            f"""
--- RETRIEVED CHUNK {i} ---

FILE:
{path}

CODE:
{doc.page_content}

--- END CHUNK ---
"""
        )

    if not formatted:
        return "NO_REPOSITORY_CONTEXT"

    return "\n".join(formatted)


def retrieve_context(data):
    """
    Retrieval pipeline:

    1. Exact active-file retrieval
    2. Semantic retrieval using error + active code
    3. Merge and deduplicate
    """

    error_message = data.get(
        "errorMessage",
        ""
    )

    active_file = data.get(
        "activeFile",
        ""
    )

    active_code = data.get(
        "activeCode",
        ""
    )

    terminal_logs = data.get(
        "terminalLogs",
        ""
    )

    diagnostics = data.get(
        "diagnostics",
        []
    )

    # ---------------------------------
    # 1. EXACT ACTIVE FILE RETRIEVAL
    # ---------------------------------

    exact_documents = []

    if active_file:

        exact_documents = (
            get_documents_by_file(
                active_file
            )
        )

    # ---------------------------------
    # 2. SEMANTIC RETRIEVAL
    # ---------------------------------

    semantic_query = f"""
ERROR:
{error_message}

ACTIVE FILE:
{active_file}

ACTIVE CODE:
{active_code}

TERMINAL LOGS:
{terminal_logs}

DIAGNOSTICS:
{diagnostics}
"""

    semantic_documents = (
        get_semantic_documents(
            semantic_query,
            k=8
        )
    )

    # ---------------------------------
    # 3. MERGE + DEDUPLICATE
    # ---------------------------------

    combined_documents = []

    seen = set()

    # Exact file gets priority.
    for doc in exact_documents:

        key = (
            doc.metadata.get(
                "path",
                ""
            ),
            doc.page_content
        )

        if key not in seen:
            seen.add(key)
            combined_documents.append(doc)

    # Then semantic results.
    for doc in semantic_documents:

        key = (
            doc.metadata.get(
                "path",
                ""
            ),
            doc.page_content
        )

        if key not in seen:
            seen.add(key)
            combined_documents.append(doc)

    print(
        "\n================ RETRIEVAL ================"
    )

    print(
        f"Active file: {active_file}"
    )

    print(
        f"Exact chunks: {len(exact_documents)}"
    )

    print(
        f"Semantic chunks: {len(semantic_documents)}"
    )

    print(
        f"Final chunks: {len(combined_documents)}"
    )

    print(
        "============================================\n"
    )

    return {
        "repository_context":
            format_docs(
                combined_documents
            ),

        "errorMessage":
            error_message,

        "activeFile":
            active_file,

        "activeCode":
            active_code,

        "terminalLogs":
            terminal_logs,

        "diagnostics":
            diagnostics,
    }


@lru_cache(maxsize=1)
def get_main_chain():

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        api_key=os.getenv(
            "GOOGLE_API_KEY"
        )
    )

    prompt = PromptTemplate(
        template="""
    You are a production debugging AI.

    Analyze the software error using the repository code
    and debugging information provided below.

    ========================
    IMPORTANT SOURCE RULES
    ========================

    There are TWO different sources of code:

    1. REPOSITORY CODE
    This comes from Qdrant and represents actual code
    retrieved from the indexed repository.

    2. ACTIVE EDITOR CODE
    This is code sent by the VS Code extension from the
    user's currently active editor.

    NEVER assume that ACTIVE EDITOR CODE belongs to the
    REPOSITORY FILE unless the exact same code is present
    in the retrieved repository context.

    Repository evidence has priority when determining what
    actually exists in the indexed project.

    ========================
    ANTI-HALLUCINATION RULES
    ========================

    1. NEVER invent a file path.

    2. NEVER invent a function, method, class, variable,
    module, import, export, or code.

    3. Mention a repository file only if its exact path
    appears in the retrieved repository context.

    4. Mention a function or method only if it actually
    appears in the retrieved repository code.

    5. Do not assume that ACTIVE EDITOR CODE exists in
    the repository.

    6. Do not treat ACTIVE EDITOR CODE as proof of how
    the repository file is implemented.

    7. Do not claim an import/export mismatch unless the
    retrieved repository code proves it.

    8. Do not use general programming knowledge to invent
    missing repository details.

    9. Clearly separate:
    - Repository Facts
    - Active Editor Facts
    - Inference

    10. If the repository does not contain enough evidence
        to prove the root cause, say:

        "Insufficient repository context to determine
        the root cause."

    ========================
    ERROR
    ========================

    {errorMessage}

    ========================
    ACTIVE FILE
    ========================

    {activeFile}

    ========================
    ACTIVE EDITOR CODE
    ========================

    {activeCode}

    ========================
    TERMINAL LOGS
    ========================

    {terminalLogs}

    ========================
    DIAGNOSTICS
    ========================

    {diagnostics}

    ========================
    REPOSITORY CODE
    ========================

    {repository_context}

    ========================
    DEBUGGING PROCESS
    ========================

    Step 1:
    Analyze the exact error message.

    Step 2:
    Inspect the ACTIVE EDITOR CODE separately.

    Step 3:
    Inspect the exact ACTIVE FILE from the repository.

    Step 4:
    Find the identifiers mentioned by the error in the
    repository code.

    Step 5:
    Inspect imports and exports related to those identifiers.

    Step 6:
    Inspect callers and consumers of the relevant service.

    Step 7:
    Determine whether the repository actually proves
    the root cause.

    Step 8:
    Only suggest a fix supported by repository evidence.

    ========================
    OUTPUT FORMAT
    ========================

    Error:
    <exact error>

    Repository Facts:
    <List facts directly visible in repository code>

    Active Editor Facts:
    <List facts directly visible in active editor code>

    Root Cause:
    <proven root cause OR
    "Insufficient repository context to determine the root cause.">

    Relevant Files:
    <List only repository files actually retrieved>

    Explanation:
    <explain using repository evidence>

    Suggested Fix:
    <fix supported by repository evidence OR
    "Insufficient context">

    Confidence:
    <High / Medium / Low>

    IMPORTANT:

    Do not confuse ACTIVE EDITOR CODE with repository code.

    If the active editor code does not match the retrieved
    repository code, explicitly state that difference.

    Do not claim a root cause merely because the active editor
    code contains a problematic-looking line.
    """,
        input_variables=[
            "repository_context",
            "errorMessage",
            "activeFile",
            "activeCode",
            "terminalLogs",
            "diagnostics",
        ],
    )

    retrieval_chain = RunnableLambda(
        retrieve_context
    )

    return (
        retrieval_chain
        | prompt
        | llm
        | StrOutputParser()
    )