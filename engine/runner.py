from __future__ import annotations

import asyncio
import time
from typing import Any, Awaitable, Callable


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _safe_list_str(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [s for s in (_safe_str(x) for x in value) if s]
    if isinstance(value, tuple):
        return [s for s in (_safe_str(x) for x in value) if s]
    s = _safe_str(value)
    return [s] if s else []


async def _maybe_await(value: Any) -> Any:
    if asyncio.iscoroutine(value) or isinstance(value, Awaitable):
        return await value
    return value


def _default_ragas() -> dict[str, Any]:
    return {"faithfulness": 0.0, "relevancy": 0.0, "retrieval": {"hit_rate": 0.0, "mrr": 0.0}}


def _normalize_ragas(obj: Any) -> dict[str, Any]:
    if not isinstance(obj, dict):
        return _default_ragas()
    retrieval = obj.get("retrieval", {})
    if not isinstance(retrieval, dict):
        retrieval = {}
    return {
        "faithfulness": float(obj.get("faithfulness", 0.0) or 0.0),
        "relevancy": float(obj.get("relevancy", 0.0) or 0.0),
        "retrieval": {
            "hit_rate": float(retrieval.get("hit_rate", 0.0) or 0.0),
            "mrr": float(retrieval.get("mrr", 0.0) or 0.0),
        },
    }


def _normalize_judge(obj: Any) -> dict[str, Any]:
    if not isinstance(obj, dict):
        obj = {}
    individual_scores = obj.get("individual_scores", {})
    if not isinstance(individual_scores, dict):
        individual_scores = {}
    return {
        "individual_scores": {str(k): float(v) for k, v in individual_scores.items() if isinstance(v, (int, float))},
        "final_score": float(obj.get("final_score", 0.0) or 0.0),
        "agreement_rate": float(obj.get("agreement_rate", 0.0) or 0.0),
        "reasoning": _safe_str(obj.get("reasoning", "")).strip() or "No judge reasoning provided.",
        "conflict": bool(obj.get("conflict", False)),
    }


def _error_result(case_id: str, error: str) -> dict[str, Any]:
    return {
        "case_id": case_id or "unknown",
        "status": "error",
        "error": _safe_str(error),
        "judge": {
            "final_score": 0.0,
            "agreement_rate": 0.0,
            "reasoning": "Benchmark failed for this case.",
            "individual_scores": {},
            "conflict": False,
        },
        "ragas": {"retrieval": {"hit_rate": 0.0, "mrr": 0.0}, "faithfulness": 0.0, "relevancy": 0.0},
        "latency_sec": 0.0,
        "agent_response": "",
        "retrieved_ids": [],
        "question": "",
        "expected_answer": "",
        "contexts": [],
        "token_usage": {"input": 0, "output": 0, "total": 0},
    }


class BenchmarkRunner:
    def __init__(self, agent: Any, evaluator: Any, judge: Any, max_concurrency: int = 5) -> None:
        self.agent = agent
        self.evaluator = evaluator
        self.judge = judge
        self._semaphore = asyncio.Semaphore(max(1, int(max_concurrency)))

    async def run_single_test(self, test_case: dict[str, Any]) -> dict[str, Any]:
        case_id = _safe_str((test_case or {}).get("id", "")) or "unknown"
        question = _safe_str((test_case or {}).get("question", ""))
        expected_answer = _safe_str((test_case or {}).get("expected_answer", ""))

        start = time.perf_counter()
        try:
            response = await _maybe_await(self.agent.query(question))
            latency_sec = time.perf_counter() - start

            if not isinstance(response, dict):
                response = {}
            agent_answer = _safe_str(response.get("answer", ""))
            contexts = _safe_list_str(response.get("contexts", []))
            retrieved_ids = _safe_list_str(response.get("retrieved_ids", []))
            agent_meta = response.get("metadata", {})
            if not isinstance(agent_meta, dict):
                agent_meta = {}

            ragas_raw: Any = _default_ragas()
            if self.evaluator is not None and hasattr(self.evaluator, "score"):
                try:
                    ragas_raw = await _maybe_await(self.evaluator.score(test_case, response))
                except TypeError:
                    ragas_raw = await _maybe_await(self.evaluator.score(test_case))
                except Exception:
                    ragas_raw = _default_ragas()
            ragas = _normalize_ragas(ragas_raw)

            judge_raw: Any = {}
            if self.judge is not None and hasattr(self.judge, "evaluate_multi_judge"):
                try:
                    judge_raw = await _maybe_await(
                        self.judge.evaluate_multi_judge(
                            question=question,
                            answer=agent_answer,
                            ground_truth=expected_answer,
                            contexts=contexts,
                            metadata=agent_meta,
                        )
                    )
                except TypeError:
                    judge_raw = await _maybe_await(self.judge.evaluate_multi_judge(question, agent_answer, expected_answer))
                except Exception as exc:
                    judge_raw = {"final_score": 0.0, "agreement_rate": 0.0, "reasoning": f"Judge failed: {exc}", "individual_scores": {}}
            judge = _normalize_judge(judge_raw)

            status = "pass" if judge["final_score"] >= 3.0 else "fail"
            agent_tokens = int(agent_meta.get("tokens_used", 0) or 0)

            return {
                "case_id": case_id,
                "question": question,
                "expected_answer": expected_answer,
                "agent_response": agent_answer,
                "contexts": contexts,
                "retrieved_ids": retrieved_ids,
                "ragas": ragas,
                "judge": judge,
                "latency_sec": float(latency_sec),
                "token_usage": {"input": 0, "output": 0, "total": int(agent_tokens)},
                "status": status,
            }
        except Exception as exc:
            return _error_result(case_id, str(exc))

    async def run_all(self, dataset: list[dict[str, Any]], batch_size: int = 5) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []

        async def _run_with_limit(case: dict[str, Any]) -> dict[str, Any]:
            async with self._semaphore:
                return await self.run_single_test(case)

        for i in range(0, len(dataset), batch_size):
            batch = dataset[i : i + batch_size]
            tasks = [_run_with_limit(case) for case in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            for item in batch_results:
                if isinstance(item, Exception):
                    results.append(_error_result("unknown", str(item)))
                else:
                    results.append(item)
        return results
