from __future__ import annotations

import asyncio
import json
import math
import re
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any, Literal, Mapping


Backend = Literal["heuristic", "ollama", "openai_compatible"]


@dataclass(frozen=True)
class JudgeResult:
    score: float
    reasoning: str
    model: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


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
    return [_safe_str(value)] if _safe_str(value) else []


def _tokenize(text: str) -> set[str]:
    text = text.lower()
    return set(re.findall(r"[a-z0-9]+", text))


def _heuristic_score(
    question: str,
    answer: str,
    ground_truth: str,
    contexts: list[str] | None,
) -> tuple[float, str]:
    a = _safe_str(answer).strip()
    gt = _safe_str(ground_truth).strip()
    if not a:
        return 1.0, "Empty answer."

    a_tokens = _tokenize(a)
    gt_tokens = _tokenize(gt) if gt else set()
    ctx_tokens: set[str] = set()
    if contexts:
        for c in contexts:
            ctx_tokens |= _tokenize(_safe_str(c))

    overlap_gt = (len(a_tokens & gt_tokens) / max(1, len(gt_tokens))) if gt_tokens else 0.0
    overlap_ctx = (len(a_tokens & ctx_tokens) / max(1, len(a_tokens))) if a_tokens and ctx_tokens else 0.0

    length_penalty = 0.0
    if len(a) < 20:
        length_penalty = 0.15

    hallucination_penalty = 0.0
    if ctx_tokens:
        unsupported = a_tokens - ctx_tokens
        unsupported_ratio = len(unsupported) / max(1, len(a_tokens))
        hallucination_penalty = _clamp(unsupported_ratio * 0.35, 0.0, 0.35)

    base = 1.0
    if gt_tokens:
        base = 1.0 + 4.0 * overlap_gt
        score = base - 2.0 * hallucination_penalty - 1.5 * length_penalty
        score = _clamp(score, 1.0, 5.0)
        reasoning = (
            f"Overlap with expected answer: {overlap_gt:.2f}. "
            f"Context support: {overlap_ctx:.2f}. "
            f"Penalties applied: {hallucination_penalty + length_penalty:.2f}."
        )
        return score, reasoning

    score = 3.0 - 1.5 * length_penalty - 2.0 * hallucination_penalty
    score = _clamp(score, 1.0, 5.0)
    reasoning = (
        f"No ground truth provided. Context support: {overlap_ctx:.2f}. "
        f"Penalties applied: {hallucination_penalty + length_penalty:.2f}."
    )
    return score, reasoning


def _build_judge_prompt(question: str, answer: str, ground_truth: str, contexts: list[str] | None) -> str:
    ctx = "\n\n".join(f"- {c}" for c in (contexts or []))[:6000]
    return (
        "You are a strict evaluator. Score the ANSWER vs EXPECTED_ANSWER from 1 to 5.\n"
        "Rubric (overall score): correctness, faithfulness-to-context, completeness, refusal quality.\n"
        "Return ONLY valid JSON: {\"score\": <float 1..5>, \"reasoning\": <short string>}.\n\n"
        f"QUESTION:\n{question}\n\n"
        f"EXPECTED_ANSWER:\n{ground_truth}\n\n"
        f"CONTEXTS:\n{ctx}\n\n"
        f"ANSWER:\n{answer}\n"
    )


def _extract_json_object(text: str) -> dict[str, Any] | None:
    text = text.strip()
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        obj = json.loads(match.group(0))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


class LLMJudge:
    def __init__(
        self,
        backend: Backend = "heuristic",
        model_a: str = "qwen2.5-7b-instruct",
        model_b: str = "qwen2.5-7b-instruct",
        ollama_url: str = "http://localhost:11434/api/generate",
        openai_base_url: str = "http://localhost:1234/v1/chat/completions",
        openai_api_key: str | None = None,
        request_timeout_sec: float = 60.0,
    ) -> None:
        self.backend = backend
        self.model_a = model_a
        self.model_b = model_b
        self.ollama_url = ollama_url
        self.openai_base_url = openai_base_url
        self.openai_api_key = openai_api_key
        self.request_timeout_sec = request_timeout_sec

    async def _judge_once(
        self,
        judge_key: str,
        model_name: str,
        question: str,
        answer: str,
        ground_truth: str,
        contexts: list[str] | None = None,
    ) -> JudgeResult:
        question_s = _safe_str(question)
        answer_s = _safe_str(answer)
        ground_truth_s = _safe_str(ground_truth)
        contexts_s = _safe_list_str(contexts)

        if self.backend == "heuristic":
            score, reasoning = _heuristic_score(question_s, answer_s, ground_truth_s, contexts_s)
            return JudgeResult(score=float(score), reasoning=reasoning, model="heuristic")

        prompt = _build_judge_prompt(question_s, answer_s, ground_truth_s, contexts_s)
        try:
            if self.backend == "ollama":
                text = await asyncio.to_thread(self._call_ollama, model_name, prompt)
            else:
                text = await asyncio.to_thread(self._call_openai_compatible, model_name, prompt)
            parsed = _extract_json_object(text) or {}
            raw_score = parsed.get("score", None)
            score = float(raw_score) if raw_score is not None and not isinstance(raw_score, bool) else math.nan
            if math.isnan(score):
                raise ValueError(f"Invalid score from judge {judge_key}")
            score = _clamp(score, 1.0, 5.0)
            reasoning = _safe_str(parsed.get("reasoning", "")).strip() or "No reasoning provided."
            return JudgeResult(score=score, reasoning=reasoning, model=model_name)
        except Exception:
            score, reasoning = _heuristic_score(question_s, answer_s, ground_truth_s, contexts_s)
            return JudgeResult(score=float(score), reasoning=f"LLM backend failed; fallback. {reasoning}", model="heuristic")

    def _call_ollama(self, model: str, prompt: str) -> str:
        payload = {"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.ollama_url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=self.request_timeout_sec) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        obj = json.loads(body) if body else {}
        return _safe_str(obj.get("response", body))

    def _call_openai_compatible(self, model: str, prompt: str) -> str:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an evaluator that returns JSON only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.0,
        }
        headers = {"Content-Type": "application/json"}
        if self.openai_api_key:
            headers["Authorization"] = f"Bearer {self.openai_api_key}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.openai_base_url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=self.request_timeout_sec) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        obj = json.loads(body) if body else {}
        content = (
            obj.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        return _safe_str(content) or body

    @staticmethod
    def _compute_agreement(score_a: float, score_b: float) -> tuple[float, bool]:
        delta = abs(float(score_a) - float(score_b))
        agreement_rate = max(0.0, 1.0 - delta / 5.0)
        conflict = delta > 1.0
        return float(agreement_rate), bool(conflict)

    async def evaluate_multi_judge(
        self,
        question: str,
        answer: str,
        ground_truth: str,
        contexts: list[str] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Evaluate with at least two judges and return a JSON-serializable dict with:
        individual_scores, final_score, agreement_rate, reasoning, conflict, models.
        """
        _ = metadata
        judge_a_task = self._judge_once("judge_a", self.model_a, question, answer, ground_truth, contexts)
        judge_b_task = self._judge_once("judge_b", self.model_b, question, answer, ground_truth, contexts)
        res_a, res_b = await asyncio.gather(judge_a_task, judge_b_task)

        final_score = (res_a.score + res_b.score) / 2.0
        agreement_rate, conflict = self._compute_agreement(res_a.score, res_b.score)
        merged_reasoning = f"Judge A: {res_a.reasoning} Judge B: {res_b.reasoning}".strip()

        return {
            "individual_scores": {"judge_a": float(res_a.score), "judge_b": float(res_b.score)},
            "final_score": float(final_score),
            "agreement_rate": float(agreement_rate),
            "reasoning": merged_reasoning,
            "conflict": bool(conflict),
            "models": {"judge_a": _safe_str(res_a.model), "judge_b": _safe_str(res_b.model)},
        }

    async def check_position_bias(self, response_a: str, response_b: str) -> dict[str, Any]:
        _ = response_a
        _ = response_b
        return {"tested": False, "bias_detected": False, "notes": "Position bias test not enabled in local mode."}
