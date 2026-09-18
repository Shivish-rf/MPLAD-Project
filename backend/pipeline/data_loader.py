from sqlalchemy.orm import Session

from backend.database.crud import get_raw_work_data


def load_work(db: Session, work_id: str):
    """
    Load all raw database records belonging to one Work ID.

    This function does not calculate features or risk.
    """

    raw_data = get_raw_work_data(db, work_id)

    return raw_data