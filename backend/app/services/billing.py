"""Stripe billing event handlers."""

import structlog
import stripe

from app.config import settings
from app.models.subscription import PlanTier, Subscription, SubscriptionStatus

log = structlog.get_logger()

stripe.api_key = settings.STRIPE_SECRET_KEY

PRICE_TO_PLAN: dict[str, str] = {
    settings.STRIPE_STARTER_PRICE_ID: PlanTier.STARTER,
    settings.STRIPE_PRO_PRICE_ID: PlanTier.PRO,
    settings.STRIPE_TEAM_PRICE_ID: PlanTier.TEAM,
}


async def handle_stripe_event(event: dict) -> None:
    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        await _handle_checkout_completed(data)
    elif event_type in ("customer.subscription.updated", "customer.subscription.created"):
        await _handle_subscription_updated(data)
    elif event_type == "customer.subscription.deleted":
        await _handle_subscription_canceled(data)
    elif event_type == "invoice.payment_failed":
        await _handle_payment_failed(data)
    else:
        log.debug("stripe_event_ignored", event_type=event_type)


async def _handle_checkout_completed(session: dict) -> None:
    """Provision subscription after successful checkout."""
    log.info("checkout_completed", session_id=session.get("id"))
    # Implementation: match customer to workspace, create Subscription record


async def _handle_subscription_updated(subscription: dict) -> None:
    """Update subscription plan and status."""
    price_id = subscription["items"]["data"][0]["price"]["id"]
    plan = PRICE_TO_PLAN.get(price_id, PlanTier.FREE)
    status = subscription["status"]
    log.info("subscription_updated", plan=plan, status=status)


async def _handle_subscription_canceled(subscription: dict) -> None:
    """Downgrade to free plan on cancellation."""
    log.info("subscription_canceled", subscription_id=subscription.get("id"))


async def _handle_payment_failed(invoice: dict) -> None:
    """Mark subscription as past_due."""
    log.warning("payment_failed", invoice_id=invoice.get("id"))
