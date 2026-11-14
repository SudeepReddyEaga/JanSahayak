"""
10-Profile Precision & Recall Benchmark Evaluator (CO3 / CO4 Evaluation Target).
Runs all 10 curated multilingual citizen profiles through the full Microsoft Agent
Framework SequentialPipeline, measures Precision, Recall, F1, Exact Match, Grounding
Pass Rate, Language Consistency Rate, Scheme Name Preservation Rate, and saves results.
"""

import json
from pathlib import Path
import uuid

from shared.domain.enums import LanguageCode
from shared.domain.models import (
    ApplicationGuideRequest,
    EvaluationProfileResult,
    EvaluationSummary,
)
from services.agent_orchestrator_service.clients.profile_client import IProfileMemoryClient
from services.agent_orchestrator_service.pipeline.sequential_pipeline import (
    SequentialSchemePipeline,
)

BENCHMARK_FILE = Path(__file__).parent / "benchmark_profiles.json"


def _compute_prf(expected: set[str], predicted: set[str]) -> tuple[float, float, float]:
    """
    Compute per-profile (precision, recall, f1) cleanly.
    When both expected and predicted are empty (negative control P10), returns (1.0, 1.0, 1.0).
    """
    if not expected and not predicted:
        return 1.0, 1.0, 1.0
    tp = len(expected & predicted)
    precision = tp / len(predicted) if predicted else 0.0
    recall = tp / len(expected) if expected else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return round(precision, 4), round(recall, 4), round(f1, 4)


class BenchmarkEvaluator:
    """Executes and aggregates the 10-profile precision/recall evaluation suite."""

    def __init__(
        self,
        pipeline: SequentialSchemePipeline,
        memory_client: IProfileMemoryClient | None = None,
    ) -> None:
        self._pipeline = pipeline
        self._memory_client = memory_client

    @staticmethod
    def load_profiles(path: Path = BENCHMARK_FILE) -> list[dict]:
        """Load the 10 benchmark citizen profiles from JSON."""
        return json.loads(path.read_text(encoding="utf-8"))

    async def run_evaluation(self, *, persist: bool = True) -> EvaluationSummary:
        """Execute all 10 profiles through the live sequential pipeline and compute metrics."""
        profiles = self.load_profiles()
        run_id = f"eval-{uuid.uuid4().hex[:10]}"

        per_profile: list[EvaluationProfileResult] = []
        total_tp = 0
        total_fp = 0
        total_fn = 0

        for item in profiles:
            expected_list: list[str] = item["expected_scheme_ids"]
            expected_set = set(expected_list)
            lang = LanguageCode(item["language"])

            # Run full pipeline with bypass_cache=True to test true live multi-agent execution
            req = ApplicationGuideRequest(
                query=item["query"],
                session_id=f"{run_id}-{item['profile_id']}",
                preferred_language=lang,
                bypass_cache=True,
            )
            resp = await self._pipeline.run(req)

            predicted_list = [s.scheme_id for s in resp.eligible_schemes]
            predicted_set = set(predicted_list)

            tp_list = sorted(expected_set & predicted_set)
            fp_list = sorted(predicted_set - expected_set)
            fn_list = sorted(expected_set - predicted_set)

            total_tp += len(tp_list)
            total_fp += len(fp_list)
            total_fn += len(fn_list)

            p, r, f1 = _compute_prf(expected_set, predicted_set)
            per_profile.append(
                EvaluationProfileResult(
                    profile_id=item["profile_id"],
                    label=item["label"],
                    language=lang,
                    query=item["query"],
                    expected_scheme_ids=expected_list,
                    predicted_scheme_ids=predicted_list,
                    true_positives=tp_list,
                    false_positives=fp_list,
                    false_negatives=fn_list,
                    precision=p,
                    recall=r,
                    f1_score=f1,
                    exact_match=(expected_set == predicted_set),
                    grounding_passed=resp.grounding_report.passed,
                    language_consistent=resp.language_review_report.language_consistent,
                    scheme_names_intact=resp.language_review_report.scheme_names_intact,
                    latency_ms=resp.total_latency_ms,
                )
            )

        n = max(1, len(per_profile))
        macro_p = round(sum(x.precision for x in per_profile) / n, 4)
        macro_r = round(sum(x.recall for x in per_profile) / n, 4)
        macro_f1 = round(sum(x.f1_score for x in per_profile) / n, 4)

        micro_p = round(total_tp / (total_tp + total_fp), 4) if (total_tp + total_fp) > 0 else 1.0
        micro_r = round(total_tp / (total_tp + total_fn), 4) if (total_tp + total_fn) > 0 else 1.0
        micro_f1 = (
            round(2 * micro_p * micro_r / (micro_p + micro_r), 4)
            if (micro_p + micro_r) > 0
            else 0.0
        )

        summary = EvaluationSummary(
            run_id=run_id,
            total_profiles=len(per_profile),
            macro_precision=macro_p,
            macro_recall=macro_r,
            macro_f1=macro_f1,
            micro_precision=micro_p,
            micro_recall=micro_r,
            micro_f1=micro_f1,
            exact_match_rate=round(sum(1 for x in per_profile if x.exact_match) / n, 4),
            grounding_pass_rate=round(sum(1 for x in per_profile if x.grounding_passed) / n, 4),
            language_consistency_rate=round(sum(1 for x in per_profile if x.language_consistent) / n, 4),
            scheme_name_preservation_rate=round(sum(1 for x in per_profile if x.scheme_names_intact) / n, 4),
            avg_latency_ms=round(sum(x.latency_ms for x in per_profile) / n, 2),
            profile_results=per_profile,
        )

        if persist and self._memory_client is not None:
            await self._memory_client.save_evaluation(summary)

        return summary

