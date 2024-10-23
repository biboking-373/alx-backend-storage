import requests
import redis
import time
from functools import wraps

# Set up the Redis connection (assuming Redis is running locally)
cache = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Decorator for caching and counting the number of accesses to a URL
def cache_page(expiration=10):
    def decorator(func):
        @wraps(func)
        def wrapper(url):
            # Check if the page is already cached
            cached_page = cache.get(f"page:{url}")
            if cached_page:
                # Increment the access count
                cache.incr(f"count:{url}")
                print(f"Cache hit: {url}")
                return cached_page
            
            # If not cached, fetch the page
            print(f"Cache miss: Fetching {url}")
            page_content = func(url)
            
            # Store the page in the cache and set the expiration time
            cache.setex(f"page:{url}", expiration, page_content)
            # Track how many times this URL was accessed
            cache.incr(f"count:{url}")
            
            return page_content
        return wrapper
    return decorator

# The core get_page function that fetches the HTML content
@cache_page(expiration=10)
def get_page(url: str) -> str:
    response = requests.get(url)
    return response.text

# Test the function with a slow URL for caching
if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk/delay/3000/url/https://example.com"
    
    # First call (should fetch and cache the page)
    print("Fetching page for the first time...")
    content = get_page(url)
    print("Page fetched.")
    
    # Wait 2 seconds and fetch again (should use cache)
    time.sleep(2)
    print("Fetching page again (should hit cache)...")
    content = get_page(url)
    
    # Wait for cache to expire (10 seconds total)
    time.sleep(11)
    print("Fetching page after cache expiration...")
    content = get_page(url)

