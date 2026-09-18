def calculate_days(start_date, end_date):
    if not start_date or not end_date:
        return None

    return (end_date - start_date).days


def extract_features(raw_data):

    recommended = raw_data.get("recommended")
    sanctioned = raw_data.get("sanctioned")
    completed = raw_data.get("completed")
    expenditures = raw_data.get("expenditures", [])

    features = {}

    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    if recommended:
        features["work_id"] = recommended.work_id
        features["work_category"] = recommended.work_category
        features["state"] = recommended.state
        features["constituency"] = recommended.constituency
        features["work"] = recommended.work
        features["work_description"] = recommended.work_description
        features["recommended_amount"] = (
            recommended.recommended_amount_rs
        )

    # =====================================================
    # SANCTION
    # =====================================================

    features["is_sanctioned"] = sanctioned is not None

    # =====================================================
    # COMPLETION
    # =====================================================

    features["is_completed"] = completed is not None

    # =====================================================
    # APPROVAL DELAY
    # =====================================================

    if recommended and sanctioned:

        features["approval_delay_days"] = calculate_days(
            recommended.recommended_date,
            sanctioned.sanction_date
        )

    else:
        features["approval_delay_days"] = None

    # =====================================================
    # EXPENDITURE
    # =====================================================

    features["expenditure_record_count"] = len(expenditures)

    total_expenditure = 0

    for expenditure in expenditures:

        amount = expenditure.fund_disbursed_amount_rs

        if amount is not None:
            total_expenditure += amount

    features["total_expenditure"] = total_expenditure

    # =====================================================
    # COMPLETION AMOUNT
    # =====================================================

    if completed:
        features["amount_disbursed"] = (
            completed.amount_disbursed_rs
        )
    else:
        features["amount_disbursed"] = None

    # =====================================================
    # DUPLICATE SCREENING FEATURES
    # =====================================================

    # Number of raw expenditure records is useful later
    # because one work can have multiple payments.
    features["payment_record_count"] = len(expenditures)

    # These are candidate fields that the duplicate engine
    # will use later.
    features["duplicate_candidate"] = False
    features["similar_work_count"] = 0
    features["duplicate_work_id_count"] = 1

    return features