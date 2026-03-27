import structlog
import stripe
from fastapi import APIRouter, Header, HTTPException, Request

from app.config import settings
from app.services.billing import handle_stripe_event

log = structlog.get_logger()
router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="stripe-signature"),
) -> dict:
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    log.info("stripe_webhook_received", event_type=event["type"])
    await handle_stripe_event(event)
    return {"received": True}
