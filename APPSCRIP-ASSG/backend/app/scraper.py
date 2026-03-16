import asyncio
import random
import logging
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import feedparser
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
]

async def fetch_with_retry(client: httpx.AsyncClient, url: str) -> Optional[httpx.Response]:
    for attempt in range(2):
        try:
            await asyncio.sleep(random.uniform(1.0, 2.5)) # Slightly longer delay
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
                "Referer": "https://www.google.com/",
            }
            response = await client.get(url, headers=headers, timeout=15, follow_redirects=True)
            if response.status_code == 200:
                return response
            elif response.status_code == 403:
                logger.warning(f"Access forbidden for {url} (403) - Attempt {attempt + 1}")
            elif response.status_code == 429:
                logger.warning(f"Rate limited for {url} (429). Waiting longer...")
                await asyncio.sleep(5 + (attempt * 5))
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
    return None

async def scrape_duckduckgo(sector: str) -> List[Dict[str, str]]:
    results = []
    queries = [
        f"{sector} sector India market size 2024 2025",
        f"{sector} India export opportunities trade",
        f"{sector} India government policy FDI incentives",
        f"{sector} India top companies market share",
    ]
    
    # Increase delay and try to avoid rate limits
    for query in queries:
        try:
            await asyncio.sleep(random.uniform(1.5, 3.0))
            with DDGS() as ddgs:
                # Use a smaller max_results and handle it correctly
                query_results = [r for r in ddgs.text(query, max_results=3)]
                if query_results:
                    for r in query_results:
                        results.append({
                            "title": r.get('title', 'No Title'),
                            "snippet": r.get('body', 'No Snippet'),
                            "url": r.get('href', '')
                        })
        except Exception as e:
            logger.error(f"DuckDuckGo search failed for query '{query}': {e}")
            await asyncio.sleep(2) # Extra delay on error
            
    return results

async def scrape_google_news(sector: str) -> List[Dict[str, str]]:
    url = f"https://news.google.com/rss/search?q={sector}+India+trade&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        async with httpx.AsyncClient() as client:
            response = await fetch_with_retry(client, url)
            if not response:
                return []
            
            # Google News RSS is XML, not HTML, so we use feedparser
            feed = feedparser.parse(response.text)
            news_items = []
            for entry in feed.entries[:8]:
                # Extract clean link if possible (Google News uses redirects)
                news_items.append({
                    "title": entry.get('title', 'No Title'),
                    "description": entry.get('summary', 'No summary available.'),
                    "date": entry.get('published', 'N/A'),
                    "url": entry.get('link', '')
                })
            return news_items
    except Exception as e:
        logger.error(f"Google News RSS scraping failed: {e}")
        return []

async def scrape_economic_times(sector: str, client: httpx.AsyncClient) -> List[Dict[str, str]]:
    # Try different URL patterns
    formatted_sector = sector.replace(' ', '-')
    urls = [
        f"https://economictimes.indiatimes.com/topic/{formatted_sector}",
        f"https://economictimes.indiatimes.com/topic/{sector.replace(' ', '%20')}"
    ]
    
    for url in urls:
        response = await fetch_with_retry(client, url)
        if not response:
            continue
        
        soup = BeautifulSoup(response.text, "html.parser")
        articles = []
        
        # Try multiple selectors as ET changes layout often
        selectors = [
            ".topic_box li", 
            ".st_topic_list li", 
            ".flt.topic_box div.flt",
            "div.topic-list div.item"
        ]
        
        for selector in selectors:
            items = soup.select(selector, limit=6)
            if items:
                for item in items:
                    title_tag = item.select_one("h3 a") or item.select_one("a")
                    desc_tag = item.select_one("p") or item.select_one(".desc")
                    date_tag = item.select_one("time") or item.select_one(".date")
                    
                    if title_tag:
                        articles.append({
                            "title": title_tag.get_text(strip=True),
                            "date": date_tag.get_text(strip=True) if date_tag else "N/A",
                            "description": desc_tag.get_text(strip=True) if desc_tag else "No description available"
                        })
                if articles:
                    return articles
    return []

async def scrape_wikipedia(sector: str, client: httpx.AsyncClient) -> Dict[str, Any]:
    formatted_sector = sector.replace(' ', '_')
    # Try a few common URL patterns for Indian industry
    urls = [
        f"https://en.wikipedia.org/wiki/{formatted_sector}_industry_in_India",
        f"https://en.wikipedia.org/wiki/{formatted_sector}_sector_in_India",
        f"https://en.wikipedia.org/wiki/{formatted_sector}_in_India"
    ]
    
    response = None
    for url in urls:
        response = await fetch_with_retry(client, url)
        if response:
            break
            
    if not response:
        # Fallback to search if direct page not found
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={sector}+India&format=json&origin=*"
        search_response = await fetch_with_retry(client, search_url)
        if search_response:
            try:
                search_results = search_response.json()['query']['search']
                if search_results:
                    page_title = search_results[0]['title']
                    url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
                    response = await fetch_with_retry(client, url)
            except (KeyError, IndexError):
                logger.warning(f"Wikipedia fallback search failed for {sector}")

    if not response:
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    content_div = soup.select_one("#mw-content-text .mw-parser-output")
    if not content_div:
        return {}

    # Get first few paragraphs that have actual text
    paragraphs = []
    for p in content_div.find_all('p', recursive=False):
        text = p.get_text(strip=True)
        if len(text) > 50:
            paragraphs.append(text)
        if len(paragraphs) >= 3:
            break
            
    overview = "\n\n".join(paragraphs)
    
    stats = {}
    # Try infobox first
    for table in content_div.find_all('table', class_=['infobox', 'wikitable']):
        for row in table.find_all('tr'):
            header = row.find(['th', 'td'], class_='infobox-label') or row.find('th')
            data = row.find(['td', 'th'], class_='infobox-data') or row.find('td')
            if header and data:
                h_text = header.get_text(strip=True)
                d_text = data.get_text(strip=True)
                if h_text and d_text and len(h_text) < 50:
                    stats[h_text] = d_text
        if stats: break # Found some stats, good enough

    return {"overview": overview, "stats": stats, "url": response.url}

async def scrape_gov_data(sector: str, client: httpx.AsyncClient) -> List[Dict[str, str]]:
    # data.gov.in often blocks simple scrapers or requires specific search params
    url = f"https://www.data.gov.in/search?title={sector.replace(' ', '+')}"
    response = await fetch_with_retry(client, url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    datasets = []
    
    # Updated selectors for data.gov.in
    selectors = [
        ".views-row", 
        ".dataset-item",
        "div.search-result"
    ]
    
    for selector in selectors:
        items = soup.select(selector, limit=3)
        if items:
            for item in items:
                title_tag = item.select_one("h3 a") or item.select_one(".field-content a") or item.select_one("a")
                desc_tag = item.select_one(".field-name-field-description") or item.select_one(".notes") or item.select_one("p")
                
                if title_tag:
                    datasets.append({
                        "title": title_tag.get_text(strip=True),
                        "description": desc_tag.get_text(strip=True) if desc_tag else "Official dataset related to the sector."
                    })
            if datasets:
                return datasets
    return []

async def scrape_all(sector: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        tasks = [
            scrape_duckduckgo(sector),
            scrape_google_news(sector),
            scrape_economic_times(sector, client),
            scrape_wikipedia(sector, client),
            scrape_gov_data(sector, client)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results, handling potential errors from gather
    ddg_results, news_results, et_results, wiki_results, gov_results = [r if not isinstance(r, Exception) else [] for r in results]

    sources = {
        "duckduckgo": ddg_results,
        "news": news_results,
        "economic_times": et_results,
        "wikipedia": wiki_results,
        "gov_data": gov_results
    }

    # Combine all text for AI analysis in a structured way
    raw_text = f"Sector: {sector}\n"
    raw_text += f"Analysis Target: Indian Market\n\n"
    
    for source, data in sources.items():
        if not data:
            continue
            
        raw_text += f"=== SOURCE: {source.upper()} ===\n"
        if isinstance(data, list):
            for i, item in enumerate(data):
                title = item.get('title', 'N/A')
                desc = item.get('snippet', item.get('description', 'N/A'))
                raw_text += f"[{i+1}] TITLE: {title}\nCONTENT: {desc}\n"
                if 'date' in item:
                    raw_text += f"DATE: {item['date']}\n"
                raw_text += "\n"
        elif isinstance(data, dict):
            raw_text += f"OVERVIEW: {data.get('overview', 'N/A')}\n"
            if data.get('stats'):
                raw_text += "KEY STATISTICS:\n"
                for k, v in data['stats'].items():
                    raw_text += f"- {k}: {v}\n"
        raw_text += "\n"

    return {
        "sector": sector,
        "scraped_at": datetime.now(timezone.utc),
        "sources": sources,
        "total_sources": sum(len(v) if isinstance(v, list) else 1 for v in sources.values() if v),
        "raw_text_combined": raw_text
    }
