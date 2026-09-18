from sqlalchemy.orm import Session

from .models import (
    WorkRecommended,
    WorkSanctioned,
    WorkCompleted,
    Expenditure
)


def get_recommended_work(db: Session, work_id: str):

    return (
        db.query(WorkRecommended)
        .filter(WorkRecommended.work_id == work_id)
        .first()
    )


def get_sanctioned_work(db: Session, work_id: str):

    return (
        db.query(WorkSanctioned)
        .filter(WorkSanctioned.work_id == work_id)
        .first()
    )


def get_completed_work(db: Session, work_id: str):

    return (
        db.query(WorkCompleted)
        .filter(WorkCompleted.work_id == work_id)
        .first()
    )


def get_expenditures(db: Session, work_id: str):

    return (
        db.query(Expenditure)
        .filter(Expenditure.work_id == work_id)
        .all()
    )


def get_raw_work_data(db: Session, work_id: str):

    return {
        "recommended": get_recommended_work(db, work_id),
        "sanctioned": get_sanctioned_work(db, work_id),
        "completed": get_completed_work(db, work_id),
        "expenditures": get_expenditures(db, work_id)
    }