# Báo cáo cá nhân (Reflection)

**Họ và tên:** Nguyễn Đức Anh  
**Mã học viên:** 2A202600146
**Nhóm:** Team 61   
**Ngày:** 21/04/2026  
**Vai trò:** Execution Layer Engineer (Runner + Multi-Judge + Integration Outputs)

---

## 1. Engineering Contribution

Trong Lab 14, tôi phụ trách chính phần **lớp thực thi benchmark** (execution layer) để pipeline chạy được end-to-end và sinh ra các file output đúng chuẩn chấm điểm.

- **Triển khai Multi-Judge** (`engine/llm_judge.py`)
  - Xây dựng `LLMJudge.evaluate_multi_judge(...)` chạy **tối thiểu 2 judge** song song bằng `asyncio.gather`.
  - Tính **final_score**, **agreement_rate**, **conflict**, và sinh **reasoning** ổn định.
  - Hỗ trợ nhiều chế độ backend:
    - **heuristic** (fallback luôn chạy được, không phụ thuộc API)
    - **ollama** (local)
    - **openai_compatible** (LM Studio/llama.cpp/OpenAI endpoint)
  - Đảm bảo output trả về **JSON-serializable**, đúng schema để `main.py` có thể aggregate.

- **Triển khai Async Benchmark Runner** (`engine/runner.py`)
  - Implement `run_single_test(...)` và `run_all(...)` theo batch, dùng `asyncio.gather(..., return_exceptions=True)` để **không crash toàn run**.
  - Chuẩn hoá agent output một cách phòng thủ (thiếu field vẫn chạy) và trả về result schema thống nhất.
  - Ghi nhận `latency_sec`, `retrieved_ids`, `status`, `judge.final_score`, `judge.agreement_rate` theo yêu cầu integration.
  - Thêm giới hạn concurrency bằng semaphore để tránh quá tải khi chạy batch.

- **Chuẩn hoá report theo format tham chiếu** (`main.py`, `reports/`)
  - Chuyển `reports/summary.json` và `reports/benchmark_results.json` về **format giống thư mục `example/`** (phục vụ chấm điểm/đối chiếu).
  - Tạo thêm artifact phục vụ regression tracking: `reports/comparison.json`, `reports/v1_*.json`, `reports/v2_*.json`.

---

## 2. Technical Depth

- **Multi-judge agreement & conflict**
  - Áp dụng logic minh bạch: \(agreement\_rate = \max(0, 1 - |a-b|/5)\), conflict khi \(|a-b| > 1\).
  - Thiết kế output có `individual_scores` và mapping model để giữ traceability.

- **Thiết kế hệ thống “backend-agnostic”**
  - Judge có thể chạy heuristic (offline), hoặc chuyển sang local/endpoint OpenAI-compatible mà không đổi pipeline.
  - Điều này giúp benchmark **luôn chạy được** ngay cả khi môi trường thiếu kết nối mạng.

- **Schema stability & JSON safety**
  - Ưu tiên “output contract” ổn định để `check_lab.py` luôn pass.
  - Các dict trả ra đảm bảo JSON-serializable, tránh object không thể dump.

---

## 3. Problem Solving

- **Sửa các lỗi integration làm benchmark không chạy**
  - Fix mismatch import/luồng chạy trong `main.py` (agent V1/V2, latency field, output aggregation).
  - Bổ sung và chuẩn hoá output để không thiếu các trường mà pipeline aggregation cần.

- **Xử lý lỗi kết nối “Connection error” nhưng vẫn chạy được benchmark**
  - Khi môi trường không gọi được OpenAI, agent tự fallback sang offline extraction từ contexts.
  - Giảm log spam bằng cơ chế chỉ in lỗi kết nối “một lần”/agent.
  - Nhờ vậy benchmark vẫn sinh đủ report trong `reports/` để nhóm nộp bài.

- **Tối ưu câu trả lời V2 theo “hợp lý với câu hỏi dựa vào data”**
  - Điều chỉnh logic chọn câu trong contexts theo độ phù hợp với câu hỏi (ưu tiên câu tổng quát, tránh lẫn thông tin Level khi câu hỏi không yêu cầu).

---

## 4. Những gì làm tốt và những gì chưa xong

### Làm tốt
- Pipeline benchmark chạy được end-to-end và **không chết vì 1 case lỗi**.
- Multi-judge có fallback chạy được offline, giúp hệ thống ổn định.
- Output `reports/summary.json` và `reports/benchmark_results.json` đã **khớp format tham chiếu** trong `example/`.

### Chưa xong / cần cải thiện
- **Retrieval metrics (Hit Rate/MRR) vẫn = 0** phần lớn do lệch nhãn giữa `expected_retrieval_ids` và `retrieved_ids` thực tế (cần đồng bộ lại golden label với chunk index).
- Khi môi trường không có kết nối, agent chạy offline fallback nên chưa phản ánh đầy đủ năng lực generation của LLM online/local.

