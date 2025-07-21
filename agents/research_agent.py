"""Simplified Research Agent with truthful error handling."""

import logging
from typing import List, Optional
import httpx
from pydantic_ai import Agent, RunContext

from .dependencies import ResearchAgentDependencies, EmailAgentDependencies
from .models import SearchResult, SearchQuery
from .email_agent import email_agent
from .providers import get_llm_model
from .settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Simplified research agent with truthful system prompt
research_agent = Agent(
    get_llm_model(),
    deps_type=ResearchAgentDependencies,
    system_prompt="""You are a truthful research assistant. You MUST be completely honest about what actually happens.

Your capabilities:
1. Search the web using Brave Search API
2. Delegate email creation to the email agent

CRITICAL RULES:
- ONLY claim success when operations actually succeed
- If a tool fails, you MUST report the failure honestly
- NEVER claim to have sent emails unless they were actually sent
- NEVER claim to have created drafts unless they were actually created
- If credentials are missing, report this clearly
- Be helpful but always truthful about what you can and cannot do

When tools fail, explain what went wrong and suggest solutions."""
)


@research_agent.tool
async def search_web(
    ctx: RunContext[ResearchAgentDependencies], 
    query: str,
    max_results: int = 10
) -> str:
    """Search the web using Brave Search API."""
    
    try:
        # Validate query
        search_query = SearchQuery(query=query, max_results=max_results)
        
        # Prepare request
        deps = ctx.deps
        url = "https://api.search.brave.com/res/v1/web/search"
        
        params = {
            "q": search_query.query,
            "count": min(search_query.max_results, settings.max_search_results),
            "format": "json",
            "safesearch": "moderate"
        }
        
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": deps.brave_api_key
        }
        
        # Make request
        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            web_results = data.get("web", {}).get("results", [])
            
            if not web_results:
                return f"SEARCH RESULT: No results found for '{query}'"
            
            # Format results simply
            formatted_results = [f"Found {len(web_results)} results for '{query}':\n"]
            
            for i, item in enumerate(web_results[:search_query.max_results], 1):
                formatted_results.append(f"{i}. {item.get('title', 'No title')}")
                formatted_results.append(f"   {item.get('description', 'No description')}")
                formatted_results.append(f"   URL: {item.get('url', '')}\n")
            
            return "SEARCH SUCCESS: " + "\n".join(formatted_results)
            
    except httpx.HTTPStatusError as e:
        error_msg = f"SEARCH FAILED: HTTP {e.response.status_code}"
        if e.response.status_code == 401:
            error_msg += " - Invalid API key. Check your Brave API configuration."
        elif e.response.status_code == 429:
            error_msg += " - Rate limit exceeded. Try again later."
        logger.error(error_msg)
        return error_msg
        
    except Exception as e:
        error_msg = f"SEARCH FAILED: {str(e)}"
        logger.error(error_msg)
        return error_msg


@research_agent.tool
async def delegate_to_email_agent(
    ctx: RunContext[ResearchAgentDependencies],
    research_findings: str,
    recipients: List[str],
    email_purpose: str,
    tone: str = "professional"
) -> str:
    """Delegate email creation to the email agent with research findings."""
    
    try:
        # Check if we have email credentials
        try:
            email_deps = EmailAgentDependencies.from_settings()
            # Basic validation - check if credentials file exists
            import os
            if not os.path.exists(email_deps.credentials_file):
                return "EMAIL DELEGATION FAILED: Gmail credentials file not found. Please set up Gmail OAuth2 credentials first."
        except Exception as cred_error:
            return f"EMAIL DELEGATION FAILED: Credentials setup error - {str(cred_error)}"
        
        # Create the email request prompt
        email_prompt = f"""Create a professional email draft based on this research:

Research Findings:
{research_findings}

Email Details:
- Recipients: {', '.join(recipients)}
- Purpose: {email_purpose}
- Tone: {tone}

Please create an appropriate email draft."""

        # Delegate to email agent
        email_result = await email_agent.run(
            email_prompt,
            deps=email_deps
        )
        
        # Check if email agent succeeded
        if hasattr(email_result, 'output') and email_result.output:
            return f"EMAIL DELEGATION SUCCESS: Email draft created for {', '.join(recipients)}. The email agent has prepared a {tone} email about {email_purpose}."
        else:
            return f"EMAIL DELEGATION FAILED: Email agent did not produce a valid result."
            
    except Exception as e:
        error_msg = f"EMAIL DELEGATION FAILED: {str(e)}"
        logger.error(error_msg)
        return error_msg


# External function for testing
async def test_research_with_missing_credentials(query: str) -> str:
    """Test function to verify truthful behavior with missing credentials."""
    
    try:
        deps = ResearchAgentDependencies(brave_api_key=settings.brave_api_key)
        
        result = await research_agent.run(
            f"""Search for information about '{query}' and then create an email draft for test@example.com about your findings.""",
            deps=deps
        )
        
        return result.output if hasattr(result, 'output') else str(result)
        
    except Exception as e:
        return f"Test failed: {e}"