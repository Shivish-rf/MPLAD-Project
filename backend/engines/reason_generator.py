
def generate_risk_reasons(
    compliance_result,
    duplicate_result,
    anomaly_result,
    delay_result,
    final_risk_result
):
    """
    Generate human-readable explanations for the final risk result.

    This does NOT calculate the risk score.
    It only explains the signals produced by the four engines.
    """

    reasons = []

    # ---------------------------------------------------------
    # 1. COMPLIANCE REASONS
    # ---------------------------------------------------------
    matched_rules = compliance_result.get("matched_rules", [])

    for rule in matched_rules:
        reasons.append({
            "engine": "compliance",
            "severity": rule.get("severity", "MEDIUM"),
            "type": "compliance_rule",
            "message": rule.get("reason", "Compliance rule triggered.")
        })

    # ---------------------------------------------------------
    # 2. DUPLICATE / PATTERN REASONS
    # ---------------------------------------------------------
    high_similarity = duplicate_result.get(
        "high_similarity_count",
        0
    )

    medium_similarity = duplicate_result.get(
        "medium_similarity_count",
        0
    )

    similar_work_count = duplicate_result.get(
        "similar_work_count",
        0
    )

    if high_similarity > 0:
        reasons.append({
            "engine": "duplicate_pattern",
            "severity": "HIGH",
            "type": "high_similarity",
            "message": (
                f"{high_similarity} work(s) have high textual "
                f"similarity with this work."
            )
        })

    elif medium_similarity > 0:
        reasons.append({
            "engine": "duplicate_pattern",
            "severity": "MEDIUM",
            "type": "medium_similarity",
            "message": (
                f"{medium_similarity} work(s) have medium textual "
                f"similarity with this work."
            )
        })

    elif similar_work_count > 0:
        reasons.append({
            "engine": "duplicate_pattern",
            "severity": "LOW",
            "type": "similar_works",
            "message": (
                f"{similar_work_count} potentially similar "
                f"work(s) were found, but none crossed the "
                f"strong similarity threshold."
            )
        })

    # ---------------------------------------------------------
    # 3. ANOMALY REASONS
    # ---------------------------------------------------------
    if anomaly_result.get("anomaly") is True:

        deviation = anomaly_result.get(
            "deviation_percent"
        )

        recommended_amount = anomaly_result.get(
            "recommended_amount"
        )

        local_median = anomaly_result.get(
            "local_median"
        )

        message = (
            "The cost pattern was identified as unusual "
            "by the anomaly detection model."
        )

        if (
            deviation is not None
            and recommended_amount is not None
            and local_median is not None
        ):
            message = (
                f"The recommended amount is "
                f"{recommended_amount:,.2f}, while the local "
                f"median is {local_median:,.2f}, with a "
                f"{deviation}% deviation."
            )

        reasons.append({
            "engine": "anomaly",
            "severity": "MEDIUM",
            "type": "cost_anomaly",
            "message": message
        })

    # ---------------------------------------------------------
    # 4. DELAY / PROGRESS REASONS
    # ---------------------------------------------------------
    delay_reasons = delay_result.get(
        "reasons",
        []
    )

    for reason in delay_reasons:
        reasons.append({
            "engine": "delay_progress",
            "severity": "MEDIUM",
            "type": reason.get("type", "delay"),
            "message": reason.get(
                "message",
                "Delay or progress issue detected."
            )
        })

    # ---------------------------------------------------------
    # 5. FINAL RISK SUMMARY
    # ---------------------------------------------------------
    final_score = final_risk_result.get(
        "final_risk_score",
        0
    )

    risk_level = final_risk_result.get(
        "risk_level",
        "LOW"
    )

    if risk_level == "HIGH":
        summary = (
            f"High prototype risk score ({final_score}/100). "
            "Multiple risk signals require review."
        )

    elif risk_level == "MEDIUM":
        summary = (
            f"Medium prototype risk score ({final_score}/100). "
            "Some risk signals require further review."
        )

    else:
        summary = (
            f"Low prototype risk score ({final_score}/100). "
            "The current configured engines detected limited "
            "combined risk signals."
        )

    # ---------------------------------------------------------
    # 6. ENGINE SCORE SUMMARY
    # ---------------------------------------------------------
    engine_scores = final_risk_result.get(
        "engine_scores",
        {}
    )

    return {
        "summary": summary,
        "risk_level": risk_level,
        "final_risk_score": final_score,
        "reasons": reasons,
        "engine_scores": engine_scores,
        "reason_count": len(reasons)
    }

