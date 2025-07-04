# Web Crawler API

A high-performance web crawler built with FastAPI and Playwright that discovers all internal links from any website using multiple extraction strategies.

## Features

- **Multi-Strategy Link Discovery**: Combines sitemap parsing and browser-based scraping
- **FastAPI REST API**: Easy-to-use HTTP endpoints
- **Playwright Integration**: JavaScript-enabled crawling for dynamic content
- **Intelligent Scrolling**: Automatically loads dynamic content and pagination
- **Robots.txt Compliance**: Respects website crawling policies
- **JSON Output**: Structured results saved to file


## Requirements

Create a `requirements.txt` file with the following dependencies:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
playwright==1.40.0
beautifulsoup4==4.12.2
lxml==4.9.3
requests==2.31.0
pydantic==2.5.0
```

## Project Structure

```
web-crawler/
├── main.py                 # FastAPI application
├── scraper/
│   ├── __init__.py
│   ├── crawler.py          # Main crawling logic
│   ├── robots.py           # Robots.txt handling
│   └── sitemap.py          # Sitemap parsing
├── requirements.txt        # Python dependencies
├── extracted.json          # Output file (generated)
└── README.md              # This file
```

## Usage

### Starting the API Server

```bash
uvicorn main:app 
```

The API will be available at: `http://localhost:8000`


## How It Works

### 1. Robots.txt Check
- Verifies crawling permissions before starting
- Respects website policies and rate limits

### 2. Sitemap Discovery
- Searches for sitemaps in robots.txt
- Falls back to common sitemap locations:
  - `/sitemap.xml`
  - `/sitemap_index.xml`
  - `/media/sitemap/sitemap.xml`
  - `/sitemaps/sitemap.xml`

### 3. Browser-Based Crawling
- Uses Playwright to load pages with JavaScript
- Automatically scrolls to load dynamic content
- Handles pagination and "load more" buttons
- Extracts links using multiple strategies

### 4. Link Processing
- Converts relative URLs to absolute
- Filters out external domains
- Removes duplicates and fragments
- Validates URL formats





