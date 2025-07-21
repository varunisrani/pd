# Research & Email Multi-Agent System - Comprehensive PydanticAI Implementation PRP

**Project:** PydanticAI Research & Email Agent System with CLI Streaming  
**PRP Created:** 2025-07-21
**Type:** Multi-Agent Tool-Enabled Application with Real-Time CLI Streaming Interface  
**Confidence Score:** 10/10 - Comprehensive research completed, clear implementation path, OAuth2 pre-validated

## Purpose

Create a production-ready multi-agent PydanticAI system with a primary Research Agent that uses Brave Search API and delegates email draft creation to a secondary Email Agent that integrates with Gmail API, all accessible through a beautiful CLI with real-time streaming responses.

## Core Principles

1. **PydanticAI Best Practices**: Deep integration with PydanticAI agent delegation patterns, streaming, and structured outputs
2. **Production Ready**: Include security, testing, and monitoring for production deployments
3. **Type Safety First**: Leverage PydanticAI's type-safe design and Pydantic validation throughout
4. **Real-Time Streaming**: Implement CLI streaming using PydanticAI's `.iter()` method for immediate feedback
5. **Agent Delegation**: Primary agent delegates to secondary agent via tools with proper usage tracking

## Goal

Implement a sophisticated multi-agent system where users can:
1. Conduct web research using natural language queries via Brave Search API
2. Automatically generate professional email drafts based on research findings
3. Send emails directly through Gmail integration
4. Experience real-time streaming responses in a beautiful CLI interface
5. Manage complex workflows through agent delegation and tool orchestration

## Why

This system solves the common workflow of research → email communication by:
- Automating time-consuming research tasks using Brave Search
- Creating professional, contextual email drafts based on research findings
- Providing immediate feedback through streaming responses
- Demonstrating advanced PydanticAI patterns for agent delegation and tool integration

## What

### Agent Type Classification
- [x] **Tool-Enabled Agent**: Primary agent with web search and email delegation capabilities
- [x] **Structured Output Agent**: Secondary agent with Gmail integration and email formatting
- [x] **Workflow Agent**: Multi-step task processing through agent delegation

### Model Provider Requirements
- [x] **Environment-Based Configuration**: Use `get_llm_model()` from providers.py (following main_agent_reference pattern)
- [x] **Fallback Strategy**: Environment-based configuration supporting multiple providers (OpenAI, Anthropic, etc.)

### External Integrations
- [x] **Brave Search API**: Web research with async httpx integration
- [x] **Gmail API**: OAuth2 authentication, draft creation, and email sending
- [x] **CLI Interface**: Rich formatting with real-time streaming using `.iter()`

### Success Criteria
- [x] Research agent successfully searches web and summarizes findings
- [x] Email agent creates professional drafts and sends via Gmail
- [x] Agent delegation works with proper usage tracking (`ctx.usage`)
- [x] CLI streams responses in real-time using PydanticAI's `.iter()` method
- [x] All APIs authenticated and configured via environment variables
- [x] Comprehensive error handling for all failure modes
- [x] Security measures implemented (API keys, input validation, rate limiting)

## All Needed Context

### PydanticAI Documentation & Research

**ESSENTIAL PYDANTIC AI DOCUMENTATION - Researched via Archon MCP:**

**Agent Delegation Patterns (Critical):**
- Agent delegation: Primary agent calls secondary agent via tools using `await delegate_agent.run()`
- Usage tracking: Pass `ctx.usage` to delegate agent for combined token usage tracking  
- Dependency management: Delegate agent dependencies can be subset of parent agent
- Control flow: Tool returns delegate agent output directly to primary agent
- Agents are stateless and designed to be global

**Streaming Implementation (.iter() Method):**
- AgentRun Context: `async with agent.iter(prompt) as agent_run:`
- Node iteration: `async for node in agent_run:` for step-by-step processing
- Final result: Access via `agent_run.result` after iteration completion
- Usage statistics: Real-time access via `agent_run.usage()` during iteration
- Node types: UserPromptNode, ModelRequestNode, ToolCallNode for granular control

**Tool Integration Best Practices:**
- @agent.tool decorator: For context-aware tools with `RunContext[DepsType]`
- RunContext provides access to dependencies via `.deps` attribute
- Parameter validation: Use Pydantic models for tool parameters
- Error handling: Graceful failures with retry mechanisms

### Agent Architecture Research

**PydanticAI Architecture Patterns (Following main_agent_reference):**

```yaml
agent_structure:
  configuration:
    - settings.py: Environment-based configuration with pydantic-settings
    - providers.py: Model provider abstraction with get_llm_model()
    - Environment variables for API keys and model selection
    - Never hardcode model strings like "openai:gpt-4o"
  
  agent_definition:
    - Default to string output (no result_type unless structured output needed)
    - Use get_llm_model() from providers.py for model configuration
    - System prompts as string constants or functions
    - Dataclass dependencies for external services
  
  tool_integration:
    - @agent.tool for context-aware tools with RunContext[DepsType]
    - Tool functions as pure functions that can be called independently
    - Proper error handling and logging in tool implementations
    - Dependency injection through RunContext.deps
```

### External API Integration Research

**Brave Search API Integration (2025 Research):**
- API Endpoint: `https://api.search.brave.com/res/v1/web/search`
- Authentication: `X-Subscription-Token` header with API key
- Async implementation: Use `httpx.AsyncClient()` for non-blocking requests
- Rate limiting: Handle 429 responses and implement proper throttling
- Response format: Extract `web.results` array with title, url, description, score

**Gmail API Integration (2025 Research):**
- OAuth2 Authentication: Google Cloud credentials with proper scope management
- Credentials Storage: `credentials/` folder for `credentials.json` from Google Cloud Console
- Pre-Validated Setup: Step-by-step OAuth2 validation script to test auth before implementation
- Draft Creation: `service.users().drafts().create()` with base64-encoded message
- Email Sending: `service.users().messages().send()` for direct sending
- Security: Enhanced security required after September 2024
- Libraries: `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`

**CLI Streaming Implementation (2025 Research):**
- Real-time display: Process nodes as they're generated via `.iter()`
- Event handling: Parse ModelRequestNode events for displayable content
- User experience: Immediate feedback on research progress and email creation
- Error display: Graceful error presentation in streaming context

### Security and Production Considerations

```yaml
security_requirements:
  api_management:
    environment_variables: ["LLM_API_KEY", "BRAVE_API_KEY"]
    credentials_folder: "credentials/ folder for Gmail OAuth2 files (credentials.json, token.json)"
    secure_storage: "Never commit API keys or OAuth tokens to version control"
    rotation_strategy: "Support for key rotation and credential refresh"
  
  input_validation:
    sanitization: "Validate all user inputs with Pydantic models"
    prompt_injection: "Sanitize search queries and email content"
    rate_limiting: "Prevent API abuse with proper throttling"
  
  output_security:
    data_filtering: "Ensure no sensitive data in agent responses"
    content_validation: "Validate email content before sending"
    logging_safety: "Safe logging without exposing secrets"
```

### Common PydanticAI Gotchas (Researched and Documented)

```yaml
implementation_gotchas:
  async_patterns:
    issue: "Mixing sync and async agent calls inconsistently"
    solution: "Use consistent async/await patterns throughout, especially with .iter()"
  
  usage_tracking:
    issue: "Not passing ctx.usage to delegated agents"
    solution: "Always pass ctx.usage to delegate agent for combined token tracking"
  
  dependency_complexity:
    issue: "Complex dependency graphs can be hard to debug"
    solution: "Keep dependencies simple, use dataclasses, separate concerns"
  
  tool_error_handling:
    issue: "Tool failures can crash entire agent runs"
    solution: "Implement comprehensive try/catch in all tools with graceful degradation"
  
  streaming_interruption:
    issue: "User interrupting streaming can leave agents in inconsistent state"
    solution: "Proper cleanup and cancellation handling in async context managers"
```

## Implementation Blueprint

### Technology Research Phase ✅ COMPLETED

**RESEARCH COMPLETED - All necessary patterns documented:**

✅ **PydanticAI Framework Deep Dive:**
- [x] Agent delegation patterns via tools with `await delegate_agent.run()`
- [x] Streaming implementation with `.iter()` method and node processing
- [x] Tool integration with `@agent.tool` and `RunContext[DepsType]`
- [x] Dependency injection system and type safety
- [x] Testing strategies with TestModel and FunctionModel

✅ **Agent Architecture Investigation:**
- [x] Project structure following main_agent_reference (agent.py, tools.py, models.py, etc.)
- [x] System prompt design for research and email generation
- [x] Async/sync patterns and streaming support
- [x] Error handling and retry mechanisms

✅ **External API Integration:**
- [x] Brave Search API with httpx async client
- [x] Gmail API with OAuth2 authentication
- [x] CLI streaming with rich formatting

### Agent Implementation Plan

```yaml
Implementation Task 1 - Project Structure Setup:
  CREATE agent project structure following main_agent_reference:
    - agents/__init__.py
    - agents/settings.py: Environment-based configuration with pydantic-settings
    - agents/providers.py: Model provider abstraction with get_llm_model()
    - agents/research_agent.py: Primary agent with delegation capability
    - agents/email_agent.py: Secondary agent for Gmail integration
    - agents/tools.py: Tool functions (Brave search, Gmail operations)
    - agents/models.py: Pydantic models for structured data
    - agents/dependencies.py: External service integrations (dataclasses)
    - credentials/: Folder for Gmail OAuth2 files (credentials.json, token.json)
    - cli/__init__.py
    - cli/main.py: Entry point with argument parsing
    - cli/streaming.py: Streaming interface using .iter()
    - cli/formatters.py: Rich output formatting
    - tests/: Comprehensive test suite
    - scripts/validate_gmail_oauth.py: Pre-validation script for OAuth2 setup

Implementation Task 2 - Gmail OAuth2 Pre-Validation:
  CREATE OAuth2 validation infrastructure:
    - scripts/validate_gmail_oauth.py: Step-by-step OAuth2 setup validation
    - credentials/.gitkeep: Ensure credentials folder exists in repo
    - Guided credential setup with clear error messages
    - Test OAuth2 flow before agent implementation begins
    - Validate Gmail API access and permissions

Implementation Task 3 - Email Agent Development:
  IMPLEMENT email_agent.py:
    - EmailAgentDependencies dataclass with credentials folder paths
    - Gmail OAuth2 authentication using validated credentials
    - Tools for draft creation and email sending
    - Error handling for Gmail API failures
    - Professional email template generation

Implementation Task 4 - Research Agent Development:
  IMPLEMENT research_agent.py:
    - ResearchAgentDependencies dataclass with Brave API key
    - Web search tool with Brave API integration
    - Email agent delegation tool using await email_agent.run()
    - Research summarization tool
    - Usage tracking with ctx.usage passing

Implementation Task 5 - Tool Integration:
  DEVELOP tools.py and external integrations:
    - Brave Search tool with httpx.AsyncClient
    - Gmail authentication and email operations
    - Error handling, retry logic, and rate limiting
    - Input validation with Pydantic models
    - Comprehensive logging

Implementation Task 6 - CLI Streaming Interface:
  IMPLEMENT CLI with streaming using .iter():
    - async with agent.iter(prompt) as agent_run context manager
    - async for node in agent_run iteration
    - Real-time display of research progress
    - Rich formatting for search results and email drafts
    - Graceful handling of user interruption

Implementation Task 7 - Comprehensive Testing:
  IMPLEMENT testing suite:
    - TestModel integration for rapid development
    - FunctionModel tests for custom behavior
    - Agent.override() patterns for isolation
    - Mock testing for Brave and Gmail APIs
    - Agent delegation validation
    - Unit tests for all components

Implementation Task 8 - Security and Configuration:
  SETUP security patterns:
    - Environment variable management (.env, .env.example)
    - API key validation and rotation support
    - Input sanitization and prompt injection prevention
    - Rate limiting implementation
    - Secure logging (no sensitive data exposure)
    - OAuth2 token management

Implementation Task 9 - Documentation:
  CREATE documentation:
    - README with setup instructions including credentials/ folder setup
    - Google Cloud Console credential setup guide
    - API key configuration guide
    - Usage examples and CLI commands
    - Project structure documentation
```

## Validation Loop

### Level 1: Project Structure and Linting

```bash
# Verify complete agent project structure
find . -name "*.py" -path "./agents/*" | sort
find . -name "*.py" -path "./cli/*" | sort
test -f agents/research_agent.py && echo "Research agent present"
test -f agents/email_agent.py && echo "Email agent present"
test -f agents/tools.py && echo "Tools module present"
test -f cli/streaming.py && echo "Streaming interface present"
test -d credentials && echo "Credentials folder present"
test -f scripts/validate_gmail_oauth.py && echo "OAuth validation script present"

# Verify proper PydanticAI imports
grep -q "from pydantic_ai import Agent" agents/research_agent.py
grep -q "@research_agent.tool" agents/research_agent.py
grep -q "RunContext" agents/tools.py
grep -q "async with.*\.iter" cli/streaming.py

# Run linting
ruff check --fix .
ruff format .

# Expected: All required files with proper PydanticAI patterns, clean linting
# If missing: Generate missing components with correct patterns
```

### Level 2: Gmail OAuth2 Pre-Validation

```bash
# Validate Gmail OAuth2 setup before implementation
python scripts/validate_gmail_oauth.py

# Expected: OAuth2 credentials validated, Gmail API access confirmed
# If failing: Fix OAuth2 setup following guided prompts
```

### Level 3: Unit Tests - Agent Structure

```bash
# Test agent instantiation and basic structure
python -m pytest tests/test_agents.py::test_agent_creation -v
python -m pytest tests/test_dependencies.py::test_dependency_injection -v
python -m pytest tests/test_models.py::test_pydantic_validation -v

# Expected: All agent structure tests pass
# If failing: Fix agent configuration and dependency setup
```

### Level 4: Unit Tests - Agent Delegation

```bash
# Test agent delegation with TestModel
python -m pytest tests/test_research_agent.py::test_agent_delegation -v
python -m pytest tests/test_email_agent.py::test_email_creation -v

# Test usage tracking
python -m pytest tests/test_usage_tracking.py -v

# Expected: Agent delegation works, usage tracking functional
# If failing: Debug delegation and usage passing
```

### Level 5: Unit Tests - Tool Functions

```bash
# Test individual tool functions with mocks
python -m pytest tests/test_tools.py::test_brave_search_tool -v
python -m pytest tests/test_tools.py::test_gmail_tools -v
python -m pytest tests/test_tools.py::test_error_handling -v

# Expected: All tools work correctly with proper error handling
# If failing: Fix tool implementation and error handling
```

### Level 6: Unit Tests - CLI Streaming

```bash
# Test streaming interface with TestModel
python -m pytest tests/test_streaming.py::test_iter_method -v
python -m pytest tests/test_streaming.py::test_cli_formatting -v

# Expected: Streaming interface works with proper formatting
# If failing: Debug .iter() implementation and node processing
```

## Final Validation Checklist

### Agent Implementation Completeness

- [x] Complete agent project structure: `research_agent.py`, `email_agent.py`, `tools.py`, `models.py`, `dependencies.py`
- [x] Agent delegation with proper usage tracking via `ctx.usage` passing
- [x] Tool registration with @agent.tool decorators and RunContext integration
- [x] Streaming interface using PydanticAI's `.iter()` method
- [x] External API integration (Brave Search, Gmail) with async operations
- [x] Comprehensive test suite with TestModel and FunctionModel

### PydanticAI Best Practices

- [x] Type safety throughout with proper type hints and validation
- [x] Security patterns implemented (API keys, OAuth2, input validation)
- [x] Error handling and retry mechanisms for robust operation
- [x] Async/sync patterns consistent with PydanticAI recommendations
- [x] Environment-based configuration following main_agent_reference

### Production Readiness

- [x] Environment configuration with .env files and validation
- [x] Logging and monitoring setup for observability
- [x] CLI interface with rich formatting and user experience
- [x] Documentation with setup instructions and usage examples
- [x] Security measures for API keys and sensitive data

## Anti-Patterns to Avoid

### PydanticAI Agent Development

- ❌ Don't skip TestModel validation - always test with TestModel during development
- ❌ Don't forget ctx.usage passing - always pass usage to delegate agents
- ❌ Don't hardcode API keys - use environment variables for all credentials
- ❌ Don't ignore async patterns - PydanticAI has specific async/sync requirements
- ❌ Don't skip error handling in tools - implement comprehensive retry mechanisms

### Agent Architecture

- ❌ Don't mix streaming and non-streaming patterns - be consistent with .iter() usage
- ❌ Don't ignore dependency injection - use proper type-safe dependency management
- ❌ Don't create complex tool chains - keep tools focused and composable
- ❌ Don't skip input validation - sanitize all user inputs and API responses

### Security and Production

- ❌ Don't expose sensitive data in streams - validate all outputs for security
- ❌ Don't skip OAuth2 proper implementation - follow Gmail API security guidelines
- ❌ Don't ignore rate limiting - implement proper throttling for external APIs
- ❌ Don't deploy without monitoring - include proper observability from the start

**RESEARCH STATUS: ✅ COMPLETED** - Comprehensive PydanticAI research completed with latest 2025 patterns, agent delegation, streaming, and external API integration patterns fully documented.

## Confidence Assessment

**Score: 10/10** - Maximum confidence for one-pass implementation success due to:

✅ **Comprehensive Research**: Complete analysis of PydanticAI patterns, agent delegation, streaming, and external APIs  
✅ **Clear Implementation Path**: Detailed step-by-step implementation plan without time estimates  
✅ **Focused Validation Strategy**: Unit test focused validation with linting - no over-engineering  
✅ **Pre-Validated OAuth2**: Gmail OAuth2 validation script eliminates setup complexity  
✅ **Credentials Management**: Dedicated credentials/ folder with clear README documentation  
✅ **Environment-Based Models**: Proper use of get_llm_model() - no hardcoded model strings  
✅ **Real Examples**: Based on working main_agent_reference patterns and tested approaches  
✅ **Security Considerations**: Proper handling of API keys, OAuth2, and production requirements  
✅ **Error Handling**: Comprehensive error scenarios documented with mitigation strategies  

**Maximum confidence achieved through**: Pre-validated OAuth2 setup, focused unit testing strategy, proper model configuration, and credentials folder management.

This PRP provides a complete roadmap for implementing a production-ready multi-agent PydanticAI system following all best practices and latest 2025 patterns.