import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

RULES_PATH = os.path.join(
    BASE_DIR,
    "backend",
    "engines",
    "compliance_rules.json"
)


def load_rules():

    with open(
        RULES_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)["rules"]


def check_rule(rule, features):

    condition = rule["condition"]

    # --------------------------------------------------
    # Completed but no expenditure
    # --------------------------------------------------

    if condition == "completed_and_zero_expenditure":

        return (
            features.get("is_completed") is True
            and features.get("expenditure_record_count", 0) == 0
        )

    # --------------------------------------------------
    # Expenditure > recommended amount
    # --------------------------------------------------

    if condition == "expenditure_greater_than_recommended":

        recommended = features.get(
            "recommended_amount"
        )

        expenditure = features.get(
            "total_expenditure",
            0
        )

        return (
            recommended is not None
            and expenditure > recommended
        )

    # --------------------------------------------------
    # Approval delay
    # --------------------------------------------------

    if condition == "greater_than_30":

        value = features.get(
            rule["field"]
        )

        return (
            value is not None
            and value > rule["threshold"]
        )

    # --------------------------------------------------
    # Boolean false
    # --------------------------------------------------

    if condition == "equals_false":

        return features.get(
            rule["field"]
        ) is False

    return False


def run_compliance_engine(features):

    rules = load_rules()

    matched_rules = []

    total_points = 0

    for rule in rules:

        matched = check_rule(
            rule,
            features
        )

        if matched:

            total_points += rule["points"]

            matched_rules.append({
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "severity": rule["severity"],
                "points": rule["points"],
                "reason": rule["reason"]
            })

    # Maximum possible score
    max_points = sum(
        rule["points"]
        for rule in rules
    )

    if max_points > 0:

        engine_score = (
            total_points / max_points
        ) * 100

    else:

        engine_score = 0

    engine_score = round(
        min(engine_score, 100),
        2
    )

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    if engine_score >= 70:

        status = "HIGH_COMPLIANCE_RISK"

    elif engine_score >= 40:

        status = "MEDIUM_COMPLIANCE_RISK"

    else:

        status = "LOW_COMPLIANCE_RISK"

    return {
        "engine": "compliance",
        "engine_score": engine_score,
        "status": status,
        "matched_rule_count": len(matched_rules),
        "matched_rules": matched_rules
    }