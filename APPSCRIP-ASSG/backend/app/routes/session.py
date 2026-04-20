from fastapi import APIRouter, Depends, Request
from app.auth import get_current_user
from app.models import User, SessionStats, SessionQuery
from app.session_manager import get_session
from app.cache import get_cache_stats
from app.rate_limiter import limiter

router = APIRouter()

@router.get("/stats", response_model=SessionStats)
@limiter.limit("20/minute")
async def get_session_stats(request: Request, current_user: User = Depends(get_current_user)):
    session = get_session(current_user.username)
    return {
        "requests_made": session["requests_made"],
        "sectors_queried": session["sectors_queried"],
        "rate_limit_remaining": 5, # Placeholder, actual rate limit is handled by slowapi
        "session_start": session["session_start"],
        "rate_limit_hits": session["rate_limit_hits"],
        "cache_stats": get_cache_stats()
    }

@router.get("/history", response_model=list[SessionQuery])
@limiter.limit("20/minute")
async def get_session_history(request: Request, current_user: User = Depends(get_current_user)):
    session = get_session(current_user.username)
    return session["query_history"]
