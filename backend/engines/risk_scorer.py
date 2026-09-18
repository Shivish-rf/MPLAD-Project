
def calculate_final_risk(
    compliance_result,
    duplicate_result,
    anomaly_result,
    delay_result
):
    """
    Combine all engine scores into one final risk score.

    Weights:
        Compliance       = 30%
        Duplicate        = 25%
        Anomaly          = 25%
        Delay & Progress = 20%

    Final score range: 0-100
    """

    compliance_score = compliance_result.get(
        "engine_score",
        0
    )

    duplicate_score = duplicate_result.get(
        "engine_score",
        0
    )

    anomaly_score = anomaly_result.get(
        "engine_score",
        0
    )

    delay_score = delay_result.get(
        "engine_score",
        0
    )

    # -----------------------------------------
    # WEIGHTS
    # -----------------------------------------

    compliance_weight = 0.30
    duplicate_weight = 0.25
    anomaly_weight = 0.25
    delay_weight = 0.20

    # -----------------------------------------
    # FINAL SCORE
    # -----------------------------------------

    final_score = (
        compliance_score * compliance_weight
        + duplicate_score * duplicate_weight
        + anomaly_score * anomaly_weight
        + delay_score * delay_weight
    )

    final_score = round(
        min(max(final_score, 0), 100),
        2
    )

    # -----------------------------------------
    # RISK LEVEL
    # -----------------------------------------

    if final_score >= 70:
        risk_level = "HIGH"

    elif final_score >= 40:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    return {
        "final_risk_score": final_score,
        "risk_level": risk_level,

        "engine_scores": {
            "compliance": compliance_score,
            "duplicate_pattern": duplicate_score,
            "anomaly": anomaly_score,
            "delay_progress": delay_score
        },

        "weights": {
            "compliance": compliance_weight,
            "duplicate_pattern": duplicate_weight,
            "anomaly": anomaly_weight,
            "delay_progress": delay_weight
        }
    }

