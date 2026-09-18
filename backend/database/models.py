from sqlalchemy import Column, Integer, String, Float, Date
from .connection import Base


class WorkRecommended(Base):

    __tablename__ = "works_recommended"

    id = Column(Integer, primary_key=True)
    work_id = Column(String, index=True)

    work_category = Column(String)
    work = Column(String)

    state = Column(String)
    ida = Column(String)

    hon_ble_members_of_parliament = Column(String)
    constituency = Column(String)

    work_description = Column(String)

    recommended_date = Column(Date)
    recommended_amount_rs = Column(Float)

    sanction_date = Column(Date)


class WorkSanctioned(Base):
    __tablename__ = "works_sanctioned"

    id = Column(Integer, primary_key=True)
    work_id = Column(String, index=True)
    work_category = Column(String)
    work = Column(String)
    state = Column(String)
    ida = Column(String)
    hon_ble_members_of_parliament = Column(String)
    constituency = Column(String)
    work_description = Column(String)
    recommended_date = Column(Date)
    sanction_date = Column(Date)


class WorkCompleted(Base):

    __tablename__ = "works_completed"

    id = Column(Integer, primary_key=True)
    work_id = Column(String, index=True)

    work_category = Column(String)
    work = Column(String)

    state = Column(String)
    ida = Column(String)

    work_description = Column(String)

    hon_ble_members_of_parliament = Column(String)
    constituency = Column(String)

    completion_date = Column(Date)
    amount_disbursed_rs = Column(Float)


class Expenditure(Base):

    __tablename__ = "expenditures"

    id = Column(Integer, primary_key=True)
    work_id = Column(String, index=True)

    state = Column(String)
    work = Column(String)
    ida = Column(String)

    hon_ble_members_of_parliament = Column(String)
    constituency = Column(String)

    vendor_name = Column(String)
    payment_status = Column(String)

    fund_disbursed_amount_rs = Column(Float)