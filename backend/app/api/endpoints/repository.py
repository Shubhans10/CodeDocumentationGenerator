from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Response
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
import os
import json

from app.models.repository import (
    RepositoryRequest, 
    RepositoryResponse, 
    RepositoryStatusResponse,
    RepositorySource,
    RepositoryStatus
)
from app.services.repository_service import (
    clone_github_repository,
    save_uploaded_repository,
    get_repository_status
)
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=RepositoryResponse)
async def create_repository(repo_request: RepositoryRequest):
    """
    Create a new repository from GitHub URL.
    """
    if repo_request.source == RepositorySource.GITHUB:
        if not repo_request.url:
            raise HTTPException(status_code=400, detail="URL is required for GitHub repositories")
        return await clone_github_repository(str(repo_request.url), repo_request.branch)
    else:
        raise HTTPException(status_code=400, detail="For file uploads, use the /upload endpoint")

@router.post("/upload", response_model=RepositoryResponse)
async def upload_repository(file: UploadFile = File(...)):
    """
    Upload a repository as a zip file.
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only zip files are supported")

    return await save_uploaded_repository(file)

@router.get("/{repo_id}/status", response_model=RepositoryStatusResponse)
async def check_repository_status(repo_id: str):
    """
    Check the status of a repository.
    """
    status = await get_repository_status(repo_id)
    if not status:
        raise HTTPException(status_code=404, detail="Repository not found")

    return RepositoryStatusResponse(
        id=repo_id,
        status=status["status"],
        progress=status["progress"],
        message=status.get("message")
    )

@router.get("/{repo_id}/documentation")
async def get_documentation(repo_id: str):
    """
    Get the generated documentation for a repository.
    """
    # Check if repository exists and is completed
    status = await get_repository_status(repo_id)
    if not status:
        raise HTTPException(status_code=404, detail="Repository not found")

    if status["status"] != RepositoryStatus.COMPLETED:
        raise HTTPException(
            status_code=400, 
            detail=f"Documentation not ready. Current status: {status['status']}"
        )

    # Get the documentation file path
    repo_path = os.path.join(settings.REPO_STORAGE_DIR, repo_id)
    doc_path = os.path.join(repo_path, "documentation", "documentation.json")

    if not os.path.exists(doc_path):
        raise HTTPException(status_code=404, detail="Documentation file not found")

    # Read the documentation file
    try:
        with open(doc_path, 'r') as f:
            documentation = json.load(f)
        return documentation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading documentation: {str(e)}")

@router.get("/{repo_id}/documentation/download")
async def download_documentation(repo_id: str):
    """
    Download the generated documentation for a repository.
    """
    # Check if repository exists and is completed
    status = await get_repository_status(repo_id)
    if not status:
        raise HTTPException(status_code=404, detail="Repository not found")

    if status["status"] != RepositoryStatus.COMPLETED:
        raise HTTPException(
            status_code=400, 
            detail=f"Documentation not ready. Current status: {status['status']}"
        )

    # Get the documentation file path
    repo_path = os.path.join(settings.REPO_STORAGE_DIR, repo_id)
    doc_path = os.path.join(repo_path, "documentation", "documentation.json")

    if not os.path.exists(doc_path):
        raise HTTPException(status_code=404, detail="Documentation file not found")

    # Return the file as a download
    return FileResponse(
        path=doc_path,
        filename="documentation.json",
        media_type="application/json"
    )
