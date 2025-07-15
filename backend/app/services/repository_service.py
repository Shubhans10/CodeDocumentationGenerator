import os
import uuid
import shutil
import git
from fastapi import UploadFile
from typing import Optional, Dict, Any
import asyncio
import logging

from app.core.config import settings
from app.models.repository import RepositorySource, RepositoryStatus, RepositoryResponse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for repository status (in a real app, use a database)
repository_status: Dict[str, Dict[str, Any]] = {}

async def clone_github_repository(url: str, branch: Optional[str] = None) -> RepositoryResponse:
    """
    Clone a GitHub repository and return its details.
    """
    repo_id = str(uuid.uuid4())
    repo_path = os.path.join(settings.REPO_STORAGE_DIR, repo_id)

    # Create directory if it doesn't exist
    os.makedirs(settings.REPO_STORAGE_DIR, exist_ok=True)

    # Update status to pending
    repository_status[repo_id] = {
        "status": RepositoryStatus.PENDING,
        "progress": 0.0,
        "message": "Repository cloning initiated"
    }

    try:
        # Start cloning in a background task
        asyncio.create_task(
            _clone_repository_task(repo_id, url, repo_path, branch)
        )

        return RepositoryResponse(
            id=repo_id,
            source=RepositorySource.GITHUB,
            url=url,
            branch=branch,
            status=RepositoryStatus.PENDING,
            message="Repository cloning initiated"
        )
    except Exception as e:
        logger.error(f"Error initiating repository clone: {str(e)}")
        repository_status[repo_id] = {
            "status": RepositoryStatus.FAILED,
            "progress": 0.0,
            "message": f"Failed to initiate repository clone: {str(e)}"
        }
        return RepositoryResponse(
            id=repo_id,
            source=RepositorySource.GITHUB,
            url=url,
            branch=branch,
            status=RepositoryStatus.FAILED,
            message=f"Failed to initiate repository clone: {str(e)}"
        )

async def save_uploaded_repository(file: UploadFile) -> RepositoryResponse:
    """
    Save an uploaded repository file and return its details.
    """
    repo_id = str(uuid.uuid4())
    repo_path = os.path.join(settings.REPO_STORAGE_DIR, repo_id)
    zip_path = f"{repo_path}.zip"

    # Create directory if it doesn't exist
    os.makedirs(settings.REPO_STORAGE_DIR, exist_ok=True)

    # Update status to pending
    repository_status[repo_id] = {
        "status": RepositoryStatus.PENDING,
        "progress": 0.0,
        "message": "Repository upload initiated"
    }

    try:
        # Start processing in a background task
        asyncio.create_task(
            _process_uploaded_file_task(repo_id, file, zip_path, repo_path)
        )

        return RepositoryResponse(
            id=repo_id,
            source=RepositorySource.FILE_UPLOAD,
            status=RepositoryStatus.PENDING,
            message="Repository upload initiated"
        )
    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        repository_status[repo_id] = {
            "status": RepositoryStatus.FAILED,
            "progress": 0.0,
            "message": f"Failed to process uploaded file: {str(e)}"
        }
        return RepositoryResponse(
            id=repo_id,
            source=RepositorySource.FILE_UPLOAD,
            status=RepositoryStatus.FAILED,
            message=f"Failed to process uploaded file: {str(e)}"
        )

async def get_repository_status(repo_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the current status of a repository.
    """
    # First check if the status is in memory
    status = repository_status.get(repo_id)
    if status:
        return status

    # If not in memory (e.g., after server restart), check if the repository directory exists
    repo_path = os.path.join(settings.REPO_STORAGE_DIR, repo_id)
    if os.path.exists(repo_path):
        # Check if documentation has been generated
        doc_path = os.path.join(repo_path, "documentation", "documentation.json")
        if os.path.exists(doc_path):
            # Documentation has been generated, return completed status
            return {
                "status": RepositoryStatus.COMPLETED,
                "progress": 1.0,
                "message": "Documentation generated successfully"
            }
        else:
            # Repository exists but documentation not generated, return processing status
            return {
                "status": RepositoryStatus.PROCESSING,
                "progress": 0.5,
                "message": "Processing repository..."
            }

    # Repository not found
    return None

# Background tasks
async def _clone_repository_task(repo_id: str, url: str, repo_path: str, branch: Optional[str] = None):
    """
    Background task to clone a repository.
    """
    try:
        # Update status to processing
        repository_status[repo_id] = {
            "status": RepositoryStatus.PROCESSING,
            "progress": 0.1,
            "message": "Cloning repository..."
        }

        # Clone the repository
        if branch:
            git.Repo.clone_from(url, repo_path, branch=branch)
        else:
            git.Repo.clone_from(url, repo_path)

        # Update status
        repository_status[repo_id] = {
            "status": RepositoryStatus.PROCESSING,
            "progress": 0.2,
            "message": "Repository cloned, starting documentation generation..."
        }

        # Process the repository with documentation service
        from app.services.documentation_service import documentation_service
        await documentation_service.process_repository(repo_id, repo_path)

    except Exception as e:
        logger.error(f"Error cloning repository: {str(e)}")
        repository_status[repo_id] = {
            "status": RepositoryStatus.FAILED,
            "progress": 0.0,
            "message": f"Failed to clone repository: {str(e)}"
        }
        # Clean up
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)

async def _process_uploaded_file_task(repo_id: str, file: UploadFile, zip_path: str, repo_path: str):
    """
    Background task to process an uploaded repository file.
    """
    try:
        # Update status to processing
        repository_status[repo_id] = {
            "status": RepositoryStatus.PROCESSING,
            "progress": 0.1,
            "message": "Processing uploaded file..."
        }

        # Save the uploaded file
        with open(zip_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Extract the zip file
        # Note: In a real implementation, you would use a library like zipfile to extract the contents
        # For now, we'll just simulate the process
        os.makedirs(repo_path, exist_ok=True)

        # Update progress
        repository_status[repo_id] = {
            "status": RepositoryStatus.PROCESSING,
            "progress": 0.5,
            "message": "Extracting repository..."
        }

        # Simulate extraction delay
        await asyncio.sleep(1)

        # Update status
        repository_status[repo_id] = {
            "status": RepositoryStatus.PROCESSING,
            "progress": 0.6,
            "message": "Repository extracted, starting documentation generation..."
        }

        # Process the repository with documentation service
        from app.services.documentation_service import documentation_service
        await documentation_service.process_repository(repo_id, repo_path)

    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        repository_status[repo_id] = {
            "status": RepositoryStatus.FAILED,
            "progress": 0.0,
            "message": f"Failed to process uploaded file: {str(e)}"
        }
        # Clean up
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
