# Failure Analysis Report (Team61)

## 1. Scope & pipeline overview
This lab submission implements a local, integration-friendly benchmark execution layer with:
- **Dataset**: `data/golden_set.jsonl` (JSONL test cases)
- **Agents**: `agent/main_agent.py`
  - **V1**: intentionally degraded (randomized “worse” behavior)
  - **V2**: improved answer extraction from retrieved contexts
- **Runner**: `engine/runner.py` (async batch runner, robust error handling)
- **Retrieval evaluator**: `engine/retrieval_eval.py` (Hit Rate, MRR)
- **Judge**: `engine/llm_judge.py` (multi-judge with agreement/conflict)
- **Orchestration + reports**: `main.py` → writes outputs to `reports/`

Benchmark flow per case:
1) Load test case (`id`, `question`, `expected_answer`, `expected_retrieval_ids`)
2) `agent.query(question)` → `answer`, `contexts`, `retrieved_ids`, `metadata`
3) Evaluator computes retrieval metrics (Hit Rate, MRR)
4) Multi-judge scores answer vs expected answer
5) Runner merges into a standardized JSON result per case

## 2. Reproducible results (latest run)
Source: `reports/comparison.json` (timestamp `2026-04-21 16:29:36`).

### Dataset size
- **Total cases**: **60**

### V1 (baseline, degraded)
- **Avg judge score**: **1.49 / 5**
- **Agreement rate**: **0.995**
- **Hit rate / MRR**: **0.00 / 0.00**

### V2 (optimized)
- **Avg judge score**: **3.19 / 5**
- **Agreement rate**: **0.994**
- **Hit rate / MRR**: **0.00 / 0.00**

### Regression deltas (V2 − V1)
- **Avg score**: **+1.71**
- **Hit rate**: **+0.00**
- **MRR**: **+0.00**
- **Avg latency**: slightly better for V2

Decision recorded in `reports/comparison.json`: **approve** (V2 improved score without lowering retrieval metrics).

## 3. What failed (clusters) and why
This section focuses on “why quality is not perfect yet” and “why retrieval metrics are stuck at 0”.

### 3.1 Retrieval metrics stuck at zero (Hit Rate = 0, MRR = 0)
**Symptom**
- Across runs, retrieval metrics remain **0.0** for both V1 and V2.

**Most likely cause**
- **Mismatch between** `expected_retrieval_ids` in the golden set and the agent’s `retrieved_ids` format/content.
  - Example pattern: golden set often uses default IDs like `doc_id:chunk_01`, while the retriever returns IDs like `doc_id:chunk_61`, `chunk_66`, etc.
  - Even when the contexts are relevant, the **IDs don’t match**, so Hit Rate/MRR compute to 0.

**Impact**
- Retrieval evaluation cannot currently validate whether retrieval improved, so improvements are reflected mainly in judge score (answer quality) rather than retrieval metrics.

### 3.2 Connectivity failures during agent generation (“Connection error”)
**Symptom**
- Terminal prints: `Error in MainAgent(V1/V2).query: Connection error.`

**Root cause**
- The environment cannot reach OpenAI endpoints (network/proxy/firewall/DNS).

**Mitigation implemented**
- Agents automatically **fall back to offline answering** using retrieved contexts, so the benchmark completes and still produces results.

**Impact**
- When fallback is active, agent quality depends on extraction heuristics rather than true LLM generation.

### 3.3 Answer quality failures (V1 vs V2 behavior)
**V1 failures (expected)**
- Randomly drops contexts or answers too short (“Có.” / “Không chắc.”), causing:
  - **Incomplete** answers
  - **Ungrounded** guesses

**V2 failures (before fixes)**
- Earlier versions were too verbose or included irrelevant sections (e.g., extra “Level 4” details).
- Then an over-aggressive shortening step removed key details.

**Fix implemented**
- V2 now selects **question-relevant sentences** from retrieved contexts using overlap scoring and applicability heuristics (e.g., “áp dụng cho ai” prefers general applicability over Level-specific rules).

## 4. 5-Whys on the biggest quality blocker (Retrieval = 0)
**Problem**: Retrieval metrics are 0.0 even when the retrieved context is relevant.
1) **Why is Hit Rate 0?** Expected IDs are not found in retrieved IDs.
2) **Why are IDs not found?** The dataset’s `expected_retrieval_ids` don’t match actual chunk IDs produced/used by the retriever.
3) **Why don’t they match?** The golden set generator defaults to `doc_id:chunk_01` when missing, while the retriever returns other chunk indices.
4) **Why does the generator default like that?** It does not have ground-truth chunk alignment to the chunk store used at retrieval time.
5) **Root cause**: Golden set retrieval labels are not aligned with the retriever’s chunking/indexing scheme.

## 5. Action plan (next improvements)
### High priority (fix evaluation correctness)
- Align `expected_retrieval_ids` with the actual `retrieved_ids` emitted by `engine/retriever.py` and `data/chunks.jsonl`.
- Add a small validator that checks `expected_retrieval_ids` exist in the chunk index before running benchmark.

### Medium priority (improve agent quality realistically)
- Restore online generation once connectivity is available (or run via local OpenAI-compatible server).
- Add a reranking step (BM25 + heuristic scoring) before selecting contexts.

### Low priority (nice-to-have)
- Add a failure dashboard script that counts clusters: incomplete, irrelevant, refusal, wrong entity/number.

