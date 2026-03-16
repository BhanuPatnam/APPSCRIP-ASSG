from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

# In-memory session store
# { user_id: { session_data } }
sessions: Dict[str, Dict[str, Any]] = {}

def get_session(user_id: str) -> Dict[str, Any]:
    if user_id not in sessions:
        sessions[user_id] = {
            "session_start": datetime.now(timezone.utc),
            "requests_made": 0,
            "sectors_queried": [],
            "last_request": datetime.now(timezone.utc),
            "rate_limit_hits": 0,
            "query_history": []
        }
    return sessions[user_id]

def update_session_request(user_id: str, sector: str, cached: bool, duration_ms: int):
    session = get_session(user_id)
    session["requests_made"] += 1
    session["last_request"] = datetime.now(timezone.utc)
    
    if sector not in session["sectors_queried"]:
        session["sectors_queried"].append(sector)
        
    session["query_history"].append({
        "sector": sector,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cached": cached,
        "duration_ms": duration_ms
    })
    
    # Keep history manageable
    if len(session["query_history"]) > 50:
        session["query_history"].pop(0)

def record_rate_limit_hit(user_id: str):
    session = get_session(user_id)
    session["rate_limit_hits"] += 1

def cleanup_sessions():
    now = datetime.now(timezone.utc)
    expired_users = [
        user_id for user_id, session in sessions.items()
        if (now - session["session_start"]) > timedelta(hours=2)
    ]
    for user_id in expired_users:
        logger.info(f"Cleaning up expired session for user: {user_id}")
        del sessions[user_id]
