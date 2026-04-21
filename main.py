import asyncio
import json
import os
import time
from engine.runner import BenchmarkRunner
from agent.main_agent import MainAgentV1, MainAgentV2
from engine.retrieval_eval import RetrievalEvaluator
from engine.llm_judge import LLMJudge

async def run_benchmark_with_results(agent_version: str):
    print(f"🚀 Khởi động Benchmark cho {agent_version}...")

    if not os.path.exists("data/golden_set.jsonl"):
        print("❌ Thiếu data/golden_set.jsonl. Hãy chạy 'python data/synthetic_gen.py' trước.")
        return None, None

    with open("data/golden_set.jsonl", "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    if not dataset:
        print("❌ File data/golden_set.jsonl rỗng. Hãy tạo ít nhất 1 test case.")
        return None, None

    agent = MainAgentV1() if agent_version == "Agent_V1_Base" else MainAgentV2()
    judge = LLMJudge(
        backend=os.getenv("JUDGE_BACKEND", "heuristic"),
        model_a=os.getenv("JUDGE_MODEL_A", "qwen2.5-7b-instruct"),
        model_b=os.getenv("JUDGE_MODEL_B", "qwen2.5-7b-instruct"),
        ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate"),
        openai_base_url=os.getenv("OPENAI_COMPATIBLE_URL", "http://localhost:1234/v1/chat/completions"),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
    )
    runner = BenchmarkRunner(agent, RetrievalEvaluator(), judge)
    results = await runner.run_all(dataset)

    total = len(results)
    summary = {
        "metadata": {"version": agent_version, "total": total, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")},
        "metrics": {
            "avg_score": sum(r["judge"]["final_score"] for r in results) / total,
            "hit_rate": sum(r["ragas"]["retrieval"]["hit_rate"] for r in results) / total,
            "mrr": sum(r["ragas"]["retrieval"]["mrr"] for r in results) / total,
            "agreement_rate": sum(r["judge"]["agreement_rate"] for r in results) / total,
            "avg_latency": sum(r.get("latency_sec", 0.0) for r in results) / total,
            "avg_cost": sum(r.get("cost", 0.0) for r in results) / total
        }
    }
    return results, summary

async def run_benchmark(version):
    _, summary = await run_benchmark_with_results(version)
    return summary

async def main():
    v1_results, v1_summary = await run_benchmark_with_results("Agent_V1_Base")
    
    # Giả lập V2 có cải tiến (để test logic)
    v2_results, v2_summary = await run_benchmark_with_results("Agent_V2_Optimized")
    
    if not v1_results or not v1_summary or not v2_results or not v2_summary:
        print("❌ Không thể chạy Benchmark. Kiểm tra lại data/golden_set.jsonl.")
        return

    print("\n📊 --- KẾT QUẢ SO SÁNH (REGRESSION) ---")
    delta_score = v2_summary["metrics"]["avg_score"] - v1_summary["metrics"]["avg_score"]
    delta_hr = v2_summary["metrics"]["hit_rate"] - v1_summary["metrics"]["hit_rate"]
    delta_mrr = v2_summary["metrics"]["mrr"] - v1_summary["metrics"]["mrr"]
    delta_lat = v2_summary["metrics"]["avg_latency"] - v1_summary["metrics"]["avg_latency"]

    print(f"🔹 V1 Score: {v1_summary['metrics']['avg_score']:.2f}")
    print(f"🔹 V2 Score: {v2_summary['metrics']['avg_score']:.2f}")
    print(f"🔹 Hit Rate V1: {v1_summary['metrics']['hit_rate']:.2f} | MRR V1: {v1_summary['metrics']['mrr']:.2f}")
    print(f"🔹 Hit Rate V2: {v2_summary['metrics']['hit_rate']:.2f} | MRR V2: {v2_summary['metrics']['mrr']:.2f}")
    print(f"🔹 Avg Latency V1: {v1_summary['metrics']['avg_latency']:.2f}s | Avg Latency V2: {v2_summary['metrics']['avg_latency']:.2f}s")
    
    print("\n📈 Phân tích Delta:")
    print(f"Delta Score: {'+' if delta_score >= 0 else ''}{delta_score:.2f}")
    print(f"Delta Hit Rate: {'+' if delta_hr >= 0 else ''}{delta_hr:.2f} (Từ MRR: {'+' if delta_mrr >= 0 else ''}{delta_mrr:.2f})")
    print(f"Delta Latency: {'+' if delta_lat >= 0 else ''}{delta_lat:.2f}s (Số âm là tốt hơn)")

    os.makedirs("reports", exist_ok=True)
    with open("reports/v1_summary.json", "w", encoding="utf-8") as f:
        json.dump(v1_summary, f, ensure_ascii=False, indent=2)
    with open("reports/v2_summary.json", "w", encoding="utf-8") as f:
        json.dump(v2_summary, f, ensure_ascii=False, indent=2)
    with open("reports/v1_benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(v1_results, f, ensure_ascii=False, indent=2)
    with open("reports/v2_benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(v2_results, f, ensure_ascii=False, indent=2)
    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump(v2_summary, f, ensure_ascii=False, indent=2)
    with open("reports/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(v2_results, f, ensure_ascii=False, indent=2)

    # Approve release nếu không làm giảm Score trung bình, tỉ lệ Hit Rate và MRR
    decision = "approve"
    if delta_score >= 0 and delta_hr >= 0 and delta_mrr >= 0:
        print("\n✅ QUYẾT ĐỊNH: CHẤP NHẬN BẢN CẬP NHẬT (APPROVE)")
    else:
        decision = "block"
        print("\n❌ QUYẾT ĐỊNH: TỪ CHỐI (BLOCK RELEASE) vì suy giảm chất lượng truy xuất hoặc nội dung")

    comparison = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "v1_version": v1_summary.get("metadata", {}).get("version", "Agent_V1_Base"),
            "v2_version": v2_summary.get("metadata", {}).get("version", "Agent_V2_Optimized"),
        },
        "v1_summary": v1_summary,
        "v2_summary": v2_summary,
        "deltas": {
            "avg_score": float(delta_score),
            "hit_rate": float(delta_hr),
            "mrr": float(delta_mrr),
            "avg_latency": float(delta_lat),
        },
        "decision": decision,
    }
    with open("reports/comparison.json", "w", encoding="utf-8") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
