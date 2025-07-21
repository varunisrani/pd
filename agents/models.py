"""Pydantic models for structured data validation."""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class SearchResult(BaseModel):
    """Individual search result from Brave API."""
    title: str
    url: str
    description: str
    score: Optional[float] = None


class ResearchSummary(BaseModel):
    """Summarized research findings."""
    query: str
    results: List[SearchResult]
    summary: str
    key_insights: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)


class EmailDraft(BaseModel):
    """Email draft structure."""
    to: List[EmailStr] = Field(min_length=1)
    subject: str
    body: str
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None


class SearchQuery(BaseModel):
    """Validated search query parameters."""
    query: str = Field(min_length=1, max_length=500)
    max_results: int = Field(default=10, ge=1, le=50)