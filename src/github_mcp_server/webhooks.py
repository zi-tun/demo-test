"""Webhook handlers for GitHub events."""

import hashlib
import hmac
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel

from github_mcp_server.config import get_config


router = APIRouter()


class WebhookPayload(BaseModel):
    """Base webhook payload model."""
    action: str
    sender: Dict[str, Any]
    repository: Dict[str, Any]


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature."""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # GitHub sends the signature as 'sha256=<signature>'
    if signature.startswith('sha256='):
        signature = signature[7:]
    
    return hmac.compare_digest(expected_signature, signature)


async def process_webhook_event(event_type: str, payload: Dict[str, Any]):
    """Process GitHub webhook events in the background."""
    print(f"Processing webhook event: {event_type}")
    print(f"Action: {payload.get('action', 'N/A')}")
    print(f"Repository: {payload.get('repository', {}).get('full_name', 'N/A')}")
    
    # Add your webhook processing logic here
    # Examples:
    # - Update local cache
    # - Trigger automated workflows
    # - Send notifications
    # - Update database records


@router.post("/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Handle GitHub webhook events."""
    # Get webhook secret from environment
    # Get webhook secret from config
    config = get_config()
    webhook_secret = config.github_webhook_secret
    if not webhook_secret or webhook_secret == "your_webhook_secret_here":
        raise HTTPException(
            status_code=500,
            detail="GITHUB_WEBHOOK_SECRET not configured"
        )
    
    # Get headers
    signature = request.headers.get("X-Hub-Signature-256")
    event_type = request.headers.get("X-GitHub-Event")
    delivery_id = request.headers.get("X-GitHub-Delivery")
    
    if not signature or not event_type:
        raise HTTPException(
            status_code=400,
            detail="Missing required webhook headers"
        )
    
    # Get raw payload
    payload_bytes = await request.body()
    
    # Verify signature
    if not verify_webhook_signature(payload_bytes, signature, webhook_secret):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature"
        )
    
    # Parse JSON payload
    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON payload: {str(e)}"
        )
    
    # Process the webhook event in the background
    background_tasks.add_task(process_webhook_event, event_type, payload)
    
    return {
        "message": "Webhook received and queued for processing",
        "event_type": event_type,
        "delivery_id": delivery_id,
    }
