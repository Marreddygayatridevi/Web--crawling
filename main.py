import asyncio
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scraper.crawler import collect_all_links

# Enhanced Windows-specific fix for Playwright compatibility
if sys.platform.startswith("win"):
    # Set the event loop policy before any async operations
    try:
        # Use ProactorEventLoop for Windows (recommended for subprocess operations)
        policy = asyncio.WindowsProactorEventLoopPolicy()
        asyncio.set_event_loop_policy(policy)
        print("Set Windows ProactorEventLoopPolicy")
    except AttributeError:
        try:
            # Fallback to SelectorEventLoop if ProactorEventLoop is not available
            policy = asyncio.WindowsSelectorEventLoopPolicy()
            asyncio.set_event_loop_policy(policy)
            print("Set Windows SelectorEventLoopPolicy")
        except AttributeError:
            print("Using default event loop policy")

app = FastAPI()

class URLRequest(BaseModel):
    url: str

@app.post("/crawl")
async def crawl_website(request: URLRequest):
    try:
        # Ensure we're using the correct event loop
        loop = asyncio.get_event_loop()
        if sys.platform.startswith("win"):
            # For Windows, create a new event loop if needed
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        
        all_links = await collect_all_links(request.url)
        return {"total_links": len(all_links), "links": all_links}
    except Exception as e:
        print(f"Error in crawl_website: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the web crawler API!"}