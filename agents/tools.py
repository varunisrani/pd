"""Comprehensive tool functions for external API integration with error handling and rate limiting."""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from dataclasses import dataclass, field

from .models import SearchResult, SearchQuery
from .settings import settings

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class RateLimiter:
    """Simple rate limiter for API calls."""
    max_calls: int
    time_window: int  # seconds
    calls: List[float] = field(default_factory=list)
    
    def can_make_request(self) -> bool:
        """Check if a request can be made within rate limits."""
        now = time.time()
        # Remove calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        return len(self.calls) < self.max_calls
    
    def record_request(self):
        """Record a request timestamp."""
        self.calls.append(time.time())
    
    async def wait_if_needed(self):
        """Wait if rate limit is exceeded."""
        if not self.can_make_request():
            wait_time = self.time_window - (time.time() - self.calls[0])
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds...")
                await asyncio.sleep(wait_time)


# Global rate limiters
brave_rate_limiter = RateLimiter(max_calls=100, time_window=60)  # 100 calls per minute
gmail_rate_limiter = RateLimiter(max_calls=250, time_window=60)  # 250 calls per minute


class RetryConfig:
    """Configuration for retry logic."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor


async def retry_with_backoff(
    func, 
    *args, 
    retry_config: RetryConfig = None,
    retryable_exceptions: tuple = (httpx.RequestError, httpx.HTTPStatusError),
    **kwargs
):
    """Retry function with exponential backoff."""
    
    if retry_config is None:
        retry_config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(retry_config.max_retries + 1):
        try:
            return await func(*args, **kwargs)
        
        except retryable_exceptions as e:
            last_exception = e
            
            if attempt == retry_config.max_retries:
                break
            
            # Calculate delay with exponential backoff
            delay = retry_config.base_delay * (retry_config.backoff_factor ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f} seconds...")
            await asyncio.sleep(delay)
    
    # If we get here, all retries failed
    raise last_exception


async def search_brave_api(
    query: str,
    api_key: str,
    max_results: int = 10,
    safesearch: str = "moderate",
    country: str = "US",
    language: str = "en"
) -> List[SearchResult]:
    """
    Search using Brave Search API with comprehensive error handling and rate limiting.
    
    Args:
        query: Search query string
        api_key: Brave API key
        max_results: Maximum number of results to return
        safesearch: SafeSearch setting (strict, moderate, off)
        country: Country code for localized results
        language: Language code for results
        
    Returns:
        List of SearchResult objects
        
    Raises:
        ValueError: For invalid parameters
        httpx.HTTPStatusError: For API errors
        httpx.RequestError: For network errors
    """
    
    # Validate input
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    if not api_key:
        raise ValueError("API key is required")
    
    if max_results < 1 or max_results > 50:
        raise ValueError("max_results must be between 1 and 50")
    
    # Apply rate limiting
    await brave_rate_limiter.wait_if_needed()
    
    # Prepare request
    url = "https://api.search.brave.com/res/v1/web/search"
    
    params = {
        "q": query.strip(),
        "count": min(max_results, settings.max_search_results),
        "safesearch": safesearch,
        "country": country,
        "search_lang": language,
        "format": "json"
    }
    
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
        "User-Agent": "PydanticAI-Research-Agent/1.0"
    }
    
    async def make_request():
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(settings.request_timeout),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        ) as client:
            
            brave_rate_limiter.record_request()
            response = await client.get(url, params=params, headers=headers)
            
            # Handle specific HTTP errors
            if response.status_code == 401:
                raise httpx.HTTPStatusError(
                    "Invalid API key or authentication failed",
                    request=response.request,
                    response=response
                )
            elif response.status_code == 429:
                raise httpx.HTTPStatusError(
                    "Rate limit exceeded",
                    request=response.request,
                    response=response
                )
            elif response.status_code == 403:
                raise httpx.HTTPStatusError(
                    "Access forbidden - check API permissions",
                    request=response.request,
                    response=response
                )
            
            response.raise_for_status()
            return response.json()
    
    try:
        # Execute with retry logic
        data = await retry_with_backoff(
            make_request,
            retry_config=RetryConfig(max_retries=3, base_delay=1.0),
            retryable_exceptions=(httpx.RequestError, httpx.HTTPStatusError)
        )
        
        # Parse results
        web_results = data.get("web", {}).get("results", [])
        
        if not web_results:
            logger.info(f"No search results found for query: '{query}'")
            return []
        
        # Convert to SearchResult objects
        results = []
        for item in web_results[:max_results]:
            try:
                result = SearchResult(
                    title=item.get("title", "No title"),
                    url=item.get("url", ""),
                    description=item.get("description", "No description"),
                    score=item.get("score")
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to parse search result: {e}")
                continue
        
        logger.info(f"Retrieved {len(results)} search results for query: '{query}'")
        return results
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Brave API HTTP error: {e.response.status_code}")
        if e.response.status_code == 429:
            # Rate limit hit, wait longer
            await asyncio.sleep(60)
        raise
        
    except httpx.RequestError as e:
        logger.error(f"Brave API request error: {e}")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error in Brave search: {e}")
        raise


def validate_search_query(query: str) -> SearchQuery:
    """
    Validate and sanitize search query.
    
    Args:
        query: Raw search query
        
    Returns:
        Validated SearchQuery object
        
    Raises:
        ValueError: For invalid queries
    """
    
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")
    
    # Remove potentially harmful characters
    sanitized_query = query.strip()
    
    # Remove excessive whitespace
    sanitized_query = " ".join(sanitized_query.split())
    
    # Check length constraints
    if len(sanitized_query) < 1:
        raise ValueError("Query is too short")
    
    if len(sanitized_query) > 500:
        raise ValueError("Query is too long (max 500 characters)")
    
    # Create validated query object
    return SearchQuery(query=sanitized_query, max_results=settings.max_search_results)


def format_search_results(results: List[SearchResult], query: str) -> str:
    """
    Format search results for display or agent consumption.
    
    Args:
        results: List of SearchResult objects
        query: Original search query
        
    Returns:
        Formatted string representation of results
    """
    
    if not results:
        return f"No search results found for query: '{query}'"
    
    lines = []
    lines.append(f"Search Results for: '{query}' ({len(results)} results)")
    lines.append("=" * 60)
    lines.append("")
    
    for i, result in enumerate(results, 1):
        lines.append(f"{i}. {result.title}")
        lines.append(f"   URL: {result.url}")
        lines.append(f"   Description: {result.description}")
        
        if result.score is not None:
            lines.append(f"   Relevance Score: {result.score:.2f}")
        
        lines.append("")
    
    return "\n".join(lines)


async def extract_key_insights(results: List[SearchResult], max_insights: int = 5) -> List[str]:
    """
    Extract key insights from search results.
    
    Args:
        results: List of SearchResult objects
        max_insights: Maximum number of insights to extract
        
    Returns:
        List of key insight strings
    """
    
    if not results:
        return ["No search results available for insight extraction"]
    
    insights = []
    
    # Analysis based on result patterns
    total_results = len(results)
    insights.append(f"Found {total_results} relevant sources on the topic")
    
    # Check for authoritative domains
    authoritative_domains = ['edu', 'gov', 'org']
    auth_sources = sum(1 for r in results if any(domain in r.url for domain in authoritative_domains))
    
    if auth_sources > 0:
        insights.append(f"Includes {auth_sources} authoritative sources (educational, government, or organizational)")
    
    # Check for recent content (simplified heuristic)
    current_year = datetime.now().year
    recent_sources = sum(1 for r in results if str(current_year) in r.description or str(current_year) in r.title)
    
    if recent_sources > 0:
        insights.append(f"Contains {recent_sources} sources with current year references")
    
    # Extract common themes from titles and descriptions
    all_text = " ".join([r.title + " " + r.description for r in results])
    words = all_text.lower().split()
    
    # Simple keyword frequency analysis
    word_freq = {}
    for word in words:
        if len(word) > 4:  # Focus on longer words
            word_freq[word] = word_freq.get(word, 0) + 1
    
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
    
    if top_words:
        keywords = [word for word, freq in top_words if freq > 1]
        if keywords:
            insights.append(f"Key themes include: {', '.join(keywords[:3])}")
    
    # Add general insights
    insights.append("Information compiled from multiple independent sources")
    
    return insights[:max_insights]


# Gmail-specific tools (simplified for integration with email_agent.py)

async def create_email_message(
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create email message structure for Gmail API.
    
    Args:
        to: List of recipient email addresses
        subject: Email subject
        body: Email body text
        cc: Optional CC recipients
        bcc: Optional BCC recipients
        
    Returns:
        Email message dictionary ready for Gmail API
    """
    
    # Validate inputs
    if not to or not all(isinstance(email, str) and "@" in email for email in to):
        raise ValueError("Invalid recipient email addresses")
    
    if not subject or not isinstance(subject, str):
        raise ValueError("Subject must be a non-empty string")
    
    if not body or not isinstance(body, str):
        raise ValueError("Body must be a non-empty string")
    
    # Create message structure
    message = {
        "to": to,
        "subject": subject.strip(),
        "body": body.strip(),
        "timestamp": datetime.now().isoformat()
    }
    
    if cc:
        message["cc"] = cc
    
    if bcc:
        message["bcc"] = bcc
    
    return message


async def log_api_usage(
    api_name: str,
    endpoint: str,
    status_code: int,
    response_time: float,
    request_size: int = 0,
    response_size: int = 0
):
    """
    Log API usage for monitoring and debugging.
    
    Args:
        api_name: Name of the API (e.g., "Brave Search", "Gmail")
        endpoint: API endpoint called
        status_code: HTTP status code
        response_time: Response time in seconds
        request_size: Size of request in bytes
        response_size: Size of response in bytes
    """
    
    logger.info(
        f"API Usage - {api_name}: {endpoint} | "
        f"Status: {status_code} | "
        f"Time: {response_time:.2f}s | "
        f"Request: {request_size}B | "
        f"Response: {response_size}B"
    )


# Error handling utilities

class APIError(Exception):
    """Base exception for API-related errors."""
    
    def __init__(self, message: str, api_name: str, status_code: Optional[int] = None):
        self.api_name = api_name
        self.status_code = status_code
        super().__init__(message)


class RateLimitError(APIError):
    """Exception for rate limit errors."""
    
    def __init__(self, api_name: str, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        message = f"Rate limit exceeded for {api_name}"
        if retry_after:
            message += f" (retry after {retry_after} seconds)"
        super().__init__(message, api_name, 429)


class AuthenticationError(APIError):
    """Exception for authentication errors."""
    
    def __init__(self, api_name: str):
        super().__init__(f"Authentication failed for {api_name}", api_name, 401)


async def handle_api_error(error: Exception, api_name: str) -> str:
    """
    Handle and format API errors for user-friendly messages.
    
    Args:
        error: The exception that occurred
        api_name: Name of the API that failed
        
    Returns:
        User-friendly error message
    """
    
    if isinstance(error, httpx.HTTPStatusError):
        status_code = error.response.status_code
        
        if status_code == 401:
            return f"{api_name} authentication failed. Please check your API key."
        elif status_code == 403:
            return f"Access to {api_name} forbidden. Check your permissions."
        elif status_code == 429:
            return f"{api_name} rate limit exceeded. Please try again later."
        elif status_code >= 500:
            return f"{api_name} server error. Please try again later."
        else:
            return f"{api_name} returned error {status_code}."
    
    elif isinstance(error, httpx.RequestError):
        return f"Network error connecting to {api_name}. Check your internet connection."
    
    elif isinstance(error, ValueError):
        return f"Invalid request to {api_name}: {str(error)}"
    
    else:
        return f"Unexpected error with {api_name}: {str(error)}"