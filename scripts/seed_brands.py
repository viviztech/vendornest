#!/usr/bin/env python3
"""Seed default hardware brands and categories."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.product import Brand, Category
from python_slugify import slugify

BRANDS = [
    {"name": "HP", "description": "Hewlett-Packard products"},
    {"name": "Dell", "description": "Dell Technologies products"},
    {"name": "Lenovo", "description": "Lenovo products"},
    {"name": "Acer", "description": "Acer products"},
    {"name": "Asus", "description": "Asus products"},
    {"name": "Apple", "description": "Apple products"},
    {"name": "Samsung", "description": "Samsung electronics"},
    {"name": "Sony", "description": "Sony products"},
    {"name": "LG", "description": "LG electronics"},
    {"name": "Canon", "description": "Canon printers and cameras"},
    {"name": "Epson", "description": "Epson printers"},
    {"name": "Brother", "description": "Brother printers"},
    {"name": "Cisco", "description": "Cisco networking"},
    {"name": "D-Link", "description": "D-Link networking"},
    {"name": "TP-Link", "description": "TP-Link networking"},
]

CATEGORIES = [
    {"name": "Laptops", "name_ta": "மடிக்கணினிகள்", "name_hi": "लैपटॉप", "children": []},
    {"name": "Desktops", "name_ta": "டெஸ்க்டாப்", "name_hi": "डेस्कटॉप", "children": [
        {"name": "All-in-One PC", "name_ta": "ஆல்-இன்-ஒன் பிசி", "name_hi": "ऑल-इन-वन पीसी"},
        {"name": "Tower PC", "name_ta": "டவர் பிசி", "name_hi": "टॉवर पीसी"},
    ]},
    {"name": "Printers", "name_ta": "அச்சுப்பொறிகள்", "name_hi": "प्रिंटर", "children": [
        {"name": "Laser Printer", "name_ta": "லேசர் அச்சுப்பொறி", "name_hi": "लेजर प्रिंटर"},
        {"name": "Inkjet Printer", "name_ta": "இன்க்ஜெட் அச்சுப்பொறி", "name_hi": "इंकजेट प्रिंटर"},
        {"name": "Multifunction Printer", "name_ta": "பல்செயல் அச்சுப்பொறி", "name_hi": "मल्टीफंक्शन प्रिंटर"},
    ]},
    {"name": "Monitors", "name_ta": "மானிட்டர்கள்", "name_hi": "मॉनिटर", "children": []},
    {"name": "Networking", "name_ta": "நெட்வொர்க்கிங்", "name_hi": "नेटवर्किंग", "children": [
        {"name": "Routers", "name_ta": "ரூட்டர்கள்", "name_hi": "राउटर"},
        {"name": "Switches", "name_ta": "சுவிட்சுகள்", "name_hi": "स्विच"},
        {"name": "Access Points", "name_ta": "அணுகல் புள்ளிகள்", "name_hi": "एक्सेस पॉइंट"},
    ]},
    {"name": "Storage", "name_ta": "சேமிப்பு", "name_hi": "स्टोरेज", "children": [
        {"name": "External Hard Drives", "name_ta": "வெளிப்புற ஹார்ட் டிரைவ்கள்", "name_hi": "एक्सटर्नल हार्ड ड्राइव"},
        {"name": "Pen Drives", "name_ta": "பேன் டிரைவ்கள்", "name_hi": "पेन ड्राइव"},
        {"name": "SSDs", "name_ta": "எஸ்எஸ்டி", "name_hi": "एसएसडी"},
    ]},
    {"name": "Accessories", "name_ta": "மேலதிக சாதனங்கள்", "name_hi": "एक्सेसरीज", "children": [
        {"name": "Keyboards & Mouse", "name_ta": "கீபோர்டு & மவுஸ்", "name_hi": "कीबोर्ड और माउस"},
        {"name": "Webcams", "name_ta": "வெப்கேம்கள்", "name_hi": "वेबकैम"},
        {"name": "Headphones", "name_ta": "ஹெட்போன்கள்", "name_hi": "हेडफोन"},
        {"name": "Bags & Cases", "name_ta": "பைகள்", "name_hi": "बैग"},
    ]},
    {"name": "Servers & Workstations", "name_ta": "சேவையகங்கள்", "name_hi": "सर्वर", "children": []},
    {"name": "Spare Parts", "name_ta": "உதிரி பாகங்கள்", "name_hi": "स्पेयर पार्ट्स", "children": []},
]

def main():
    db = SessionLocal()
    try:
        # Brands
        for b in BRANDS:
            existing = db.query(Brand).filter_by(name=b["name"]).first()
            if not existing:
                db.add(Brand(name=b["name"], slug=slugify(b["name"]), description=b["description"]))
        db.commit()
        print(f"Seeded {len(BRANDS)} brands.")

        # Categories
        count = 0
        for cat in CATEGORIES:
            parent = db.query(Category).filter_by(name=cat["name"]).first()
            if not parent:
                parent = Category(
                    name=cat["name"],
                    name_ta=cat.get("name_ta"),
                    name_hi=cat.get("name_hi"),
                    slug=slugify(cat["name"]),
                )
                db.add(parent)
                db.flush()
                count += 1
            for child in cat.get("children", []):
                existing = db.query(Category).filter_by(name=child["name"]).first()
                if not existing:
                    db.add(Category(
                        name=child["name"],
                        name_ta=child.get("name_ta"),
                        name_hi=child.get("name_hi"),
                        slug=slugify(child["name"]),
                        parent_id=parent.id,
                    ))
                    count += 1
        db.commit()
        print(f"Seeded {count} categories.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
