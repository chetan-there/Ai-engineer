# app/evaluation/ragas_eval.py
# Ragas evaluation pipeline for RAG system quality measurement.
#
# WHY EVALUATE?
#   Building a RAG system is not enough — you must MEASURE it.
#   In production, teams track these metrics continuously (CI/CD pipelines).
#   Ragas is the industry-standard evaluation framework for RAG.
#
# METRICS EXPLAINED:
#
#   Faithfulness (0–1):
#     Are the claims in the answer supported by the retrieved context?
#     High faithfulness = low hallucination. Most critical metric.
#
#   Answer Relevancy (0–1):
#     Is the answer actually relevant to the question asked?
#     Penalizes off-topic or incomplete answers.
#
#   Context Precision (0–1):
#     Are the retrieved chunks actually useful for answering the question?
#     High precision = retrieval is targeted, not noisy.
#
# USAGE:
#   Run from terminal:
#       python -m app.evaluation.ragas_eval
#   Or hit the API endpoint:
#       POST /evaluate

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from datasets import Dataset
import logging

logger = logging.getLogger(__name__)


def run_ragas_evaluation(test_cases: list[dict]) -> dict:
    """
    Run Ragas evaluation on a set of QA test cases.

    Args:
        test_cases: List of dicts, each with:
            {
                "question": str,
                "answer": str,           ← LLM-generated answer
                "contexts": list[str],   ← retrieved chunk texts
                "ground_truth": str,     ← correct answer (for context_precision)
            }

    Returns:
        Dict with metric scores, e.g.:
            {
                "faithfulness": 0.91,
                "answer_relevancy": 0.87,
                "context_precision": 0.83,
            }
    """
    if not test_cases:
        raise ValueError("No test cases provided for evaluation.")

    # Ragas expects a HuggingFace Dataset with specific column names
    dataset = Dataset.from_list([
        {
            "question": tc["question"],
            "answer": tc["answer"],
            "contexts": tc["contexts"],
            "ground_truth": tc.get("ground_truth", ""),
        }
        for tc in test_cases
    ])

    logger.info(f"Running Ragas evaluation on {len(test_cases)} test cases...")

    results = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
        ],
    )

    scores = {
        "faithfulness": round(float(results["faithfulness"]), 4),
        "answer_relevancy": round(float(results["answer_relevancy"]), 4),
        "context_precision": round(float(results["context_precision"]), 4),
    }

    logger.info(f"Ragas scores: {scores}")
    return scores


# ── Sample test harness ───────────────────────────────────────────────────────
SAMPLE_TEST_CASES = [
    {
        "question": "What is the main topic of the uploaded document?",
        "answer": "The document covers machine learning fundamentals. [Source 1]",
        "contexts": [
            "Machine learning is a subset of artificial intelligence that enables systems to learn.",
            "This textbook introduces the core concepts of supervised and unsupervised learning.",
        ],
        "ground_truth": "The document is about machine learning fundamentals.",
    },
]


if __name__ == "__main__":
    import os
    # Ragas uses OpenAI internally for LLM-as-judge
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  Set OPENAI_API_KEY in your .env to run Ragas evaluation.")
    else:
        scores = run_ragas_evaluation(SAMPLE_TEST_CASES)
        print("\n📊 Ragas Evaluation Results:")
        for metric, score in scores.items():
            bar = "█" * int(score * 20)
            print(f"  {metric:<25} {bar:<20} {score:.4f}")
