# Báo cáo cá nhân - [Họ tên]

## 1. Engineering Contribution

- Phụ trách toàn bộ pipeline Ingestion + Chunking + Retriever Core.
- Viết module `engine/retriever.py`:
    - Đọc tự động tất cả file .txt trong `data/docs/`.
    - Tách văn bản thành các chunk nhỏ, gán metadata (doc_id, chunk_id, source_file, text).
    - Sinh file `data/chunks.jsonl` làm Knowledge Base cho hệ thống.
    - Xây dựng hàm `search(query, top_k)` trả về các chunk liên quan nhất dựa trên keyword overlap.
- Đảm bảo module hoạt động ổn định, dễ mở rộng cho các phương pháp search nâng cao (TF-IDF/BM25).
- Đóng góp commit code rõ ràng, có giải thích kỹ thuật trong pull request.

## 2. Technical Depth

- **MRR (Mean Reciprocal Rank):** Hiểu và có thể tính toán chỉ số này để đánh giá chất lượng truy xuất tài liệu.
- **Cohen's Kappa:** Nắm được ý nghĩa và cách dùng để đo độ đồng thuận giữa các Judge.
- **Position Bias:** Biết cách kiểm tra và giảm thiểu thiên vị vị trí trong đánh giá.
- Hiểu rõ trade-off giữa chi phí (tính toán, lưu trữ) và chất lượng (độ chính xác, tốc độ truy xuất) khi thiết kế retriever.

## 3. Problem Solving

- Xử lý lỗi đường dẫn khi chạy script từ các thư mục khác nhau bằng cách hướng dẫn hoặc chỉnh code cho robust.
- Debug lỗi FileNotFound, kiểm tra lại cấu trúc thư mục và hướng dẫn nhóm chạy đúng quy trình.
- Đề xuất cải tiến chunking (ví dụ: chunk theo ngữ nghĩa thay vì cố định số từ) để tăng chất lượng retrieval.
- Hỗ trợ nhóm tích hợp retriever vào pipeline tổng, đảm bảo agent có thể truy xuất dữ liệu hiệu quả.

---
*Báo cáo này thể hiện rõ vai trò và đóng góp kỹ thuật của tôi trong dự án Lab 14.*
