from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from api.debug import router


app = FastAPI(
    title="AI Production Debugger",
    version="1.0.0"
)


app.include_router(
    router,
    prefix="/api"
)


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "AI Production Debugger"
    }

# from services.indexing import index_project
# from services.chain import get_main_chain
# from dotenv import load_dotenv

# load_dotenv()

# GITHUB_REPO = "shubham-1shinde/gstassistant"
# GITHUB_BRANCH = "main"

# print("\nStarting project indexing...\n")

# index_result = index_project(
#     repo=GITHUB_REPO,
#     branch=GITHUB_BRANCH
# )


# print("\nIndex Result:")

# print(index_result)

# errorMessage = """
# TypeError: Cannot read properties of undefined (reading 'calculateGST')

# The error occurs when calculateGST() is called while generating
# the GST calculation result.
# """


# print("\nRunning AI debugger...\n")

# answer = get_main_chain().invoke(errorMessage)

# print("\nFinal Answer:")

# print(answer)


# from services.chain import get_main_chain

# errorMessage = """
# TypeError: Cannot read properties of undefined (reading 'calculateGST')

# The error occurs when calculateGST() is called while generating
# the GST calculation result.
# """

# answer = get_main_chain().invoke(errorMessage)

# print("\nFinal Answer:")
# print(answer)


# from fastapi import FastAPI

# from api.debug import router as debug_router


# app = FastAPI(
#     title="AI Production Debugger",
#     version="1.0.0"
# )

# app.include_router(debug_router)


# @app.get("/")
# def root():
#     return {
#         "message": "AI Production Debugger API is running"
#     }







# import os
# from pathlib import Path
# from functools import lru_cache
# from services.chain import get_main_chain
# from langchain_community.document_loaders import GithubFileLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_qdrant import QdrantVectorStore
# from qdrant_client import QdrantClient
# from langchain_core.prompts import PromptTemplate
# from langchain_core.runnables import (
#     RunnableParallel,
#     RunnablePassthrough,
#     RunnableLambda,
# )
# from langchain_core.output_parsers import StrOutputParser
# from dotenv import load_dotenv

# load_dotenv()


# try:
#     loader = GithubFileLoader(
#         repo="shubham-1shinde/gstassistant",
#         branch="main",
#         access_token=os.getenv("GITHUB_TOKEN"),
#         github_api_url="https://api.github.com",

#         # Load only source-code files
#         file_filter=lambda path: path.endswith(
#             (".py", ".js", ".ts", ".jsx", ".tsx")
#         )
#     )

#     documents = list(loader.lazy_load())

#     print("Repo fetched successfully.")

# except Exception as e:
#     print("Error fetching Repo:", e)
#     raise SystemExit

# LANGUAGE_MAP = {
#     ".py": Language.PYTHON,
#     ".js": Language.JS,
#     ".ts": Language.TS,
#     ".tsx": Language.TS,
#     ".jsx": Language.JS,
#     ".java": Language.JAVA,
#     ".cpp": Language.CPP,
#     ".c": Language.C,
# }

# # Cache splitters so they are not recreated for every file
# @lru_cache(maxsize=None)
# def get_splitter(extension: str):

#     language = LANGUAGE_MAP.get(extension)

#     if language:
#         return RecursiveCharacterTextSplitter.from_language(
#             language=language,
#             chunk_size=1500,
#             chunk_overlap=200,
#         )

#     return RecursiveCharacterTextSplitter(
#         chunk_size=1500,
#         chunk_overlap=200,
#     )


# all_chunks = []

# for doc in documents:

#     file_path = doc.metadata.get("path", "")
#     extension = Path(file_path).suffix.lower()

#     splitter = get_splitter(extension)

#     chunks = splitter.split_documents([doc])

#     all_chunks.extend(chunks)


# print(f"Total chunks created: {len(all_chunks)}")

# print("\nCreating embeddings...")

# embeddings = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )

# print("Creating Qdrant vector store...")


# vector_store = QdrantVectorStore.from_documents(
#     documents=all_chunks,
#     embedding=embeddings,
#     path="./qdrant_data",
#     collection_name="gstassistant_code",
# )

# print("Qdrant vector store created successfully.")

# retriever = vector_store.as_retriever(
#     search_kwargs={"k": 5}
# )



# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0.2
# )

# prompt = PromptTemplate(
#     template="""
# You are an AI Production Debugger.

# Your job is to analyze a software error using ONLY the provided
# error information and retrieved code context from the user's repository.

# Do NOT invent code, files, variables, functions, or causes that are not
# supported by the provided context.

# Analyze the problem in the following order:

# 1. Identify the error.
# 2. Find the most likely root cause from the provided code.
# 3. Mention the exact file and relevant code section.
# 4. Explain why the error occurs.
# 5. Provide a minimal and specific fix.
# 6. If the context is insufficient, clearly say:
#    "I don't have enough code context to determine the root cause."

# Error:
# {errorMessage}

# Retrieved Repository Context:
# {context}

# Return the answer in this format:

# Error:
# <error name/message>

# Root Cause:
# <root cause>

# File:
# <file path>

# Explanation:
# <why the error happens>

# Suggested Fix:
# <corrected code or specific change>

# Confidence:
# <High / Medium / Low>
# """,
#     input_variables=["context", "errorMessage"]
# )

# def format_docs(retrieved_docs):
#     """
#     Convert a list of LangChain Documents
#     into one string.
#     """

#     return "\n\n".join(
#         doc.page_content
#         for doc in retrieved_docs
#     )
    
# parser = StrOutputParser()

# parallel_chain = RunnableParallel(
#     {
#         "context": retriever | RunnableLambda(format_docs),
#         "errorMessage": RunnablePassthrough(),
#     }
# )

# main_chain = (parallel_chain | prompt | llm | parser)
