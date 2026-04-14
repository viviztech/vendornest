"""Delhivery courier API integration."""
import httpx
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

BASE_URL = settings.delhivery_base_url
HEADERS = {
    "Authorization": f"Token {settings.delhivery_api_key}",
    "Content-Type": "application/json",
}


def check_serviceability(pincode: str) -> dict:
    """Check if Delhivery serves a pincode."""
    try:
        r = httpx.get(
            f"{BASE_URL}/c/api/pin-codes/json/",
            params={"filter_codes": pincode},
            headers=HEADERS,
            timeout=10,
        )
        data = r.json()
        delivery_codes = data.get("delivery_codes", [])
        if delivery_codes:
            info = delivery_codes[0].get("postal_code", {})
            return {
                "serviceable": info.get("pre_paid") == "Y",
                "cod": info.get("cash_on_delivery") == "Y",
                "city": info.get("city"),
                "state": info.get("state_code"),
            }
        return {"serviceable": False}
    except Exception as e:
        logger.error(f"Delhivery serviceability error: {e}")
        return {"serviceable": False, "error": str(e)}


def create_shipment(order_data: dict) -> Optional[dict]:
    """
    Create a shipment in Delhivery.
    order_data: {
        order_number, name, phone, address, city, pincode, state,
        weight_kg, products (list), cod_amount (0 if prepaid)
    }
    """
    payload = {
        "format": "json",
        "data": {
            "shipments": [{
                "name": order_data["name"],
                "add": order_data["address"],
                "city": order_data["city"],
                "state": order_data["state"],
                "country": "India",
                "pin": order_data["pincode"],
                "phone": order_data["phone"],
                "order": order_data["order_number"],
                "payment_mode": "Prepaid" if order_data.get("cod_amount", 0) == 0 else "COD",
                "return_pin": "",
                "return_city": "",
                "return_phone": "",
                "return_add": "",
                "return_state": "",
                "return_country": "India",
                "products_desc": ", ".join(order_data.get("products", [])),
                "hsn_code": "",
                "cod_amount": order_data.get("cod_amount", 0),
                "order_date": order_data.get("order_date", ""),
                "total_amount": order_data.get("total_amount", 0),
                "seller_add": "",
                "seller_name": "VendorNest",
                "seller_inv": order_data["order_number"],
                "quantity": str(order_data.get("quantity", 1)),
                "waybill": "",
                "shipment_width": "",
                "shipment_height": "",
                "weight": str(order_data.get("weight_kg", 0.5)),
                "seller_gst_tin": "",
                "shipping_mode": "Surface",
                "address_type": "home",
            }],
            "pickup_location": {"name": settings.delhivery_pickup_location},
        }
    }
    try:
        r = httpx.post(
            f"{BASE_URL}/api/cmu/create.json",
            headers=HEADERS,
            json=payload,
            timeout=15,
        )
        return r.json()
    except Exception as e:
        logger.error(f"Delhivery create_shipment error: {e}")
        return None


def track_shipment(waybill: str) -> Optional[dict]:
    """Get tracking info for an AWB/waybill."""
    try:
        r = httpx.get(
            f"{BASE_URL}/api/v1/packages/json/",
            params={"waybill": waybill},
            headers=HEADERS,
            timeout=10,
        )
        data = r.json()
        packages = data.get("ShipmentData", [])
        if packages:
            return packages[0].get("Shipment", {})
        return None
    except Exception as e:
        logger.error(f"Delhivery track error: {e}")
        return None


def cancel_shipment(waybill: str) -> bool:
    """Cancel a shipment before pickup."""
    try:
        r = httpx.post(
            f"{BASE_URL}/api/p/edit",
            headers=HEADERS,
            data={"waybill": waybill, "cancellation": "true"},
            timeout=10,
        )
        return r.status_code == 200
    except Exception as e:
        logger.error(f"Delhivery cancel error: {e}")
        return False
