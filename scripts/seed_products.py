#!/usr/bin/env python3
"""Seed real IT products across all major categories."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.product import Product, Brand, Category
from slugify import slugify

PRODUCTS = [
    # ── Laptops ───────────────────────────────────────────────────────────────
    {
        "name": "HP Pavilion 15-eg3081TU",
        "brand": "HP", "category": "Laptops",
        "model_number": "15-eg3081TU",
        "description": "Intel Core i5-1335U, 16GB DDR4, 512GB SSD, 15.6\" FHD IPS, Intel Iris Xe, Windows 11 Home",
        "specifications": {"processor": "Intel Core i5-1335U", "ram": "16GB DDR4", "storage": "512GB NVMe SSD", "display": "15.6\" FHD IPS 250 nits", "os": "Windows 11 Home", "battery": "41Whr"},
        "base_price": 57990, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 12, "weight_kg": 1.75,
    },
    {
        "name": "HP EliteBook 840 G10",
        "brand": "HP", "category": "Laptops",
        "model_number": "840-G10-i7",
        "description": "Intel Core i7-1355U, 16GB DDR5, 512GB SSD, 14\" FHD IPS, Windows 11 Pro, Business Laptop",
        "specifications": {"processor": "Intel Core i7-1355U", "ram": "16GB DDR5", "storage": "512GB NVMe SSD", "display": "14\" FHD IPS", "os": "Windows 11 Pro", "ports": "Thunderbolt 4, USB-A, HDMI"},
        "base_price": 112000, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 36, "weight_kg": 1.38,
    },
    {
        "name": "Dell Inspiron 15 3530",
        "brand": "Dell", "category": "Laptops",
        "model_number": "INS-3530-i5",
        "description": "Intel Core i5-1335U, 8GB DDR4, 512GB SSD, 15.6\" FHD, Intel Iris Xe, Windows 11 Home",
        "specifications": {"processor": "Intel Core i5-1335U", "ram": "8GB DDR4 (upgradable to 32GB)", "storage": "512GB SSD", "display": "15.6\" FHD Anti-glare", "os": "Windows 11 Home"},
        "base_price": 52990, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 12, "weight_kg": 1.69,
    },
    {
        "name": "Dell Vostro 3430",
        "brand": "Dell", "category": "Laptops",
        "model_number": "VOT-3430-i5-W11P",
        "description": "Intel Core i5-1335U, 8GB RAM, 512GB SSD, 14\" FHD, Windows 11 Pro, Business",
        "specifications": {"processor": "Intel Core i5-1335U", "ram": "8GB DDR4", "storage": "512GB SSD", "display": "14\" FHD", "os": "Windows 11 Pro"},
        "base_price": 61500, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 12, "weight_kg": 1.56,
    },
    {
        "name": "Lenovo IdeaPad Slim 3 15IRU8",
        "brand": "Lenovo", "category": "Laptops",
        "model_number": "82X7008QIN",
        "description": "Intel Core i3-1305U, 8GB DDR4, 512GB SSD, 15.6\" FHD TN, Windows 11 Home",
        "specifications": {"processor": "Intel Core i3-1305U", "ram": "8GB DDR4", "storage": "512GB SSD", "display": "15.6\" FHD TN 300 nits", "os": "Windows 11 Home"},
        "base_price": 38990, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 12, "weight_kg": 1.62,
    },
    {
        "name": "Lenovo ThinkPad E14 Gen 5",
        "brand": "Lenovo", "category": "Laptops",
        "model_number": "21JKS0FP00",
        "description": "Intel Core i5-1335U, 16GB DDR4, 512GB SSD, 14\" FHD IPS, Windows 11 Pro, Business",
        "specifications": {"processor": "Intel Core i5-1335U", "ram": "16GB DDR4", "storage": "512GB SSD", "display": "14\" FHD IPS 300 nits", "os": "Windows 11 Pro", "ports": "USB-C, USB-A x2, HDMI, RJ45"},
        "base_price": 74990, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 36, "weight_kg": 1.57,
    },
    {
        "name": "Asus VivoBook 15 X1504VA",
        "brand": "Asus", "category": "Laptops",
        "model_number": "X1504VA-NJ522WS",
        "description": "Intel Core i5-1335U, 16GB DDR4, 512GB SSD, 15.6\" FHD OLED, Windows 11 Home",
        "specifications": {"processor": "Intel Core i5-1335U", "ram": "16GB DDR4", "storage": "512GB M.2 SSD", "display": "15.6\" FHD OLED 600 nits", "os": "Windows 11 Home"},
        "base_price": 61990, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 12, "weight_kg": 1.7,
    },
    {
        "name": "Apple MacBook Air M2 13\"",
        "brand": "Apple", "category": "Laptops",
        "model_number": "MLXY3HN/A",
        "description": "Apple M2 chip, 8GB Unified Memory, 256GB SSD, 13.6\" Liquid Retina, macOS",
        "specifications": {"processor": "Apple M2 (8-core CPU, 8-core GPU)", "ram": "8GB Unified Memory", "storage": "256GB SSD", "display": "13.6\" Liquid Retina 2560x1664", "os": "macOS Ventura", "battery": "Up to 18 hours"},
        "base_price": 99900, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 12, "weight_kg": 1.24,
    },

    # ── Desktops ──────────────────────────────────────────────────────────────
    {
        "name": "HP ProDesk 400 G9 Mini Desktop",
        "brand": "HP", "category": "Desktops",
        "model_number": "PD400G9-i5",
        "description": "Intel Core i5-12500T, 8GB DDR4, 256GB SSD, Mini Form Factor, Windows 11 Pro",
        "specifications": {"processor": "Intel Core i5-12500T", "ram": "8GB DDR4", "storage": "256GB SSD", "form_factor": "Mini PC", "os": "Windows 11 Pro", "ports": "USB-A x4, USB-C, DisplayPort x2, RJ45"},
        "base_price": 55000, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 12, "weight_kg": 1.3,
    },
    {
        "name": "Dell OptiPlex 3000 Tower",
        "brand": "Dell", "category": "Tower PC",
        "model_number": "OPX3000-i5-TWR",
        "description": "Intel Core i5-12500, 8GB DDR4, 256GB SSD + 1TB HDD, Windows 11 Pro, Tower",
        "specifications": {"processor": "Intel Core i5-12500", "ram": "8GB DDR4", "storage": "256GB SSD + 1TB HDD", "form_factor": "Tower", "os": "Windows 11 Pro"},
        "base_price": 58500, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 36, "weight_kg": 7.2,
    },
    {
        "name": "Lenovo IdeaCentre AIO 3 24",
        "brand": "Lenovo", "category": "All-in-One PC",
        "model_number": "F0FR00FHIN",
        "description": "Intel Core i5-12450H, 8GB DDR4, 512GB SSD, 23.8\" FHD Touch, Windows 11 Home",
        "specifications": {"processor": "Intel Core i5-12450H", "ram": "8GB DDR4", "storage": "512GB SSD", "display": "23.8\" FHD IPS Touch", "os": "Windows 11 Home"},
        "base_price": 72990, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 12, "weight_kg": 5.5,
    },

    # ── Monitors ──────────────────────────────────────────────────────────────
    {
        "name": "HP M24f FHD Monitor 24\"",
        "brand": "HP", "category": "Monitors",
        "model_number": "M24f-FHD",
        "description": "23.8\" FHD IPS, 75Hz, AMD FreeSync, HDMI + VGA, Tilt Adjustable",
        "specifications": {"display": "23.8\" FHD IPS", "resolution": "1920x1080", "refresh_rate": "75Hz", "ports": "HDMI, VGA", "response_time": "5ms"},
        "base_price": 13490, "gst_rate": 18.0, "hsn_code": "8528", "warranty_months": 36, "weight_kg": 3.4,
    },
    {
        "name": "Dell P2422H 24\" Professional Monitor",
        "brand": "Dell", "category": "Monitors",
        "model_number": "P2422H",
        "description": "23.8\" FHD IPS, 60Hz, Height/Tilt/Swivel/Pivot, USB Hub, HDMI + DisplayPort + VGA",
        "specifications": {"display": "23.8\" FHD IPS", "resolution": "1920x1080", "refresh_rate": "60Hz", "ports": "HDMI, DP, VGA, USB 3.0 hub", "adjustability": "Height, Tilt, Swivel, Pivot"},
        "base_price": 22990, "gst_rate": 18.0, "hsn_code": "8528", "warranty_months": 36, "weight_kg": 4.8,
    },
    {
        "name": "LG 27MP400-B 27\" FHD Monitor",
        "brand": "LG", "category": "Monitors",
        "model_number": "27MP400-B",
        "description": "27\" FHD IPS, AMD FreeSync, 75Hz, HDMI + VGA, Anti-glare",
        "specifications": {"display": "27\" FHD IPS", "resolution": "1920x1080", "refresh_rate": "75Hz", "ports": "HDMI x2, VGA"},
        "base_price": 17490, "gst_rate": 18.0, "hsn_code": "8528", "warranty_months": 36, "weight_kg": 4.2,
    },

    # ── Printers ──────────────────────────────────────────────────────────────
    {
        "name": "HP LaserJet MFP M140we",
        "brand": "HP", "category": "Multifunction Printer",
        "model_number": "7MD72E",
        "description": "Mono Laser MFP, Print/Scan/Copy, WiFi, USB, 20 ppm, HP+ Instant Ink",
        "specifications": {"type": "Mono Laser MFP", "speed": "20 ppm", "connectivity": "WiFi, USB", "scan": "Flatbed 1200 dpi", "paper": "A4"},
        "base_price": 10490, "gst_rate": 18.0, "hsn_code": "8443", "warranty_months": 12, "weight_kg": 5.1,
    },
    {
        "name": "HP LaserJet Pro M404dn",
        "brand": "HP", "category": "Laser Printer",
        "model_number": "W1A53A",
        "description": "Mono Laser Printer, 38 ppm, Auto Duplex, LAN + USB, 1200 dpi, for workgroups",
        "specifications": {"type": "Mono Laser", "speed": "38 ppm", "connectivity": "Ethernet, USB", "duplex": "Auto", "resolution": "1200 dpi"},
        "base_price": 22990, "gst_rate": 18.0, "hsn_code": "8443", "warranty_months": 12, "weight_kg": 7.6,
    },
    {
        "name": "Epson EcoTank L3250",
        "brand": "Epson", "category": "Multifunction Printer",
        "model_number": "C11CJ67502",
        "description": "Color Inkjet MFP, Print/Scan/Copy, WiFi + USB, 33 ppm mono, EcoTank refillable",
        "specifications": {"type": "Color Inkjet MFP", "speed": "33 ppm mono / 15 ppm color", "connectivity": "WiFi, USB", "ink": "EcoTank refillable"},
        "base_price": 14990, "gst_rate": 18.0, "hsn_code": "8443", "warranty_months": 12, "weight_kg": 3.9,
    },
    {
        "name": "Canon PIXMA G3770",
        "brand": "Canon", "category": "Multifunction Printer",
        "model_number": "G3770-BLK",
        "description": "Color MegaTank MFP, WiFi, Print/Scan/Copy, borderless photo printing",
        "specifications": {"type": "Color MegaTank MFP", "speed": "11 ipm mono / 6 ipm color", "connectivity": "WiFi, USB", "scan": "Flatbed CIS"},
        "base_price": 13499, "gst_rate": 18.0, "hsn_code": "8443", "warranty_months": 12, "weight_kg": 3.5,
    },
    {
        "name": "Brother DCP-T426W",
        "brand": "Brother", "category": "Multifunction Printer",
        "model_number": "DCPT426W",
        "description": "Color Inkjet MFP, WiFi, Print/Scan/Copy, INKvestment Tank, 27 ppm",
        "specifications": {"type": "Color Inkjet MFP", "speed": "27 ipm mono / 26 ipm color", "connectivity": "WiFi, USB", "ink": "INKvestment refill tank"},
        "base_price": 12490, "gst_rate": 18.0, "hsn_code": "8443", "warranty_months": 12, "weight_kg": 7.3,
    },

    # ── Networking ────────────────────────────────────────────────────────────
    {
        "name": "TP-Link TL-SF1008D 8-Port Switch",
        "brand": "TP-Link", "category": "Switches",
        "model_number": "TL-SF1008D",
        "description": "8-Port 10/100Mbps Unmanaged Desktop Switch, plug and play, QoS",
        "specifications": {"ports": "8x 10/100Mbps", "type": "Unmanaged", "switching_capacity": "1.6 Gbps"},
        "base_price": 699, "gst_rate": 18.0, "hsn_code": "8517", "warranty_months": 36, "weight_kg": 0.28,
    },
    {
        "name": "TP-Link TL-SG1024D 24-Port Gigabit Switch",
        "brand": "TP-Link", "category": "Switches",
        "model_number": "TL-SG1024D",
        "description": "24-Port Gigabit Unmanaged Desktop/Rackmount Switch, 48 Gbps switching capacity",
        "specifications": {"ports": "24x 1Gbps", "type": "Unmanaged", "switching_capacity": "48 Gbps", "mounting": "Desktop / Rack"},
        "base_price": 4299, "gst_rate": 18.0, "hsn_code": "8517", "warranty_months": 36, "weight_kg": 1.4,
    },
    {
        "name": "Cisco SG350-10 10-Port Managed Switch",
        "brand": "Cisco", "category": "Switches",
        "model_number": "SG350-10-K9-IN",
        "description": "10-Port Gigabit Managed Switch, 2 Combo SFP, Web UI + CLI, VLAN, QoS",
        "specifications": {"ports": "8x 1Gbps + 2x Combo SFP", "type": "Managed", "features": "VLAN, QoS, LACP, Spanning Tree"},
        "base_price": 18500, "gst_rate": 18.0, "hsn_code": "8517", "warranty_months": 36, "weight_kg": 1.8,
    },
    {
        "name": "TP-Link Archer AX73 WiFi 6 Router",
        "brand": "TP-Link", "category": "Routers",
        "model_number": "Archer AX73",
        "description": "AX5400 WiFi 6 Dual-Band Router, 4x Antennas, MU-MIMO, OFDMA, USB 3.0",
        "specifications": {"standard": "WiFi 6 (802.11ax)", "speed": "AX5400 (574+4804 Mbps)", "antennas": "6x External", "ports": "4x Gigabit LAN + 1x WAN, USB 3.0"},
        "base_price": 9499, "gst_rate": 18.0, "hsn_code": "8517", "warranty_months": 24, "weight_kg": 0.72,
    },
    {
        "name": "D-Link DAP-2610 Access Point",
        "brand": "D-Link", "category": "Access Points",
        "model_number": "DAP-2610",
        "description": "AC1300 Wave 2 Dual-Band PoE Access Point, MU-MIMO, ceiling mount",
        "specifications": {"standard": "802.11ac Wave 2", "speed": "AC1300", "poe": "802.3at PoE", "mounting": "Ceiling / Wall"},
        "base_price": 7499, "gst_rate": 18.0, "hsn_code": "8517", "warranty_months": 24, "weight_kg": 0.35,
    },

    # ── Storage ───────────────────────────────────────────────────────────────
    {
        "name": "Samsung 870 EVO 500GB SATA SSD",
        "brand": "Samsung", "category": "SSDs",
        "model_number": "MZ-77E500B/IN",
        "description": "500GB 2.5\" SATA III SSD, 560MB/s Read, 530MB/s Write, V-NAND",
        "specifications": {"capacity": "500GB", "interface": "SATA III 6Gbps", "read": "560 MB/s", "write": "530 MB/s", "form_factor": "2.5\""},
        "base_price": 4999, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 60, "weight_kg": 0.054,
    },
    {
        "name": "Samsung 870 EVO 1TB SATA SSD",
        "brand": "Samsung", "category": "SSDs",
        "model_number": "MZ-77E1T0B/IN",
        "description": "1TB 2.5\" SATA III SSD, 560MB/s Read, 530MB/s Write, V-NAND",
        "specifications": {"capacity": "1TB", "interface": "SATA III 6Gbps", "read": "560 MB/s", "write": "530 MB/s", "form_factor": "2.5\""},
        "base_price": 8999, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 60, "weight_kg": 0.054,
    },
    {
        "name": "Seagate Backup Plus 1TB External HDD",
        "brand": "Samsung", "category": "External Hard Drives",
        "model_number": "STDR1000300",
        "description": "1TB USB 3.0 Portable External Hard Drive, 2.5\", Windows & Mac compatible",
        "specifications": {"capacity": "1TB", "interface": "USB 3.0", "form_factor": "2.5\" Portable"},
        "base_price": 3299, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 24, "weight_kg": 0.15,
    },
    {
        "name": "HP x5600C 128GB USB Pen Drive",
        "brand": "HP", "category": "Pen Drives",
        "model_number": "HPFD5600C-128",
        "description": "128GB USB-C + USB-A Dual Interface Flash Drive, USB 3.2, 100MB/s read",
        "specifications": {"capacity": "128GB", "interface": "USB 3.2 + USB-C", "read": "100 MB/s"},
        "base_price": 999, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 12, "weight_kg": 0.02,
    },

    # ── Accessories ───────────────────────────────────────────────────────────
    {
        "name": "Logitech MK275 Wireless Keyboard & Mouse Combo",
        "brand": "HP", "category": "Keyboards & Mouse",
        "model_number": "MK275",
        "description": "2.4GHz Wireless Keyboard and Mouse combo, Nano USB receiver, 24-month battery",
        "specifications": {"connectivity": "2.4GHz Wireless", "range": "10m", "battery": "24 months (keyboard), 12 months (mouse)"},
        "base_price": 1595, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 36, "weight_kg": 0.83,
    },
    {
        "name": "Dell KM3322W Wireless Keyboard & Mouse",
        "brand": "Dell", "category": "Keyboards & Mouse",
        "model_number": "KM3322W",
        "description": "Wireless Keyboard and Mouse combo, 2.4GHz, Quiet keys, 36-month battery life",
        "specifications": {"connectivity": "2.4GHz Wireless", "range": "10m", "battery": "36 months keyboard"},
        "base_price": 2699, "gst_rate": 18.0, "hsn_code": "8471", "warranty_months": 36, "weight_kg": 0.74,
    },
    {
        "name": "Lenovo 300 FHD Webcam",
        "brand": "Lenovo", "category": "Webcams",
        "model_number": "GXC1B34793",
        "description": "1080p FHD USB Webcam, built-in microphone, privacy shutter, plug and play",
        "specifications": {"resolution": "1920x1080 @ 30fps", "connectivity": "USB-A", "mic": "Built-in mono", "fov": "90°"},
        "base_price": 2499, "gst_rate": 18.0, "hsn_code": "8525", "warranty_months": 12, "weight_kg": 0.09,
    },
    {
        "name": "HP DHE-8001 Over-Ear Headset",
        "brand": "HP", "category": "Headphones",
        "model_number": "DHE-8001",
        "description": "Wired Over-Ear Headset with Mic, 3.5mm + USB, noise-cancelling mic, for calls",
        "specifications": {"connectivity": "3.5mm + USB", "type": "Over-Ear", "mic": "Noise-cancelling boom"},
        "base_price": 1299, "gst_rate": 18.0, "hsn_code": "8518", "warranty_months": 12, "weight_kg": 0.24,
    },
    {
        "name": "Dell EcoLoop Pro Laptop Bag 15\"",
        "brand": "Dell", "category": "Bags & Cases",
        "model_number": "460-BDLI",
        "description": "15.6\" Laptop Bag, recycled material, padded compartment, shoulder strap",
        "specifications": {"fits": "Up to 15.6\" laptop", "material": "Recycled PET", "pockets": "Multiple organizer pockets"},
        "base_price": 2499, "gst_rate": 18.0, "hsn_code": "4202", "warranty_months": 12, "weight_kg": 0.65,
    },
]


def main():
    db = SessionLocal()
    try:
        brand_map = {b.name: b.id for b in db.query(Brand).all()}
        cat_map = {c.name: c.id for c in db.query(Category).all()}

        added = 0
        skipped = 0
        for p in PRODUCTS:
            brand_id = brand_map.get(p["brand"])
            cat_id = cat_map.get(p["category"])

            if not brand_id:
                print(f"  SKIP (no brand): {p['name']}")
                skipped += 1
                continue
            if not cat_id:
                print(f"  SKIP (no category): {p['name']} — {p['category']}")
                skipped += 1
                continue

            existing = db.query(Product).filter_by(model_number=p["model_number"]).first()
            if existing:
                skipped += 1
                continue

            product = Product(
                brand_id=brand_id,
                category_id=cat_id,
                name=p["name"],
                slug=slugify(p["name"]),
                description=p["description"],
                specifications=p.get("specifications"),
                base_price=p["base_price"],
                gst_rate=p["gst_rate"],
                hsn_code=p.get("hsn_code"),
                model_number=p["model_number"],
                warranty_months=p.get("warranty_months", 12),
                weight_kg=p.get("weight_kg"),
                is_active=True,
                is_approved=True,
            )
            db.add(product)
            added += 1
            print(f"  + {p['name']}")

        db.commit()
        print(f"\nDone. Added: {added}, Skipped: {skipped}")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
