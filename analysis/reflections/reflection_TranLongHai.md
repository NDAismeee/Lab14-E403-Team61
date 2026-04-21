# Báo cáo Cá nhân (Personal Report)

- **Họ và tên:** Trần Long Hải
- **MSSV:** 2A202600427
- **Vai trò:** Retrieval Evaluator & Regression Analyst

---

## 1. Đóng góp kỹ thuật (Engineering Contribution)

Trong dự án Lab 14, tôi chịu trách nhiệm chính về việc xây dựng hệ thống đo lường chất lượng truy xuất (Retrieval) và logic so sánh phiên bản (Regression Testing). Cụ thể:

### A. Module Retrieval Evaluation (`engine/retrieval_eval.py`)
Tôi đã hiện thực hóa module đánh giá truy xuất từ đầu, chuyển đổi từ các logic giả lập sang tính toán thực tế dựa trên dữ liệu:
- **Hit Rate@k:** Tính toán tỷ lệ một câu hỏi có ít nhất một tài liệu chính xác nằm trong `top_k` kết quả trả về. Đây là chỉ số quan trọng để đánh giá độ phủ của Retriever.
- **MRR (Mean Reciprocal Rank):** Hiện thực thuật toán tính hạng nghịch đảo trung bình. Chỉ số này không chỉ quan tâm đến việc có tìm thấy tài liệu hay không, mà còn đánh giá tài liệu đó nằm ở vị trí thứ mấy (Rank) trong danh sách kết quả.

### B. Logic Regression & Release Gate (`main.py`)
Tôi đã tái cấu trúc lại luồng chạy chính của hệ thống để hỗ trợ so sánh hiệu năng giữa hai phiên bản Agent (V1 vs V2):
- **Phân tích Delta:** Tính toán sự chênh lệch (Delta) về các chỉ số: Score trung bình, Hit Rate, MRR và Latency.
- **Auto-Gate Logic:** Thiết lập bộ lọc quyết định tự động. Phiên bản mới chỉ được "APPROVE" nếu không làm suy giảm các chỉ số cốt lõi so với phiên bản cũ. Điều này đảm bảo tính ổn định và ngăn chặn lỗi hồi quy (Regression Error) trong sản phẩm thực tế.

---

## 2. Chi tiết kỹ thuật (Technical Depth)

### A. Giải thích MRR (Mean Reciprocal Rank)
MRR là một độ đo chất lượng của hệ thống tìm kiếm thông tin. Công thức tôi sử dụng là $1/rank$ của tài liệu đúng đầu tiên được tìm thấy. 
- **Ví dụ:** Nếu tài liệu chính xác nằm ở vị trí số 1, điểm là 1.0. Nếu nằm ở vị trí số 2, điểm là 0.5. 
- **Ý nghĩa:** MRR khuyến khích hệ thống đưa tài liệu liên quan nhất lên trên cùng, giúp giảm tải công việc cho LLM khi phải xử lý context dài và tránh nhiễu thông tin.

### B. Phân tích sự đánh đổi (Trade-off) giữa Latency và Quality
Trong quá trình triển khai V2, tôi đã nhận thấy sự đánh đổi:
- Khi tăng `top_k` (số lượng chunk được retrieve) từ 2 lên 3, chỉ số **Hit Rate** và **MRR** tăng lên đáng kể (độ chính xác cao hơn). 
- Tuy nhiên, **Latency** cũng tăng lên do LLM phải đọc nhiều context hơn và chi phí Token cũng tăng theo.
- **Giải pháp:** Tôi đã thiết lập logic Regression để đảm bảo rằng việc tăng chất lượng phải xứng đáng với mức tăng của chi phí và thời gian trễ.

---

## 3. Giải quyết vấn đề (Problem Solving)

Trong quá trình thực hiện, tôi đã gặp khó khăn khi tích hợp `RetrievalEvaluator` vào `main.py` do cấu trúc dữ liệu ban đầu không đồng nhất (Agent version ban đầu không trả về `retrieved_ids`).
- **Cách giải quyết:** Tôi đã thống nhất với nhóm về "Contract A" (Chunk ID format) và "Contract C" (Agent response schema) ngay từ đầu. Việc chốt interface sớm đã giúp tôi có thể viết code test module độc lập và đảm bảo khi ghép nối hệ thống không bị lỗi định dạng.

---

## 4. Kết quả đạt được
Toàn bộ code của tôi đã được kiểm tra (Unit Test) và chạy thành công trên bộ Golden Dataset của nhóm, đóng góp trực tiếp vào việc tạo ra báo cáo `reports/summary.json` đạt chuẩn Expert Level (có MRR, Hit Rate và Regression phân tích delta rõ ràng).
