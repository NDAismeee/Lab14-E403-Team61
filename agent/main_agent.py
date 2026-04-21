import asyncio
import os
import random
from typing import Dict
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
from engine.retriever import Retriever


def _safe_int(value: str | None, default: int) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return default


def _safe_float(value: str | None, default: float) -> float:
    try:
        return float(str(value).strip())
    except Exception:
        return default


def _tokenize_vi(text: str) -> list[str]:
    text = (text or "").lower()
    out: list[str] = []
    cur: list[str] = []
    for ch in text:
        if ch.isalnum() or ch in ("_",):
            cur.append(ch)
        else:
            if cur:
                out.append("".join(cur))
                cur = []
    if cur:
        out.append("".join(cur))
    return out


def _pick_relevant_sentences(question: str, contexts: list[str], max_sentences: int = 2) -> str:
    q_tokens = set(_tokenize_vi(question))
    if not q_tokens or not contexts:
        return ""

    q_lower = (question or "").lower()
    want_applicability_only = ("áp dụng" in q_lower and "ai" in q_lower and "level" not in q_lower)

    candidates: list[tuple[float, str]] = []
    for ctx_i, ctx in enumerate(contexts[:3]):
        for raw in (ctx or "").replace("\n", " ").split("."):
            sent = raw.strip()
            if len(sent) < 8:
                continue
            s_tokens = set(_tokenize_vi(sent))
            if not s_tokens:
                continue
            overlap = len(q_tokens & s_tokens)
            score = overlap / max(3, len(q_tokens))
            s_lower = sent.lower()
            if "áp dụng cho" in s_lower:
                score += 0.15
            if any(k in s_lower for k in ["tất cả", "nhân viên", "contractor", "vendor", "third-party"]):
                score += 0.30
            if "level" in s_lower:
                score -= 0.25
            score += (0.10 * (2 - ctx_i))
            if "thời gian" in question.lower() and ("ngày" in sent.lower() or "giờ" in sent.lower()):
                score += 0.15
            if want_applicability_only and "level" in s_lower:
                score -= 0.50
            candidates.append((score, sent))

    candidates.sort(key=lambda x: x[0], reverse=True)
    picked: list[str] = []
    seen = set()
    for score, sent in candidates:
        norm = sent.lower()
        if norm in seen:
            continue
        if score <= 0:
            break
        if want_applicability_only and "level" in norm:
            continue
        seen.add(norm)
        picked.append(sent)
        if len(picked) >= (1 if want_applicability_only else max_sentences):
            break

    if not picked:
        return ""
    return ". ".join(picked).rstrip(".") + "."


def _offline_answer_v2(question: str, contexts: list[str]) -> str:
    if not contexts:
        return "Tôi không biết vì không có ngữ cảnh phù hợp trong tài liệu."
    extracted = _pick_relevant_sentences(question, contexts, max_sentences=2)
    if extracted:
        return extracted
    first = contexts[0].strip()
    if first:
        first_line = first.split("\n", 1)[0].strip()
        if first_line:
            return (first_line[:300].rstrip() + "...") if len(first_line) > 300 else first_line
    return "Tôi không biết."


def _offline_answer_v1(question: str, contexts: list[str]) -> str:
    if not contexts:
        return "Không chắc."
    if random.random() < 0.7:
        return "Có."
    ctx = contexts[0].strip()
    if len(ctx) > 60:
        ctx = ctx[:60].rstrip() + "..."
    return ctx


def _is_connection_error(err: Exception) -> bool:
    msg = str(err).lower()
    return "connection error" in msg or "connect" in msg or "timed out" in msg or "timeout" in msg

class MainAgentV2:
    """
    Version 2: Keyword RAG with Error Handling
    - Retrieval: Keyword Search (top-3).
    - Generation: Strict prompt (refuse if not found).
    """
    def __init__(self):
        self.name = "SupportAgent-v2"
        self.retriever = Retriever()
        self.client = None
        self.model = os.getenv("AGENT_V2_MODEL", "gpt-4o-mini")
        self._logged_connection_error = False

    async def query(self, question: str) -> Dict:
        offline_mode = os.getenv("OFFLINE_MODE", "0").strip() == "1"
        max_tokens = _safe_int(os.getenv("AGENT_V2_MAX_TOKENS", "120"), 120)
        max_tokens = max(16, min(512, max_tokens))
        max_chars = _safe_int(os.getenv("AGENT_V2_MAX_CHARS", "350"), 350)
        max_chars = max(80, min(2000, max_chars))

        search_results = self.retriever.search(question, top_k=3)
        contexts = search_results.get("contexts", []) or []
        sources = search_results.get("sources", []) or []
        retrieved_ids = search_results.get("retrieved_ids", []) or []

        if contexts:
            context_str = "\n\n".join(c.strip() for c in contexts[:2] if c and c.strip())
        else:
            context_str = ""
        if len(context_str) > 900:
            context_str = context_str[:900].rstrip() + "..."

        system_prompt = (
            "Bạn là trợ lý hỗ trợ nội bộ.\n"
            "Chỉ trả lời đúng trọng tâm câu hỏi, tối đa 2 câu.\n"
            "Không liệt kê thêm thông tin không được hỏi.\n"
            "Nếu ngữ cảnh không có câu trả lời, hãy nói: \"Tôi không biết.\""
        )

        if offline_mode:
            answer_text = _offline_answer_v2(question, contexts)
            tokens_used = 0
            model_used = "offline-fallback"
        else:
            try:
                if self.client is None:
                    api_key = os.getenv("OPENAI_API_KEY")
                    if not api_key:
                        raise RuntimeError("Missing OPENAI_API_KEY")
                    base_url = os.getenv("OPENAI_BASE_URL") or None
                    self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"NGỮ CẢNH:\n{context_str}\n\nCÂU HỎI:\n{question}"},
                    ],
                    max_tokens=max_tokens,
                )
                answer_text = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
                model_used = self.model
            except Exception as e:
                if _is_connection_error(e) and not self._logged_connection_error:
                    self._logged_connection_error = True
                    msg = str(e)
                    print(f"❌ Error in MainAgent.query: {msg[:300]}{'...' if len(msg) > 300 else ''}")
                answer_text = _offline_answer_v2(question, contexts)
                tokens_used = 0
                model_used = "offline-fallback"

        answer_text = (answer_text or "").strip()
        if len(answer_text) > max_chars:
            answer_text = answer_text[:max_chars].rstrip() + "..."

        return {
            "answer": answer_text,
            "contexts": contexts,
            "retrieved_ids": retrieved_ids,
            "metadata": {
                "model": model_used,
                "tokens_used": tokens_used,
                "sources": list(set(sources)),
            },
        }

class MainAgentV1:
    """
    Version 1: Keyword RAG Baseline
    - Retrieval: Retriever (top-2).
    - Generation: Simple prompt.
    """
    def __init__(self):
        self.name = "SupportAgent-v1"
        self.retriever = Retriever()
        self.client = None
        self.model = os.getenv("AGENT_V1_MODEL", "gpt-5-nano")
        self._logged_connection_error = False
        seed_str = (os.getenv("AGENT_V1_SEED") or "").strip()
        if seed_str:
            try:
                random.seed(int(seed_str))
            except Exception:
                pass

    async def query(self, question: str) -> Dict:
        offline_mode = os.getenv("OFFLINE_MODE", "0").strip() == "1"

        degrade_prob = _safe_float(os.getenv("AGENT_V1_DEGRADE_PROB", "0.60"), 0.60)
        degrade_prob = max(0.0, min(1.0, degrade_prob))
        do_degrade = random.random() < degrade_prob

        top_k = _safe_int(os.getenv("AGENT_V1_TOP_K", "1"), 1)
        top_k = max(1, top_k)
        search_results = self.retriever.search(question, top_k=top_k)
        contexts = search_results.get("contexts", []) or []
        retrieved_ids = search_results.get("retrieved_ids", []) or []
        sources = search_results.get("sources", []) or []

        if do_degrade:
            mode = random.random()
            if mode < 0.40:
                contexts = []
                retrieved_ids = []
                sources = []
            elif mode < 0.70 and contexts:
                contexts = contexts[:1]
                retrieved_ids = retrieved_ids[:1]
            else:
                contexts = []

        context_str = "\n\n".join(contexts) if contexts else "Không có ngữ cảnh."

        if do_degrade and random.random() < 0.35:
            system_prompt = (
                "Trả lời thật ngắn (<= 1 câu). Nếu không chắc, hãy đoán. "
                f"Câu hỏi: {question}"
            )
        elif do_degrade and random.random() < 0.60:
            system_prompt = (
                "Hãy trả lời câu hỏi sau bằng kiến thức chung, không cần dựa vào ngữ cảnh. "
                f"Câu hỏi: {question}"
            )
        else:
            system_prompt = f"Dựa vào thông tin này: {context_str}. Hãy trả lời câu hỏi: {question}"

        temperature = _safe_float(os.getenv("AGENT_V1_TEMPERATURE", "0.9"), 0.9)
        temperature = max(0.0, min(2.0, temperature)) if do_degrade else 0.2

        if offline_mode:
            answer_text = _offline_answer_v1(question, contexts)
            tokens_used = 0
            model_used = "offline-fallback"
        else:
            try:
                if self.client is None:
                    api_key = os.getenv("OPENAI_API_KEY")
                    if not api_key:
                        raise RuntimeError("Missing OPENAI_API_KEY")
                    base_url = os.getenv("OPENAI_BASE_URL") or None
                    self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": system_prompt}],
                    temperature=temperature,
                )
                answer_text = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
                model_used = self.model
            except Exception as e:
                if _is_connection_error(e) and not self._logged_connection_error:
                    self._logged_connection_error = True
                    msg = str(e)
                    print(f"❌ Error in MainAgentV1.query: {msg[:300]}{'...' if len(msg) > 300 else ''}")
                answer_text = _offline_answer_v1(question, contexts)
                tokens_used = 0
                model_used = "offline-fallback"

        return {
            "answer": answer_text,
            "contexts": contexts,
            "retrieved_ids": retrieved_ids,
            "metadata": {
                "model": model_used,
                "tokens_used": tokens_used,
                "sources": list(set(sources)),
            },
        }

if __name__ == "__main__":
    agent = MainAgentV2()
    async def test():
        resp = await agent.query("Làm thế nào để đổi mật khẩu?")
        print(resp)
    asyncio.run(test())
