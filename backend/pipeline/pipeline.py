
from backend.database.connection import SessionLocal

from backend.engines.risk_scorer import calculate_final_risk
from backend.engines.reason_generator import generate_risk_reasons

from backend.engines.compilance import run_compliance_engine
from backend.engines.anomaly import run_anomaly_engine
from backend.engines.duplicate_pattern import run_duplicate_engine
from backend.engines.delay_progress import run_delay_progress_engine

from backend.pipeline.data_loader import load_work
from backend.pipeline.feature_extractor import extract_features
from backend.pipeline.duplicate_detector import find_duplicate_candidates
from backend.pipeline.quick_filter import quick_filter


TEST_WORK_ID = "WS/MP620/2024-2025/133166"


def run_pipeline(work_id):

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # 1. LOAD RAW DATABASE DATA
        # ----------------------------------------------------

        raw_data = load_work(
            db,
            work_id
        )

        # ----------------------------------------------------
        # 2. EXTRACT FEATURES
        # ----------------------------------------------------

        features = extract_features(
            raw_data
        )

        # ----------------------------------------------------
        # 3. FIND CHEAP DUPLICATE CANDIDATES
        # ----------------------------------------------------

        duplicate_candidates = []

        if (
            features.get("constituency")
            and features.get("work_category")
            and features.get("recommended_amount") is not None
        ):

            duplicate_candidates = find_duplicate_candidates(
                db=db,
                work_id=work_id,
                constituency=features["constituency"],
                work_category=features["work_category"],
                recommended_amount=features["recommended_amount"]
            )

        # ----------------------------------------------------
        # 4. QUICK FILTER
        # ----------------------------------------------------

        filter_result = quick_filter(
            features,
            duplicate_candidates
        )

        # ----------------------------------------------------
        # 5. DUPLICATE & PATTERN ENGINE
        # ----------------------------------------------------

        duplicate_result = {
            "engine": "duplicate_pattern",
            "status": "NOT_RUN",
            "engine_score": 0.0,
            "candidate_count": len(duplicate_candidates),
            "similar_work_count": 0,
            "high_similarity_count": 0,
            "medium_similarity_count": 0,
            "results": []
        }

        if filter_result["should_analyze"]:

            duplicate_result = run_duplicate_engine(
                work_description=features.get(
                    "work_description"
                ),
                candidates=duplicate_candidates,
                threshold=0.65,
                top_k=5
            )

        # ----------------------------------------------------
        # 6. ANOMALY ENGINE
        # ----------------------------------------------------

        anomaly_result = {
            "engine": "anomaly",
            "engine_score": 0.0,
            "status": "NOT_RUN",
            "anomaly": False
        }

        if filter_result["should_analyze"]:

            anomaly_result = run_anomaly_engine(
                features
            )

        # ----------------------------------------------------
        # 7. COMPLIANCE ENGINE
        # ----------------------------------------------------

        compliance_result = {
            "engine": "compliance",
            "engine_score": 0.0,
            "status": "NOT_RUN",
            "matched_rule_count": 0,
            "matched_rules": []
        }

        if filter_result["should_analyze"]:

            compliance_result = run_compliance_engine(
                features
            )

        # ----------------------------------------------------
        # 8. DELAY & PROGRESS ENGINE
        # ----------------------------------------------------

        delay_result = {
            "engine": "delay_progress",
            "engine_score": 0.0,
            "status": "NOT_RUN",
            "approval_delay_days": None,
            "is_completed": False,
            "reason_count": 0,
            "reasons": []
        }

        if filter_result["should_analyze"]:

            delay_result = run_delay_progress_engine(
                features
            )

        # ----------------------------------------------------
        # 9. FINAL RISK SCORER
        # ----------------------------------------------------

        risk_result = calculate_final_risk(
            compliance_result=compliance_result,
            duplicate_result=duplicate_result,
            anomaly_result=anomaly_result,
            delay_result=delay_result
        )

        # ----------------------------------------------------
        # 10. REASON GENERATOR
        # ----------------------------------------------------

        reason_result = generate_risk_reasons(
            compliance_result=compliance_result,
            duplicate_result=duplicate_result,
            anomaly_result=anomaly_result,
            delay_result=delay_result,
            final_risk_result=risk_result
        )

        # ----------------------------------------------------
        # 11. RETURN COMPLETE PIPELINE RESULT
        # ----------------------------------------------------

        return {

            "work_id": work_id,

            "features": features,

            "quick_filter": filter_result,

            "duplicate_engine": duplicate_result,

            "anomaly_engine": anomaly_result,

            "compliance_engine": compliance_result,

            "delay_progress_engine": delay_result,

            "final_risk": risk_result,

            "risk_reasons": reason_result
        }

    finally:

        db.close()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = run_pipeline(
        TEST_WORK_ID
    )

    print()

    print("=" * 60)
    print("MPLADS PIPELINE RESULT")
    print("=" * 60)

    # --------------------------------------------------------
    # WORK ID
    # --------------------------------------------------------

    print("\nWORK ID:")

    print(
        result["work_id"]
    )

    # --------------------------------------------------------
    # QUICK FILTER
    # --------------------------------------------------------

    print("\nQUICK FILTER")

    quick = result["quick_filter"]

    print(
        "Should analyze:",
        quick["should_analyze"]
    )

    print(
        "Signal count:",
        quick["signal_count"]
    )

    for signal in quick["signals"]:

        print(
            "-",
            signal["type"],
            ":",
            signal["message"]
        )

    # --------------------------------------------------------
    # DUPLICATE ENGINE
    # --------------------------------------------------------

    print("\nDUPLICATE & PATTERN ENGINE")

    duplicate = result["duplicate_engine"]

    print(
        "Status:",
        duplicate["status"]
    )

    print(
        "Engine score:",
        duplicate.get("engine_score", 0)
    )

    print(
        "Candidate count:",
        duplicate["candidate_count"]
    )

    print(
        "Similar work count:",
        duplicate["similar_work_count"]
    )

    print(
        "High similarity:",
        duplicate["high_similarity_count"]
    )

    print(
        "Medium similarity:",
        duplicate["medium_similarity_count"]
    )

    print("\nTOP SIMILAR WORKS")

    if duplicate["results"]:

        for item in duplicate["results"]:

            print(
                f"- {item['work_id']} | "
                f"Similarity: {item['similarity_score']} | "
                f"Level: {item['similarity_level']}"
            )

    else:

        print("- No strong similar works found.")

    # --------------------------------------------------------
    # ANOMALY ENGINE
    # --------------------------------------------------------

    print("\nANOMALY ENGINE")

    anomaly = result["anomaly_engine"]

    print(
        "Status:",
        anomaly["status"]
    )

    print(
        "Engine score:",
        anomaly.get("engine_score", 0)
    )

    print(
        "Anomaly:",
        anomaly.get("anomaly", False)
    )

    if anomaly.get("recommended_amount") is not None:

        print(
            "Recommended amount:",
            anomaly["recommended_amount"]
        )

        print(
            "Local median:",
            anomaly["local_median"]
        )

        print(
            "Deviation:",
            f"{anomaly['deviation_percent']}%"
        )

    print(
        "Reason:",
        anomaly.get("reason", "")
    )

    # --------------------------------------------------------
    # COMPLIANCE ENGINE
    # --------------------------------------------------------

    print("\nCOMPLIANCE ENGINE")

    compliance = result["compliance_engine"]

    print(
        "Status:",
        compliance["status"]
    )

    print(
        "Engine score:",
        compliance["engine_score"]
    )

    print(
        "Matched rules:",
        compliance["matched_rule_count"]
    )

    for rule in compliance["matched_rules"]:

        print(
            f"- {rule['rule_id']} | "
            f"{rule['severity']} | "
            f"+{rule['points']} points | "
            f"{rule['reason']}"
        )

    # --------------------------------------------------------
    # DELAY & PROGRESS ENGINE
    # --------------------------------------------------------

    print("\nDELAY & PROGRESS ENGINE")

    delay = result["delay_progress_engine"]

    print(
        "Status:",
        delay["status"]
    )

    print(
        "Engine score:",
        delay["engine_score"]
    )

    print(
        "Approval delay:",
        delay["approval_delay_days"],
        "days"
    )

    print(
        "Completed:",
        delay["is_completed"]
    )

    print(
        "Reasons:",
        delay["reason_count"]
    )

    for reason in delay["reasons"]:

        print(
            "-",
            reason["type"],
            ":",
            reason["message"]
        )

    # --------------------------------------------------------
    # FINAL RISK ASSESSMENT
    # --------------------------------------------------------

    print("\nFINAL RISK ASSESSMENT")

    risk = result["final_risk"]

    print(
        "Final Risk Score:",
        risk["final_risk_score"]
    )

    print(
        "Risk Level:",
        risk["risk_level"]
    )

    # --------------------------------------------------------
    # RISK REASONS
    # --------------------------------------------------------

    print("\nRISK REASONS")

    reason_data = result["risk_reasons"]

    print(
        "Summary:"
    )

    print(
        reason_data["summary"]
    )

    print(
        "\nDetected reasons:"
    )

    if reason_data["reasons"]:

        for reason in reason_data["reasons"]:

            print(
                f"- [{reason['severity']}] "
                f"{reason['engine']}: "
                f"{reason['message']}"
            )

    else:

        print(
            "- No specific risk reasons detected."
        )

    # --------------------------------------------------------
    # ENGINE SCORES USED
    # --------------------------------------------------------

    print("\nENGINE SCORES")

    for engine, score in risk["engine_scores"].items():

        print(
            f"- {engine}: {score}"
        )

    # --------------------------------------------------------
    # WEIGHTS
    # --------------------------------------------------------

    print("\nRISK WEIGHTS")

    for engine, weight in risk["weights"].items():

        print(
            f"- {engine}: {weight * 100:.0f}%"
        )

    print()

    print("=" * 60)
