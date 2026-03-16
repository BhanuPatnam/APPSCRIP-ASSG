from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
import re

class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class SectorAnalysisRequest(BaseModel):
    sector: str = Field(..., min_length=2, max_length=60)

    @validator("sector")
    def validate_sector(cls, v):
        if not re.match(r"^[a-zA-Z\s\-]+$", v):
            raise ValueError("Sector must only contain letters, spaces, and hyphens")
        # Basic check for common injections or scripts (though regex helps)
        if any(tag in v.lower() for tag in ["<script", "select ", "drop ", "insert "]):
            raise ValueError("Invalid characters detected")
        return v.strip()

class ScrapedSource(BaseModel):
    title: str
    url: Optional[str] = None
    snippet: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None

class ScraperOutput(BaseModel):
    sector: str
    scraped_at: datetime
    sources: Dict[str, Any]
    total_sources: int
    raw_text_combined: str

class AnalysisReport(BaseModel):
    sector: str
    report_markdown: str
    timestamp: datetime
    source_count: int
    cached: bool = False

class SessionQuery(BaseModel):
    sector: str
    timestamp: datetime
    cached: bool
    duration_ms: int

class SessionStats(BaseModel):
    requests_made: int
    sectors_queried: List[str]
    rate_limit_remaining: int
    session_start: datetime
    rate_limit_hits: int = 0
    cache_stats: Dict[str, Any] = {}
