# PydanticAI Research & Email Agent

AI agent system built with PydanticAI that combines web research (Brave Search) with Gmail draft creation, plus a streaming CLI built on Rich.

## Highlights

- **Research + Email**: Research with Brave, draft emails in Gmail
- **Streaming CLI**: Real‑time output using `.iter()`
- **Config first**: Environment‑based settings via pydantic‑settings and python‑dotenv
- **Testable**: Mockable agents and utilities with a small test suite

## Quick start

1) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Add minimal environment variables in a `.env` file

```bash
# LLM
LLM_API_KEY=your-openai-key
LLM_MODEL=gpt-4o

# Brave Search
BRAVE_API_KEY=your-brave-key

# Gmail (optional for email features)
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.pickle
```

4) (Optional) Authorize Gmail

```bash
python gmail_setup.py
```

5) Run the CLI

```bash
python research_email_cli.py
```

Example prompts:
- "Research AI safety trends and email summary to john@company.com"
- "Create email draft about market analysis for jane@firm.com"

## Project layout

```
agents/                # PydanticAI agents (research, email)
config/                # Settings and model providers
models/                # Pydantic models
tools/                 # Brave Search + Gmail tools
tests/                 # Test suite
research_email_cli.py  # Streaming CLI
```

## Testing

```bash
pytest -q
```

## Notes

- Do not commit `credentials.json` or `token.pickle`
- Rate limits apply for Brave Search and Gmail APIs
- See `AGENTS.md` for development principles and patterns

## Learn more

- PydanticAI docs: https://ai.pydantic.dev/
- Brave Search API: https://brave.com/search/api/
- Gmail API (Python): https://developers.google.com/workspace/gmail/api/quickstart/python