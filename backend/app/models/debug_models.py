from typing import List, Optional

from pydantic import BaseModel, Field


class Diagnostic(BaseModel):
    message: str
    severity: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    source: Optional[str] = None


class DebugRequest(BaseModel):

    repo: str

    branch: str

    errorMessage: str

    terminalLogs: str = ""

    workspacePath: str = ""

    activeFile: str = ""

    activeCode: str = ""

    diagnostics: List[Diagnostic] = Field(
        default_factory=list
    )