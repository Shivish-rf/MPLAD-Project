from sqlalchemy import text
from sqlalchemy.orm import Session


def find_duplicate_candidates(
    db: Session,
    work_id: str,
    constituency: str,
    work_category: str,
    recommended_amount: float
):
    """
    Cheap duplicate candidate search.

    This does NOT perform ML similarity.
    It only finds records that are worth comparing.
    """

    query = text("""
        SELECT
            work_id,
            work_category,
            constituency,
            work_description,
            recommended_amount_rs
        FROM works_recommended
        WHERE work_id != :work_id
          AND constituency = :constituency
          AND work_category = :work_category
          AND recommended_amount_rs BETWEEN
              :min_amount AND :max_amount
        LIMIT 20
    """)

    # Allow ±10% amount difference
    min_amount = recommended_amount * 0.90
    max_amount = recommended_amount * 1.10

    result = db.execute(
        query,
        {
            "work_id": work_id,
            "constituency": constituency,
            "work_category": work_category,
            "min_amount": min_amount,
            "max_amount": max_amount
        }
    )

    return result.fetchall()