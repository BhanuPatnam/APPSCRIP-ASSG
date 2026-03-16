from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import logging
from backend.config import settings

logger = logging.getLogger(__name__)

# In-memory cache for reports
# { sector_key: { report, timestamp } }
report_cache: Dict[str, Dict[str, Any]] = {}

def get_cache_key(sector: str) -> str:
    return sector.lower().strip().replace(" ", "_")

def get_cached_report(sector: str) -> Optional[Dict[str, Any]]:
    key = get_cache_key(sector)
    if key in report_cache:
        entry = report_cache[key]
        now = datetime.now(timezone.utc)
        ttl = timedelta(minutes=settings.CACHE_TTL_MINUTES)
        
        if (now - entry["timestamp"]) < ttl:
            logger.info(f"Cache hit for sector: {sector}")
            return entry["report"]
        else:
            logger.info(f"Cache expired for sector: {sector}")
            del report_cache[key]
            
    return None

def set_cached_report(sector: str, report: Dict[str, Any]):
    key = get_cache_key(sector)
    
    # Eviction policy: oldest on overflow
    if len(report_cache) >= 50:
        oldest_key = min(report_cache.keys(), key=lambda k: report_cache[k]["timestamp"])
        logger.info(f"Evicting oldest cache entry: {oldest_key}")
        del report_cache[oldest_key]
        
    report_cache[key] = {
        "report": report,
        "timestamp": datetime.now(timezone.utc)
    }
    logger.info(f"Cached report for sector: {sector}")

def get_cache_stats() -> Dict[str, Any]:
    return {
        "size": len(report_cache),
        "max_size": 50,
        "ttl_minutes": settings.CACHE_TTL_MINUTES
    }
