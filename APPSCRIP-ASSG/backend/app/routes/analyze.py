from fastapi import APIRouter, Depends, HTTPException, Request
from backend.app.auth import get_current_user
from backend.app.models import User, AnalysisReport, ScraperOutput
from backend.app.scraper import scrape_all
from backend.app.ai_analyzer import generate_report
from backend.app.cache import get_cached_report, set_cached_report
from backend.app.session_manager import update_session_request
from backend.app.rate_limiter import limiter
from datetime import datetime, timezone
import time
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{sector}", response_model=AnalysisReport)
@limiter.limit("5/minute")
async def analyze_sector(request: Request, sector: str, current_user: User = Depends(get_current_user)):
    start_time = time.time()
    
    # Check cache
    cached_report = get_cached_report(sector)
    if cached_report:
        duration_ms = int((time.time() - start_time) * 1000)
        update_session_request(current_user.username, sector, True, duration_ms)
        return cached_report

    # Scrape data
    try:
        scraped_data = await scrape_all(sector)
    except Exception as e:
        logger.error(f"Scraping failed for sector {sector}: {e}")
        raise HTTPException(status_code=500, detail="Failed to collect data for analysis")

    # Generate AI report
    try:
        report_markdown = await generate_report(scraped_data)
    except Exception as e:
        logger.error(f"AI analysis failed for sector {sector}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate analysis report")

    # Create report object
    report = {
        "sector": sector,
        "report_markdown": report_markdown,
        "timestamp": datetime.now(timezone.utc),
        "source_count": scraped_data["total_sources"],
        "cached": False
    }

    # Cache report
    set_cached_report(sector, report)

    # Update session
    duration_ms = int((time.time() - start_time) * 1000)
    update_session_request(current_user.username, sector, False, duration_ms)

    return report
