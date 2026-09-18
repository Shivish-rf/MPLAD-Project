def run_delay_progress_engine(features):
    """
    Delay & Progress Engine

    Calculates a 0-100 delay/progress risk score
    using simple rule-based checks.
    """

    approval_delay = features.get("approval_delay_days")
    is_completed = features.get("is_completed")

    score = 0
    reasons = []

    # -----------------------------------------
    # Approval Delay
    # -----------------------------------------

    if approval_delay is not None:

        if approval_delay > 90:
            score += 60

            reasons.append({
                "type": "very_high_approval_delay",
                "message": (
                    f"Approval delay is very high: "
                    f"{approval_delay} days"
                )
            })

        elif approval_delay > 60:
            score += 40

            reasons.append({
                "type": "high_approval_delay",
                "message": (
                    f"Approval delay is high: "
                    f"{approval_delay} days"
                )
            })

        elif approval_delay > 30:
            score += 20

            reasons.append({
                "type": "approval_delay",
                "message": (
                    f"Approval delay is {approval_delay} days"
                )
            })

    # -----------------------------------------
    # Completion Status
    # -----------------------------------------

    if is_completed is False:
        score += 30

        reasons.append({
            "type": "not_completed",
            "message": (
                "Work does not have a completion record"
            )
        })

    # -----------------------------------------
    # Limit Score
    # -----------------------------------------

    score = min(score, 100)

    # -----------------------------------------
    # Risk Status
    # -----------------------------------------

    if score >= 70:
        status = "HIGH_DELAY_RISK"

    elif score >= 40:
        status = "MEDIUM_DELAY_RISK"

    else:
        status = "LOW_DELAY_RISK"

    # -----------------------------------------
    # Result
    # -----------------------------------------

    return {
        "engine": "delay_progress",
        "engine_score": round(score, 2),
        "status": status,
        "approval_delay_days": approval_delay,
        "is_completed": is_completed,
        "reason_count": len(reasons),
        "reasons": reasons
    }