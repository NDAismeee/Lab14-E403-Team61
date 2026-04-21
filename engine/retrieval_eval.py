from typing import List, Dict

class RetrievalEvaluator:
    def __init__(self):
        pass

    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
        """
        Tính toán xem ít nhất 1 trong expected_ids có nằm trong top_k của retrieved_ids không.
        """
        if not expected_ids or not retrieved_ids:
            return 0.0
        top_retrieved = retrieved_ids[:top_k]
        hit = any(doc_id in expected_ids for doc_id in top_retrieved)
        return 1.0 if hit else 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        """
        Tính Mean Reciprocal Rank.
        Tìm vị trí đầu tiên của một expected_id trong retrieved_ids.
        MRR = 1 / position (vị trí 1-indexed). Nếu không thấy thì là 0.
        """
        if not expected_ids or not retrieved_ids:
            return 0.0
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return 1.0 / (i + 1)
        return 0.0

    async def score(self, case: Dict, resp: Dict) -> Dict:
        """
        Trả về kết quả evaluation cho 1 test case.
        """
        expected_ids = case.get("expected_retrieval_ids", [])
        retrieved_ids = resp.get("retrieved_ids", [])
        return {
            "faithfulness": 0.0, # Field placeholder nếu RAGAS metric khác được tích hợp sau
            "relevancy": 0.0,
            "retrieval": {
                "hit_rate": self.calculate_hit_rate(expected_ids, retrieved_ids),
                "mrr": self.calculate_mrr(expected_ids, retrieved_ids)
            }
        }

    async def evaluate_batch(self, dataset: List[Dict]) -> Dict:
        """
        Chạy eval cho toàn bộ bộ dữ liệu.
        Dataset cần có trường 'expected_retrieval_ids' và Agent trả về 'retrieved_ids'.
        """
        # Placeholder logic
        return {"avg_hit_rate": 0.0, "avg_mrr": 0.0}
