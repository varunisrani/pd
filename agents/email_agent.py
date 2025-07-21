"""Email Agent with Gmail integration and professional email generation."""

import base64
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic_ai import Agent, RunContext

from .dependencies import EmailAgentDependencies
from .models import EmailDraft, ResearchSummary
from .providers import get_llm_model

# Configure logging
logger = logging.getLogger(__name__)

# Email agent with structured output for professional emails
email_agent = Agent(
    get_llm_model(),
    deps_type=EmailAgentDependencies,
    output_type=EmailDraft,
    system_prompt="""You are a professional email composition agent. Your role is to create well-structured, 
    professional emails based on research findings and user requirements.

    Guidelines:
    - Use clear, professional language appropriate for business communication
    - Structure emails with proper greeting, body, and closing
    - Include relevant research insights and key findings
    - Maintain appropriate tone (formal, semi-formal, or casual as requested if applicable)
    - Include source references when requested
    - Keep emails concise but informative
    - Use proper email etiquette and formatting
    
    Always return a properly formatted EmailDraft with all required fields."""
)


@email_agent.tool
async def authenticate_gmail(ctx: RunContext[EmailAgentDependencies]) -> str:
    """Authenticate with Gmail API using OAuth2."""
    
    deps = ctx.deps
    creds = None
    
    try:
        # Load existing token if available
        if hasattr(deps, 'token_file') and deps.token_file:
            try:
                creds = Credentials.from_authorized_user_file(deps.token_file, deps.scopes)
            except Exception as e:
                logger.warning(f"Could not load existing token: {e}")
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    deps.credentials_file, deps.scopes
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            if hasattr(deps, 'token_file') and deps.token_file:
                with open(deps.token_file, 'w') as token:
                    token.write(creds.to_json())
        
        return "Successfully authenticated with Gmail API"
        
    except Exception as e:
        logger.error(f"Gmail authentication failed: {e}")
        raise RuntimeError(f"Gmail authentication failed: {e}")

@email_agent.tool
async def create_gmail_draft(
    ctx: RunContext[EmailAgentDependencies],
    email_draft: EmailDraft
) -> str:
    """Create a draft in Gmail without sending."""
    
    try:
        # Authenticate first
        await authenticate_gmail(ctx)
        
        # Build credentials and service
        deps = ctx.deps
        creds = Credentials.from_authorized_user_file(deps.token_file, deps.scopes)
        service = build('gmail', 'v1', credentials=creds)
        
        # Create message
        message = MIMEMultipart()
        message['to'] = ', '.join(email_draft.to)
        message['subject'] = email_draft.subject
        
        if email_draft.cc:
            message['cc'] = ', '.join(email_draft.cc)
        if email_draft.bcc:
            message['bcc'] = ', '.join(email_draft.bcc)
        
        # Add body
        body_part = MIMEText(email_draft.body, 'plain')
        message.attach(body_part)
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Create draft
        draft_body = {'message': {'raw': raw_message}}
        draft_result = service.users().drafts().create(
            userId='me',
            body=draft_body
        ).execute()
        
        draft_id = draft_result.get('id')
        logger.info(f"Draft created successfully with ID: {draft_id}")
        
        return f"Draft created successfully (Draft ID: {draft_id}). You can review and send it from Gmail."
        
    except HttpError as e:
        logger.error(f"Gmail API error creating draft: {e}")
        raise RuntimeError(f"Failed to create Gmail draft: {e}")
    except Exception as e:
        logger.error(f"Unexpected error creating draft: {e}")
        raise RuntimeError(f"Failed to create draft: {e}")
