# PydanticAI Research & Email Agent System

AI agent system that combines web research with Gmail email drafting. Features automated AI-powered issue fixing and PR reviews.

## 🚀 Features

- **Web Research**: Brave Search API integration
- **Email Drafting**: Gmail OAuth2 with automated draft creation  
- **Streaming CLI**: Real-time output using Rich and PydanticAI
- **AI Workflows**: `@claude-fix`, `@codex-fix`, `@cursor-fix` for automated issue handling

## 🤖 AI Coding Assistants

Mention AI assistants in issues/PRs to trigger automated workflows:

- **Commands**: `@claude-fix`, `@codex-fix`, `@cursor-fix` (and `*-review` variants)
- **Setup**: Add `CLAUDE_CODE_OAUTH_TOKEN`, `OPENAI_API_KEY`, `CURSOR_API_KEY` to repository secrets
- **Workflows**: Located in `.github/workflows/[claude_code|codex|cursor]/`

## 🏗️ Architecture

```
agents/          # PydanticAI agents (research + email)
config/          # Settings and LLM providers  
models/          # Pydantic data models
tools/           # Brave Search + Gmail OAuth2
research_email_cli.py  # Main CLI
```

## 📋 Prerequisites

- **Python 3.11+**
- **API Keys**: OpenAI, Brave Search  
- **Gmail OAuth2**: Google Cloud project with Gmail API

## 🛠️ Quick Start

```bash
git clone <repository-url>
cd PydanticAI-Research-Agent
python3 -m venv venv && source venv/bin/activate
pip install 'pydantic-ai-slim[openai]' httpx rich python-dotenv google-auth google-auth-oauthlib google-api-python-client
cp .env.example .env  # Add your API keys
python gmail_setup.py  # Gmail OAuth2 setup
python research_email_cli.py  # Run the CLI
```

## ⚙️ Configuration

Create `.env` with:
```bash
LLM_API_KEY=your-openai-key
BRAVE_API_KEY=your-brave-key
GMAIL_CREDENTIALS_PATH=credentials.json
```

Gmail setup: [Google Cloud Console](https://console.cloud.google.com) → Enable Gmail API → Create OAuth2 credentials → `python gmail_setup.py`

## 🎯 Usage

**CLI**: `python research_email_cli.py`

**Example queries**: 
- "Research AI safety trends and email summary to john@company.com"
- "Find quantum computing developments"

## 🧪 Testing

```bash
python -m pytest tests/ -v
```

Tests use TestModel for validation without external API calls.

## 📚 Learn More

- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [Brave Search API](https://brave.com/search/api/)
- [Gmail API Python Quickstart](https://developers.google.com/workspace/gmail/api/quickstart/python)

---

Built with ❤️ using [PydanticAI](https://ai.pydantic.dev/) and following production-ready development practices.