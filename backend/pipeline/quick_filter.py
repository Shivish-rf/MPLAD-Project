def quick_filter(features, duplicate_candidates=None):

    signals = []

    # =====================================================
    # 1. COMPLETED BUT NO EXPENDITURE
    # =====================================================

    if (
        features.get("is_completed") is True
        and features.get("expenditure_record_count", 0) == 0
    ):
        signals.append({
            "type": "missing_expenditure",
            "message": "Completed work has no expenditure record"
        })

    # =====================================================
    # 2. LONG APPROVAL DELAY
    # =====================================================

    approval_delay = features.get("approval_delay_days")

    if approval_delay is not None and approval_delay > 30:

        signals.append({
            "type": "approval_delay",
            "message": (
                f"Approval delay is high: "
                f"{approval_delay} days"
            )
        })

    # =====================================================
    # 3. EXPENDITURE EXCEEDS RECOMMENDED AMOUNT
    # =====================================================

    recommended_amount = features.get(
        "recommended_amount"
    )

    total_expenditure = features.get(
        "total_expenditure",
        0
    )

    if (
        recommended_amount is not None
        and total_expenditure > recommended_amount
    ):

        signals.append({
            "type": "amount_exceeded",
            "message": (
                "Total expenditure exceeds "
                "recommended amount"
            )
        })

    # =====================================================
    # 4. DUPLICATE CANDIDATES
    # =====================================================

    duplicate_count = 0

    if duplicate_candidates:
        duplicate_count = len(duplicate_candidates)

    if duplicate_count > 0:

        signals.append({
            "type": "duplicate_candidate",
            "message": (
                f"{duplicate_count} potentially similar "
                "work(s) found"
            )
        })

    # =====================================================
    # FINAL DECISION
    # =====================================================

    should_analyze = len(signals) > 0

    return {
        "should_analyze": should_analyze,
        "signal_count": len(signals),
        "signals": signals,
        "duplicate_candidate_count": duplicate_count
    }