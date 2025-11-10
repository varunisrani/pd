Aligned Gmail token path defaults with the OAuth flow so every config, doc, and test now expects `token.json`.

- Updated environment defaults to `token.json` in `.env.example:12`, `config/settings.py:39`, and `examples/main_agent_reference/settings.py:38` so generated tokens match configuration.
- Synced helper scripts and docs—including `gmail_setup.py:154`, `README.md:124`, and `PRPs/research-email-agent-cli.md:845`—to reference `token.json` and keep security reminders accurate.
- Adjusted dependency fixtures and assertions in `tests/test_email_agent.py:18` and `tests/test_research_agent.py:19` so test expectations stay consistent with the new default.

Testing: `pytest tests/test_email_agent.py tests/test_research_agent.py` *(fails: `pytest` is not installed in this runner—install it before re-running).*