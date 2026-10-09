from datetime import datetime, timezone
import logging
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

@tool
def send_notification(
    recipient: str = "operations@company.com",
    subject: str = "Workflow Notification",
    message: str = "Workflow completed successfully.",
    channel: str = "email",
    **kwargs,
) -> dict:
    """Simulate sending an alert or notification to a team."""
    current_time = datetime.now(timezone.utc).isoformat()
    logger.info(f"[{channel.upper()}] To: {recipient} | Subject: {subject}")

    return {
        "delivery_status": "sent",
        "channel": channel,
        "recipient": recipient,
        "subject": subject,
        "timestamp": current_time,
    }

@tool
def generate_restock_list(
    items: list = None,
    order_id_prefix: str = "PO-AUTO",
    **kwargs,
) -> dict:
    """Generate a draft purchase order structure from low-stock items."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    purchase_order_id = f"{order_id_prefix}-{timestamp}"
    restock_items = items or []

    return {
        "purchase_order_id": purchase_order_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "item_count": len(restock_items),
        "items": restock_items,
        "status": "draft_created",
    }

@tool
def export_report(
    data=None,
    report_title: str = "Workflow Execution Report",
    format_type: str = "json",
    **kwargs,
) -> dict:
    """Simulate saving an exported summary report."""
    record_count = len(data) if isinstance(data, list) else 1

    return {
        "status": "exported",
        "report_title": report_title,
        "format": format_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "record_count": record_count,
    }