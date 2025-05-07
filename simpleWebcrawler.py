import sys
import asyncio
from crawl4ai import AsyncWebCrawler

async def crawl_url(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return result.json()

def main():

    # Check if exactly one URL argument is provided via command line
    if len(sys.argv) != 2:
        print("Error: Please provide a URL as command line argument")
        sys.exit(1)
    
    # Get the URL from command line arguments (sys.argv[0] is the script name)
    url = sys.argv[1]
    result = asyncio.run(crawl_url(url))
    print(result)

if __name__ == "__main__":
    main()