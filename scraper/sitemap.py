import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36",
    "Accept": "application/xml,text/xml,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}


def extract_sitemap_links(site_url: str) -> set:
    """Recursively parse all sitemap links and extract URLs using robots.txt first if available."""
    parsed_links = set()
    parsed_url = urlparse(site_url)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

    sitemap_urls = []

    # Step 1: Try to fetch sitemap URLs from robots.txt
    try:
        print(f"Trying to fetch robots.txt from: {domain}/robots.txt")
        res = requests.get(f"{domain}/robots.txt", headers=HEADERS, timeout=10)
        if res.status_code == 200:
            lines = res.text.splitlines()
            for line in lines:
                line = line.strip()
                if line.lower().startswith("sitemap:"):
                    sitemap_url = line.split(":", 1)[1].strip()
                    if sitemap_url:
                        print(f"Found sitemap in robots.txt: {sitemap_url}")
                        sitemap_urls.append(sitemap_url)
    except Exception as e:
        print(f"Failed to fetch or parse robots.txt — {e}")

    # Step 2: Fallback to default sitemap URLs if robots.txt didn’t help
    if not sitemap_urls:
        print("No sitemap found in robots.txt. Using default fallback locations.")
        sitemap_urls = [
            urljoin(domain, "/sitemap.xml"),
            urljoin(domain, "/sitemap_index.xml"),
            urljoin(domain, "/media/sitemap/sitemap.xml"),
            urljoin(domain, "/sitemaps/sitemap.xml"),
            urljoin(domain, "/sitemap/sitemap.xml")
        ]

    visited = set()  # Track visited sitemap URLs to avoid infinite loops

    def parse_sitemap(url):
        if url in visited:
            return
        visited.add(url)

        try:
            print(f"Trying to fetch sitemap: {url}")
            time.sleep(0.5)

            session = requests.Session()
            session.headers.update(HEADERS)

            res = session.get(url, timeout=15, allow_redirects=True)
            res.raise_for_status()

            print(f"Successfully fetched sitemap: {url}")
            soup = BeautifulSoup(res.content, "xml")

            # Handle sitemap indexes
            sitemaps = soup.find_all("sitemap")
            if sitemaps:
                for sitemap in sitemaps:
                    loc = sitemap.find("loc")
                    if loc:
                        parse_sitemap(loc.text.strip())

            # Handle regular sitemap with URLs
            for loc in soup.find_all("loc"):
                link = loc.text.strip()
                if link.endswith(".xml"):
                    parse_sitemap(link)
                else:
                    parsed_links.add(link)

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch sitemap: {url} — {e}")
        except Exception as e:
            print(f"Failed to parse sitemap: {url} — {e}")

    # Try all discovered or default sitemap URLs
    for sitemap_url in sitemap_urls:
        parse_sitemap(sitemap_url)
        if parsed_links:
            break

    return parsed_links
