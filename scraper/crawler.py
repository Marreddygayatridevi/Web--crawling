import json
import asyncio
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from scraper.robots import is_allowed
from scraper.sitemap import extract_sitemap_links
from playwright.async_api import async_playwright

OUTPUT_FILE = Path("extracted.json")

async def fallback_scrape(url: str) -> set:
    """Scrape all links from site using Playwright (with scroll and pagination support)."""
    try:
        # Windows-specific Playwright configuration
        if sys.platform.startswith("win"):
            # Use a new event loop for Playwright on Windows
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-web-security',  # Additional Windows compatibility
                    '--disable-features=VizDisplayCompositor'  # Additional Windows compatibility
                ]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            # Set longer timeout and wait for network idle
            await page.goto(url, wait_until='networkidle', timeout=60000)  # Increased timeout
            
            # Wait for page to load completely
            await page.wait_for_timeout(3000)  # Increased wait time

            # Scroll to bottom multiple times to load dynamic content
            print("Scrolling to load dynamic content...")
            for i in range(3):  # Reduced scrolls for faster execution
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)
                print(f"Scroll {i+1}/3 completed")

            # Get the final HTML
            html = await page.content()
            await browser.close()
            
            print("Successfully scraped page content")

    except Exception as e:
        print(f"Playwright error: {e}")
        raise Exception(f"Failed to scrape page: {e}")

    # Parse links from HTML
    soup = BeautifulSoup(html, "lxml")
    links = set()
    base_url = url.rstrip("/")
    
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        
        # Skip empty hrefs and fragments
        if not href or href.startswith("#") or href.startswith("javascript:"):
            continue
            
        # Convert relative URLs to absolute
        if href.startswith("/"):
            href = base_url + href
        elif not href.startswith("http"):
            href = base_url + "/" + href
            
        # Only include HTTP/HTTPS links
        if href.startswith(("http://", "https://")):
            links.add(href)
    
    print(f"Found {len(links)} links via scraping")
    return links

async def collect_all_links(site_url: str) -> list:
    """Collect all links from a website using sitemap first, then fallback to scraping."""
    print(f"Starting crawl for: {site_url}")
    
    if not is_allowed(site_url):
        raise Exception("Crawling disallowed by robots.txt")

    all_links = set()

    # Step 1: Try sitemap approach
    print("Attempting to extract links from sitemap...")
    try:
        sitemap_links = extract_sitemap_links(site_url)
        if sitemap_links:
            all_links.update(sitemap_links)
            print(f"Found {len(sitemap_links)} links from sitemap")
        else:
            print("No links found in sitemap")
    except Exception as e:
        print(f"Sitemap extraction failed: {e}")

    # Step 2: Fallback to visual scraping if no sitemap links found
    if not all_links:
        print("Sitemap not found or empty, falling back to scraping page...")
        try:
            scraped_links = await fallback_scrape(site_url)
            all_links.update(scraped_links)
            print(f"Found {len(scraped_links)} links from scraping")
        except Exception as e:
            print(f"Scraping failed: {e}")
            raise Exception(f"Both sitemap and scraping failed: {e}")

    # Save to JSON file
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(list(all_links), f, indent=2, ensure_ascii=False)
        print(f"Saved {len(all_links)} links to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Failed to save links to file: {e}")

    return list(all_links)



