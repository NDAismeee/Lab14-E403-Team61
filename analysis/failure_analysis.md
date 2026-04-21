## Báo cáo Phân tích Thất bại (Failure Analysis Report) — Team61

## 1. Tổng quan Benchmark
Nguồn số liệu:
- `reports/benchmark_results.json` (kết quả per-case, đang là V2)
- `reports/comparison.json` (so sánh V1/V2 + delta + decision)

### 1.1 Thống kê chính
- **Tổng số cases**: **60**
- **Tỉ lệ Pass/Fail/Error**: **38 / 22 / 0**
- **Điểm RAGAS trung bình**:
  - **Faithfulness**: **0.00**
  - **Relevancy**: **0.00**
  - **Hit Rate**: **0.00**
  - **MRR**: **0.00**
- **Điểm LLM-Judge trung bình (V2)**: **3.19 / 5.0**
- **Agreement Rate trung bình (V2)**: **0.994**

### 1.2 Kết quả Regression (V2 so với V1)
- **V1 avg_score**: **1.49 / 5.0**
- **V2 avg_score**: **3.19 / 5.0**
- **Delta avg_score**: **+1.71**
- **Delta Hit Rate / MRR**: **+0.00 / +0.00**
- **Quyết định**: **approve**

## 2. Phân nhóm lỗi (Failure clustering) & nguyên nhân

### 2.1 Retrieval metrics bị “kẹt” ở 0 (Hit Rate = 0, MRR = 0)
**Triệu chứng**
- Hit Rate và MRR đều **0.0** cho cả V1 và V2.

**Nguyên nhân khả dĩ nhất**
- **Lệch nhãn** giữa `expected_retrieval_ids` (golden set) và `retrieved_ids` (agent trả về).
  - Golden set có thể default dạng `doc_id:chunk_01`
  - Retriever thực tế trả các chunk khác (vd `doc_id:chunk_61`, `chunk_66`...)
  - Context có thể đúng, nhưng **ID không match** → Hit Rate/MRR vẫn 0.

**Ảnh hưởng**
- Không phản ánh được cải thiện retrieval; benchmark hiện chủ yếu phản ánh cải thiện qua judge score (answer quality).

### 2.2 Lỗi kết nối khi agent gọi LLM (“Connection error”)
**Triệu chứng**
- Console có dòng: `Connection error` ở `MainAgentV1.query` / `MainAgent.query`.

**Root cause**
- Môi trường không truy cập được OpenAI endpoint (mạng/proxy/firewall/DNS).

**Giải pháp đã áp dụng**
- Agent tự động **fallback sang offline extraction** từ contexts để benchmark vẫn chạy xong và vẫn sinh report đúng schema.

### 2.3 Lỗi chất lượng câu trả lời
**V1 (cố tình tệ hơn)**
- Hay trả lời quá ngắn / đoán / bỏ contexts → thiếu thông tin, dễ fail.

**V2 (đã tối ưu)**
- Trước tối ưu: trả lời dài và lẫn thông tin không được hỏi.
- Sau tối ưu: chọn câu phù hợp câu hỏi từ contexts; với câu hỏi “áp dụng cho ai” ưu tiên câu tổng quát thay vì câu “Level … áp dụng cho …”.

## 3. 5 Whys cho blocker lớn nhất (Retrieval = 0)
**Vấn đề**: Retrieval metrics = 0 dù contexts có vẻ liên quan.
1) **Why 1**: Hit Rate = 0 vì expected IDs không xuất hiện trong retrieved IDs.
2) **Why 2**: expected IDs không match format/chunk index thực tế.
3) **Why 3**: golden set generator default `chunk_01` khi thiếu nhãn, trong khi retriever trả chunk khác.
4) **Why 4**: không có bước “align nhãn chunk” giữa golden set và chunk store (`data/chunks.jsonl`).
5) **Root cause**: nhãn retrieval ground-truth chưa đồng bộ với hệ thống chunking/index.

## 4. Kế hoạch cải tiến (Action plan)
### Ưu tiên cao (đúng evaluation)
- Đồng bộ `expected_retrieval_ids` với `retrieved_ids` thực tế (theo `data/chunks.jsonl` và logic `engine/retriever.py`).
- Thêm validator kiểm tra `expected_retrieval_ids` có tồn tại trong index trước khi chạy benchmark.

### Ưu tiên trung bình (tăng chất lượng agent)
- Khi có mạng/local endpoint ổn định, bật lại generation online để phản ánh đúng năng lực LLM.
- Thêm reranking đơn giản (lexical/BM25) trước khi chọn contexts.

### Nice-to-have
- Script thống kê lỗi theo cụm (incomplete/irrelevant/wrong number/entity/refusal) từ `reports/*benchmark_results.json`.

