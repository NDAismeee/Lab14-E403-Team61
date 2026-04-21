# Báo Cáo cá nhân

**Họ tên:** Nguyễn Tiến Dũng
**Ngày:** 21/04/2026


| **Engineering Contribution** | 
----------------

- Triển khai logic RAG cho `MainAgentV2` với cơ chế **Strict Prompting** giúp giảm Hallucination (từ chối trả lời nếu thiếu thông tin).<br>- Xây dựng bộ `MainAgentV1` (Baseline) với các kịch bản **degrade** (giảm chất lượng) ngẫu nhiên để kiểm thử tính chính xác của Regression Gate.<br>- Thiết kế cấu trúc dữ liệu trả về chuẩn hóa (answer, contexts, retrieved_ids, metadata) để phục vụ quá trình chấm điểm tự động. |
| **Technical Depth** | - Phân tích nguyên nhân sâu xa (5 Whys) khiến chỉ số **Hit Rate và MRR bằng 0**: Do sự lệch nhãn giữa `expected_retrieval_ids` (mặc định chunk_01) và logic chunking thực tế của `retriever.py`.<br>- Hiểu rõ tác động của Prompt Engineering đến Answer Quality: Việc áp dụng ràng buộc "tối đa 2 câu" và "trọng tâm" ở V2 đã giúp cải thiện Score từ 1.49 (V1) lên 3.19 (V2). | 
| **Problem Solving** | - Phát triển cơ chế **Offline Fallback** (`_offline_answer_v2`): Sử dụng heuristic để trích xuất câu quan trọng từ ngữ cảnh khi gặp lỗi kết nối LLM, giúp pipeline benchmark không bị gián đoạn.<br>- Xử lý vấn đề log rác bằng cách giới hạn hiển thị thông báo lỗi tối đa 300 ký tự, giúp báo cáo trực quan và sạch sẽ hơn. | 
