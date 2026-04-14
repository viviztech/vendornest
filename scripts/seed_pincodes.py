#!/usr/bin/env python3
"""
Seed all India pincodes from India Post CSV data.
Download CSV from: https://www.indiapost.gov.in/VAS/Pages/FindPinCode.aspx
Or use the bundled data/india_pincodes.csv

Usage: python scripts/seed_pincodes.py
"""

import sys
import os
import csv
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.location import State, District, Taluk, Pincode

# Fallback: Embed top 50 states + sample pincodes for quick start
STATES_DATA = [
    {"name": "Andhra Pradesh", "code": "AP"},
    {"name": "Arunachal Pradesh", "code": "AR"},
    {"name": "Assam", "code": "AS"},
    {"name": "Bihar", "code": "BR"},
    {"name": "Chhattisgarh", "code": "CG"},
    {"name": "Goa", "code": "GA"},
    {"name": "Gujarat", "code": "GJ"},
    {"name": "Haryana", "code": "HR"},
    {"name": "Himachal Pradesh", "code": "HP"},
    {"name": "Jharkhand", "code": "JH"},
    {"name": "Karnataka", "code": "KA"},
    {"name": "Kerala", "code": "KL"},
    {"name": "Madhya Pradesh", "code": "MP"},
    {"name": "Maharashtra", "code": "MH"},
    {"name": "Manipur", "code": "MN"},
    {"name": "Meghalaya", "code": "ML"},
    {"name": "Mizoram", "code": "MZ"},
    {"name": "Nagaland", "code": "NL"},
    {"name": "Odisha", "code": "OR"},
    {"name": "Punjab", "code": "PB"},
    {"name": "Rajasthan", "code": "RJ"},
    {"name": "Sikkim", "code": "SK"},
    {"name": "Tamil Nadu", "code": "TN"},
    {"name": "Telangana", "code": "TS"},
    {"name": "Tripura", "code": "TR"},
    {"name": "Uttar Pradesh", "code": "UP"},
    {"name": "Uttarakhand", "code": "UK"},
    {"name": "West Bengal", "code": "WB"},
    {"name": "Delhi", "code": "DL"},
    {"name": "Jammu and Kashmir", "code": "JK"},
    {"name": "Ladakh", "code": "LA"},
    {"name": "Puducherry", "code": "PY"},
    {"name": "Chandigarh", "code": "CH"},
    {"name": "Andaman and Nicobar Islands", "code": "AN"},
    {"name": "Dadra and Nagar Haveli and Daman and Diu", "code": "DD"},
    {"name": "Lakshadweep", "code": "LD"},
]


def seed_from_csv(csv_path: str, db):
    """
    Expected CSV columns: Pincode, OfficeName, Taluk, District, StateName, Telephone
    """
    print(f"Reading {csv_path}...")
    state_cache = {}
    district_cache = {}
    taluk_cache = {}
    count = 0

    with open(csv_path, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            state_name = row.get("StateName", "").strip()
            district_name = row.get("District", "").strip()
            taluk_name = row.get("Taluk", "").strip()
            pincode_val = row.get("Pincode", "").strip()
            office_name = row.get("OfficeName", "").strip()

            if not pincode_val or len(pincode_val) != 6:
                continue

            # State
            if state_name not in state_cache:
                state = db.query(State).filter_by(name=state_name).first()
                if not state:
                    state = State(name=state_name)
                    db.add(state)
                    db.flush()
                state_cache[state_name] = state.id
            state_id = state_cache[state_name]

            # District
            dist_key = f"{state_id}:{district_name}"
            if dist_key not in district_cache:
                district = db.query(District).filter_by(
                    state_id=state_id, name=district_name
                ).first()
                if not district:
                    district = District(state_id=state_id, name=district_name)
                    db.add(district)
                    db.flush()
                district_cache[dist_key] = district.id
            district_id = district_cache[dist_key]

            # Taluk
            taluk_key = f"{district_id}:{taluk_name}"
            taluk_id = None
            if taluk_name:
                if taluk_key not in taluk_cache:
                    taluk = db.query(Taluk).filter_by(
                        district_id=district_id, name=taluk_name
                    ).first()
                    if not taluk:
                        taluk = Taluk(district_id=district_id, name=taluk_name)
                        db.add(taluk)
                        db.flush()
                    taluk_cache[taluk_key] = taluk.id
                taluk_id = taluk_cache[taluk_key]

            # Pincode
            existing = db.query(Pincode).filter_by(pincode=pincode_val).first()
            if not existing:
                pc = Pincode(
                    pincode=pincode_val,
                    post_office=office_name,
                    taluk_id=taluk_id,
                    district_id=district_id,
                    state_id=state_id,
                )
                db.add(pc)
                count += 1

            if count % 500 == 0:
                db.commit()
                print(f"  Committed {count} pincodes...")

    db.commit()
    print(f"Done! Seeded {count} pincodes.")


def seed_states_only(db):
    """Seed just states when no CSV is available."""
    print("Seeding states...")
    for s in STATES_DATA:
        existing = db.query(State).filter_by(name=s["name"]).first()
        if not existing:
            db.add(State(name=s["name"], code=s["code"]))
    db.commit()
    print(f"Seeded {len(STATES_DATA)} states.")


def main():
    db = SessionLocal()
    try:
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "india_pincodes.csv"
        )

        if os.path.exists(csv_path):
            seed_from_csv(csv_path, db)
        else:
            print(f"CSV not found at {csv_path}")
            print("Seeding states only. Download pincode CSV and re-run for full data.")
            seed_states_only(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
