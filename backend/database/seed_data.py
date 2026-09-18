from datetime import date

from connection import Base, engine, SessionLocal
from models import Work


# --------------------------------------------------
# 1. Create database tables
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# 2. Simulated data coming from MPLADS website
# --------------------------------------------------

mplads_data = [

    {
        "work_id": "MPLADS/MP001/2025/0001",
        "work_description": "Construction of community road",
        "work_category": "Road",
        "state": "Madhya Pradesh",
        "constituency": "Bhopal",
        "mp_name": "MP Example 1",
        "vendor": "ABC Construction",
        "recommended_amount": 800000,
        "sanction_amount": 780000,
        "expenditure_amount": 720000,
        "recommended_date": date(2025, 4, 10),
        "sanction_date": date(2025, 5, 5),
        "completion_date": date(2025, 10, 10),
        "payment_status": "Paid",
        "work_status": "Completed",
        "fiscal_year": "2025-26",
        "approval_delay_days": 25
    },

    {
        "work_id": "MPLADS/MP001/2025/0002",
        "work_description": "Construction of village road",
        "work_category": "Road",
        "state": "Madhya Pradesh",
        "constituency": "Bhopal",
        "mp_name": "MP Example 1",
        "vendor": "XYZ Infrastructure",
        "recommended_amount": 1200000,
        "sanction_amount": 1150000,
        "expenditure_amount": 1400000,
        "recommended_date": date(2025, 4, 15),
        "sanction_date": date(2025, 11, 20),
        "completion_date": None,
        "payment_status": "Partially Paid",
        "work_status": "Ongoing",
        "fiscal_year": "2025-26",
        "approval_delay_days": 219
    },

    {
        "work_id": "MPLADS/MP002/2025/0003",
        "work_description": "Installation of drinking water facility",
        "work_category": "Water Supply",
        "state": "Madhya Pradesh",
        "constituency": "Indore",
        "mp_name": "MP Example 2",
        "vendor": "Water Solutions Pvt Ltd",
        "recommended_amount": 500000,
        "sanction_amount": 490000,
        "expenditure_amount": 450000,
        "recommended_date": date(2025, 6, 1),
        "sanction_date": date(2025, 6, 20),
        "completion_date": date(2025, 9, 1),
        "payment_status": "Paid",
        "work_status": "Completed",
        "fiscal_year": "2025-26",
        "approval_delay_days": 19
    }
]


# --------------------------------------------------
# 3. Insert into database
# --------------------------------------------------

db = SessionLocal()

try:

    for data in mplads_data:

        # Prevent duplicate Work IDs
        existing_work = (
            db.query(Work)
            .filter(Work.work_id == data["work_id"])
            .first()
        )

        if existing_work:
            print(
                f"Skipping duplicate: {data['work_id']}"
            )
            continue

        work = Work(**data)

        db.add(work)

    db.commit()

    print("MPLADS data inserted successfully.")

finally:

    db.close()