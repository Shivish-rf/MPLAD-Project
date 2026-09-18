from sqlalchemy import text
from backend.database.connection import SessionLocal


db = SessionLocal()

try:
    print("\n" + "=" * 60)
    print("DATABASE TEST")
    print("=" * 60)

    # 1. Test database connection
    result = db.execute(text("SELECT 1"))
    print("\n[1] Database connection: OK")

    # 2. Check row counts
    tables = [
        "works_recommended",
        "works_sanctioned",
        "works_completed",
        "expenditures"
    ]

    print("\n[2] TABLE COUNTS")

    for table in tables:
        result = db.execute(
            text(f"SELECT COUNT(*) FROM {table}")
        )
        count = result.scalar()

        print(f"{table:<25} : {count} rows")

    # 3. Get one real Work ID
    result = db.execute(
        text("""
            SELECT work_id
            FROM works_recommended
            WHERE work_id IS NOT NULL
            LIMIT 1
        """)
    )

    row = result.fetchone()

    if not row:
        print("\n[3] No Work ID found.")
    else:
        work_id = row[0]

        print("\n[3] TEST WORK ID")
        print("Work ID:", work_id)

        # 4. Test each table using the same Work ID
        for table in tables:

            result = db.execute(
                text(f"""
                    SELECT COUNT(*)
                    FROM {table}
                    WHERE work_id = :work_id
                """),
                {"work_id": work_id}
            )

            count = result.scalar()

            print(f"{table:<25} : {count} record(s)")

        # 5. Show expenditure records
        result = db.execute(
            text("""
                SELECT
                    work_id,
                    vendor_name,
                    payment_status,
                    fund_disbursed_amount_rs
                FROM expenditures
                WHERE work_id = :work_id
            """),
            {"work_id": work_id}
        )

        expenditures = result.fetchall()

        print("\n[4] EXPENDITURE RECORDS")

        for i, exp in enumerate(expenditures, start=1):
            print(f"\nPayment {i}")
            print("Work ID:", exp[0])
            print("Vendor:", exp[1])
            print("Payment Status:", exp[2])
            print("Amount:", exp[3])

    print("\n" + "=" * 60)
    print("DATABASE TEST COMPLETED")
    print("=" * 60)

except Exception as e:
    print("\nDATABASE TEST FAILED")
    print(type(e).__name__)
    print(e)

finally:
    db.close()