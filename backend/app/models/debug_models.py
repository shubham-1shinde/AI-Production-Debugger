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


class DebugResult(BaseModel):

    error: str

    rootCause: str

    evidence: List[str] = Field(
        default_factory=list
    )

    solution: str

    filesToChange: List[str] = Field(
        default_factory=list
    )

    fix: str

    verification: List[str] = Field(
        default_factory=list
    )