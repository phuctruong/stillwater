"""
VSCode Integration Routes

Provides endpoints for opening files in VSCode editor.

Rung Target: 641
Version: 1.0.0
"""

import subprocess
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["vscode"])


class VSCodeRequest(BaseModel):
    """Request to open a file in VSCode"""
    file: str = Field(..., description="File path relative to repo root")


class VSCodeResponse(BaseModel):
    """Response from VSCode operation"""
    success: bool
    message: str
    file_path: str = None


@router.post("/vscode/open", response_model=VSCodeResponse)
async def open_in_vscode(request: VSCodeRequest, repo_root: Path = None):
    """
    Open a file in VSCode.

    Args:
        request: Contains file path relative to repo root
        repo_root: Absolute path to repo root (injected from dependency)

    Returns:
        VSCodeResponse with success status and message
    """
    try:
        if not repo_root:
            repo_root = Path(__file__).parent.parent.parent

        file_path = repo_root / request.file

        # Security: ensure path is within repo
        try:
            file_path_resolved = file_path.resolve()
            repo_root_resolved = repo_root.resolve()
            if not str(file_path_resolved).startswith(str(repo_root_resolved)):
                raise HTTPException(
                    status_code=403,
                    detail="Access denied: path outside repository"
                )
        except (ValueError, OSError):
            raise HTTPException(
                status_code=400,
                detail="Invalid file path"
            )

        # Attempt to open in VSCode
        try:
            subprocess.Popen(["code", str(file_path)])
            return VSCodeResponse(
                success=True,
                message=f"Opening {request.file} in VSCode",
                file_path=str(file_path)
            )
        except FileNotFoundError:
            # VSCode not in PATH - return success with message
            logger.info(f"VSCode not in PATH. Returning file path: {file_path}")
            return VSCodeResponse(
                success=True,
                message=f"VSCode not found in PATH. File ready: {file_path}",
                file_path=str(file_path)
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error opening VSCode: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error opening file: {str(e)}"
        )
