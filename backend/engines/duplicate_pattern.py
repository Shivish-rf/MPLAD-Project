import os
import joblib
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "backend",
    "models"
)

VECTORIZER_PATH = os.path.join(
    MODEL_DIR,
    "duplicate_tfidf_vectorizer.pkl"
)

MATRIX_PATH = os.path.join(
    MODEL_DIR,
    "duplicate_tfidf_matrix.pkl"
)


# ============================================================
# LOAD EXISTING TF-IDF ARTIFACTS
# ============================================================

vectorizer = joblib.load(
    VECTORIZER_PATH
)

tfidf_matrix = joblib.load(
    MATRIX_PATH
)


# ============================================================
# SIMILARITY CLASSIFICATION
# ============================================================

def classify_similarity(score):

    if score >= 0.85:
        return "HIGH"

    elif score >= 0.65:
        return "MEDIUM"

    return "LOW"


# ============================================================
# FIND SIMILAR CANDIDATES
# ============================================================

def find_similar_candidates(
    work_description,
    candidates,
    threshold=0.65,
    top_k=5
):

    if not work_description:
        return []

    if not candidates:
        return []

    candidate_descriptions = []
    valid_candidates = []

    for candidate in candidates:

        description = getattr(
            candidate,
            "work_description",
            None
        )

        if description:

            candidate_descriptions.append(
                str(description)
            )

            valid_candidates.append(
                candidate
            )

    if not candidate_descriptions:
        return []

    # Convert current work to TF-IDF
    query_vector = vectorizer.transform(
        [str(work_description)]
    )

    # Convert candidates
    candidate_vectors = vectorizer.transform(
        candidate_descriptions
    )

    # Cosine similarity
    similarities = cosine_similarity(
        query_vector,
        candidate_vectors
    )[0]

    # Highest first
    ranked_indexes = similarities.argsort()[::-1]

    results = []

    for index in ranked_indexes:

        score = float(
            similarities[index]
        )

        if score < threshold:
            break

        candidate = valid_candidates[index]

        amount = getattr(
            candidate,
            "recommended_amount_rs",
            None
        )

        results.append({

            "work_id": candidate.work_id,

            "work_category":
                candidate.work_category,

            "constituency":
                candidate.constituency,

            "work_description":
                candidate.work_description,

            "recommended_amount":
                float(amount)
                if amount is not None
                else None,

            "similarity_score":
                round(score, 4),

            "similarity_level":
                classify_similarity(score)
        })

        if len(results) >= top_k:
            break

    return results


# ============================================================
# DUPLICATE ENGINE
# ============================================================

def run_duplicate_engine(
    work_description,
    candidates,
    threshold=0.65,
    top_k=5
):

    results = find_similar_candidates(
        work_description,
        candidates,
        threshold,
        top_k
    )

    high_count = sum(
        1
        for result in results
        if result["similarity_level"] == "HIGH"
    )

    medium_count = sum(
        1
        for result in results
        if result["similarity_level"] == "MEDIUM"
    )

    # --------------------------------------------------------
    # ENGINE SCORE
    # --------------------------------------------------------
    #
    # This is NOT the final system risk score.
    # It is only the Duplicate & Pattern engine score.
    #
    # 0   = no meaningful similarity
    # 100 = strong duplicate-pattern signal
    # --------------------------------------------------------

    if results:

        highest_similarity = max(
            result["similarity_score"]
            for result in results
        )

        candidate_factor = min(
            len(results) / top_k,
            1.0
        )

        duplicate_score = (
            highest_similarity * 70
            + candidate_factor * 30
        )

    else:

        duplicate_score = 0.0

    duplicate_score = round(
        min(duplicate_score, 100),
        2
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if high_count > 0:

        status = "HIGH_SIMILARITY_PATTERN"

    elif medium_count > 0:

        status = "MEDIUM_SIMILARITY_PATTERN"

    else:

        status = "NO_STRONG_SIMILARITY"

    return {

        "engine":
            "duplicate_pattern",

        "engine_score":
            duplicate_score,

        "status":
            status,

        "candidate_count":
            len(candidates),

        "similar_work_count":
            len(results),

        "high_similarity_count":
            high_count,

        "medium_similarity_count":
            medium_count,

        "results":
            results
    }