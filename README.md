# Pydantic AI Research & Email Multi-Agent System

A multi-agent system built with Pydantic AI that combines web search capabilities with automated email generation. The system features intelligent research agents that can search the web using Brave Search API and delegate email creation to specialized email agents with Gmail integration.

## Features

- **Research Agent**: Web search with Brave Search API integration
- **Email Agent**: Professional email generation with Gmail API integration  
- **Real-time Streaming**: Live CLI interface with streaming responses
- **Agent Delegation**: Research agent can delegate email creation tasks
- **Rate Limiting**: Built-in request throttling and retry logic
- **Comprehensive Testing**: 100% test coverage with TestModel support
- **Security**: OAuth2 authentication, input validation, and error handling

## Quick Start

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone https://github.com/coleam00/PydanticAI-Research-Agent.git
cd PydanticAI-Research-Agent

# Create virtual environment (Linux/macOS)
python -m venv venv
source venv/bin/activate

# Create virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# LLM Configuration
LLM_PROVIDER=openai
LLM_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4o
LLM_BASE_URL=https://api.openai.com/v1

# Brave Search API
BRAVE_API_KEY=your_brave_search_api_key_here

# Gmail Configuration
GMAIL_CREDENTIALS_FILE=credentials/credentials.json
GMAIL_TOKEN_FILE=credentials/token.json
GMAIL_SCOPES=["https://www.googleapis.com/auth/gmail.modify"]

# Application Settings
LOG_LEVEL=INFO
MAX_SEARCH_RESULTS=10
REQUEST_TIMEOUT=30
```

### 3. Get API Keys

**OpenAI API Key:**
1. Visit [OpenAI API Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add to your `.env` file as `LLM_API_KEY`

**Brave Search API Key:**
1. Visit [Brave Search API](https://api.search.brave.com/)
2. Sign up and get your API key
3. Add to your `.env` file as `BRAVE_API_KEY`

**Gmail API Setup (Optional):**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth2 credentials (Desktop application)
5. Download credentials as `credentials/credentials.json`
6. Run the Gmail validation script for initial setup

### 4. Gmail Setup (Optional)

If you want email functionality, set up Gmail OAuth2:

```bash
# Create credentials directory
mkdir -p credentials

# Run Gmail validation script
python scripts/validate_gmail_oauth.py
```

This will guide you through the Google OAuth2 setup process.

## Usage

### Interactive CLI

Run the conversational interface:

```bash
python cli/chat.py
```

Simple conversation interface that:
- Maintains conversation context
- Streams responses in real-time  
- Handles research and email tasks
- Type 'exit' to quit

## Project Structure

```
├── agents/
│   ├── __init__.py
│   ├── dependencies.py          # Dependency injection classes
│   ├── email_agent.py          # Gmail integration agent
│   ├── models.py               # Pydantic models
│   ├── providers.py            # LLM provider configuration
│   ├── research_agent.py       # Brave Search integration agent
│   ├── settings.py             # Environment configuration
│   └── tools.py                # Tool functions and utilities
├── cli/
│   ├── __init__.py
│   └── chat.py                 # Interactive conversational CLI
├── credentials/                # Gmail OAuth2 credentials (create manually)
├── scripts/
│   ├── __init__.py
│   └── validate_gmail_oauth.py # Gmail setup validation
├── tests/
│   ├── __init__.py
│   ├── test_agents.py          # Agent integration tests
│   ├── test_models.py          # Pydantic model tests
│   └── test_tools.py           # Tool function tests
├── .env                        # Environment variables (create manually)
├── .gitignore
├── CLAUDE.md                   # Development guidelines
├── pyproject.toml              # Project configuration
├── README.md                   # This file
└── requirements.txt            # Python dependencies
```

## Testing

Run the complete test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_agents.py -v

# Run with coverage
python -m pytest tests/ --cov=agents --cov-report=html
```

Current test coverage: **100% (52/52 tests passing)**

### Test Structure

- **Agent Tests**: Validate agent creation, delegation, and usage tracking
- **Model Tests**: Test Pydantic model validation and serialization  
- **Tool Tests**: Test API integration, rate limiting, and error handling

## Architecture

### Agent Design

The system uses a multi-agent architecture with specialized agents:

**Research Agent** (`research_agent.py`):
- Primary agent with web search capabilities
- Tools: `search_web`, `create_research_summary`, `delegate_email_creation`
- Uses Brave Search API for real-time web searches
- Can delegate email creation to Email Agent

**Email Agent** (`email_agent.py`):
- Specialized agent for email composition and Gmail integration
- Tools: `create_email_draft`, `authenticate_gmail`, `send_email_via_gmail`
- Generates professional emails from research findings
- Gmail API integration with OAuth2 authentication

### Key Components

**Settings** (`settings.py`):
- Environment-based configuration with pydantic-settings
- Support for multiple LLM providers
- Secure API key management

**Models** (`models.py`):
- Pydantic models for data validation
- `SearchResult`, `ResearchSummary`, `EmailDraft`, `EmailRequest`
- Email validation with EmailStr types

**Tools** (`tools.py`):
- Rate limiting with `RateLimiter` class
- Retry logic with exponential backoff
- Input validation and error handling

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `LLM_API_KEY` | OpenAI API key | Yes | - |
| `LLM_MODEL` | Model to use | No | `gpt-4o` |
| `LLM_PROVIDER` | Provider name | No | `openai` |
| `BRAVE_API_KEY` | Brave Search API key | Yes | - |
| `GMAIL_CREDENTIALS_FILE` | Gmail OAuth2 credentials | No | `credentials/credentials.json` |
| `LOG_LEVEL` | Logging level | No | `INFO` |
| `MAX_SEARCH_RESULTS` | Max search results | No | `10` |

### Model Providers

The system supports multiple LLM providers through environment configuration:

```python
# OpenAI (default)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4.1-mini

# Anthropic
LLM_PROVIDER=anthropic
LLM_MODEL=claude-4-sonnet-latest
```

## Security

### API Key Management
- Environment variables for sensitive data
- No hardcoded credentials in source code
- OAuth2 flow for Gmail authentication

### Input Validation
- Pydantic models validate all inputs
- Rate limiting prevents API abuse
- Error handling prevents information leakage

### Error Handling
- Comprehensive exception handling
- Graceful degradation on API failures
- Secure error messages without sensitive data

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with Pydantic AI** - Production-ready AI agents with type safety and structured outputs.