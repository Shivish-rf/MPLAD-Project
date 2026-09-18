import os
import joblib
import numpy as np


# --------------------------------------------------
# MODEL PATH
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "backend",
    "models",
    "cost_anomaly_engine.joblib"
)


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

artifacts = joblib.load(MODEL_PATH)

model = artifacts["model"]
scaler = artifacts["scaler"]
local_medians = artifacts["local_medians"]


# --------------------------------------------------
# ANOMALY ENGINE
# --------------------------------------------------

def run_anomaly_engine(features):
    constituency = features.get("constituency")
    work_category = features.get("work_category")
    recommended_amount = features.get("recommended_amount")

    # Cannot analyze without cost
    if recommended_amount is None:
        return {
            "engine": "anomaly",
            "engine_score": 0.0,
            "status": "INSUFFICIENT_DATA",
            "anomaly": False,
            "reason": "Recommended amount is missing",
            "recommended_amount": None,
            "local_median": None,
            "deviation_percent": None
        }

    # --------------------------------------------------
    # FIND LOCAL MEDIAN
    # --------------------------------------------------

    local_median = local_medians.get(
        (constituency, work_category)
    )

    # No local baseline available
    if local_median is None:
        local_median = recommended_amount

    # --------------------------------------------------
    # MODEL INPUT
    # Exact order used during training:
    # 1. sanction_amount_
    # 2. local_median
    # --------------------------------------------------

    X = np.array([
        [
            float(recommended_amount),
            float(local_median)
        ]
    ])

    X_scaled = scaler.transform(X)

    prediction = model.predict(X_scaled)[0]
    decision = model.decision_function(X_scaled)[0]

    # IsolationForest:
    # -1 = anomaly
    #  1 = normal

    is_anomaly = prediction == -1

    # --------------------------------------------------
    # COST DEVIATION
    # --------------------------------------------------

    if local_median > 0:
        deviation_percent = (
            abs(recommended_amount - local_median)
            / local_median
        ) * 100
    else:
        deviation_percent = 0

    # --------------------------------------------------
    # ENGINE SCORE
    # --------------------------------------------------

    # Convert deviation into an interpretable 0-100
    deviation_score = min(
        deviation_percent / 100 * 100,
        100
    )

    # IsolationForest signal
    if is_anomaly:
        model_score = 80
    else:
        model_score = 20

    # Combine model + local cost deviation
    engine_score = (
        model_score * 0.6
        + deviation_score * 0.4
    )

    engine_score = round(
        min(engine_score, 100),
        2
    )

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    if engine_score >= 70:
        status = "HIGH_COST_ANOMALY"
    elif engine_score >= 40:
        status = "MEDIUM_COST_ANOMALY"
    else:
        status = "NORMAL_COST_PATTERN"

    # --------------------------------------------------
    # REASON
    # --------------------------------------------------

    if deviation_percent >= 50:
        reason = (
            f"Recommended amount is {deviation_percent:.1f}% "
            f"away from the local median"
        )
    elif is_anomaly:
        reason = (
            "Isolation Forest detected an unusual cost pattern"
        )
    else:
        reason = (
            "Cost is within the expected local pattern"
        )

    return {
        "engine": "anomaly",
        "engine_score": engine_score,
        "status": status,
        "anomaly": bool(is_anomaly),
        "recommended_amount": round(
            float(recommended_amount), 2
        ),
        "local_median": round(
            float(local_median), 2
        ),
        "deviation_percent": round(
            float(deviation_percent), 2
        ),
        "model_decision": round(
            float(decision), 4
        ),
        "reason": reason
    }