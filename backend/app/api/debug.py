from fastapi import APIRouter, HTTPException
from models.debug_models import DebugRequest
from services.indexing import index_project
from services.chain import get_main_chain

router = APIRouter()

@router.post("/debug")
def debug(request: DebugRequest):

    try:
        print("\n==============================")
        print("NEW DEBUG REQUEST")
        print("==============================")
        print("\nRepository:")
        print(request.repo)
        print("\nBranch:")
        print(request.branch)
        print("\nActive File:")
        print(request.activeFile)
        print("\nActive Code:")
        print(request.activeCode)
        print("\nError:")
        print(request.errorMessage)
        print("\nTerminal Logs:")
        print(request.terminalLogs)
        print("\nDiagnostics:")
        print(request.diagnostics)
        
        index_result = index_project(
            repo=request.repo,
            branch=request.branch
        )

        debug_input = {
            "errorMessage":
                request.errorMessage,
            "terminalLogs":
                request.terminalLogs,
            "workspacePath":
                request.workspacePath,
            "activeFile":
                request.activeFile,
            "activeCode":
                request.activeCode,
            "diagnostics":
                [
                    diagnostic.model_dump()
                    for diagnostic
                    in request.diagnostics
                ]
        }

        answer = (get_main_chain().invoke(debug_input).model_dump())

        return {
            "success": True,
            "index":
                index_result,
            "answer":
                answer
        }

    except Exception as e:
        print(f"Debug request failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )