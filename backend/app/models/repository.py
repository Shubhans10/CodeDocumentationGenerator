from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List
from enum import Enum

class RepositorySource(str, Enum):
    GITHUB = "github"
    FILE_UPLOAD = "file_upload"

class RepositoryRequest(BaseModel):
    source: RepositorySource
    url: Optional[HttpUrl] = None
    branch: Optional[str] = None
    
    @validator('url')
    def url_required_for_github(cls, v, values):
        if values.get('source') == RepositorySource.GITHUB and not v:
            raise ValueError('URL is required for GitHub repositories')
        return v

class RepositoryResponse(BaseModel):
    id: str
    source: RepositorySource
    url: Optional[str] = None
    branch: Optional[str] = None
    status: str
    message: Optional[str] = None

class RepositoryStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class RepositoryStatusResponse(BaseModel):
    id: str
    status: RepositoryStatus
    progress: float  # 0.0 to 1.0
    message: Optional[str] = None