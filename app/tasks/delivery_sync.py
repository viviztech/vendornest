"""Celery task: sync Delhivery shipment status for all active orders."""
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.order import Order, OrderTracking, OrderStatus
from app.services.delivery import track_shipment
import logging

logger = logging.getLogger(__name__)

DELHIVERY_TO_ORDER_STATUS = {
    "Manifested": OrderStatus.dispatched,
    "In Transit": OrderStatus.dispatched,
    "Out for Delivery": OrderStatus.out_for_delivery,
    "Delivered": OrderStatus.delivered,
}


@celery_app.task(name="sync_delhivery_status")
def sync_delhivery_status():
    db = SessionLocal()
    try:
        active_orders = db.query(Order).filter(
            Order.delhivery_awb.isnot(None),
            Order.status.notin_([OrderStatus.delivered, OrderStatus.cancelled, OrderStatus.refunded]),
        ).all()

        updated = 0
        for order in active_orders:
            shipment = track_shipment(order.delhivery_awb)
            if not shipment:
                continue
            dl_status = shipment.get("Status", {}).get("Status", "")
            new_status = DELHIVERY_TO_ORDER_STATUS.get(dl_status)
            if new_status and order.status != new_status:
                order.status = new_status
                db.add(OrderTracking(
                    order_id=order.id,
                    status=new_status,
                    description=f"Delhivery: {dl_status}",
                    source="delhivery",
                ))
                updated += 1

        db.commit()
        logger.info(f"Delhivery sync: updated {updated} orders.")
        return updated
    finally:
        db.close()
