# BÁO CÁO CÁ NHÂN - LAB DAY 14

**Họ và tên:** Khương Quang Vinh
**Nhóm:** Team 61 - Lab14-E403
**Vai trò:** AI Engineer / Data Specialist

---

## 👤 2. Điểm Cá nhân (Tối đa 40 điểm)

### Engineering Contribution

Trong dự án này, tôi chịu trách nhiệm chính về mảng **Dataset & Synthetic Data Generation**, cụ thể:

1.  **Module Synthetic Data Generation (`data/synthetic_gen.py`):**
    *   Tái cấu trúc script để sinh dữ liệu trực tiếp từ các tài liệu nghiệp vụ thực tế trong thư mục `data/docs/`, thay thế hoàn toàn dữ liệu mẫu.
    *   Thiết kế hệ thống Prompt Engineering phức tạp để LLM sinh ra các bộ dữ liệu có cấu trúc chặt chẽ theo đúng schema JSON yêu cầu.
    *   **Kết quả:** Tạo ra bộ **Golden Dataset** gồm **60 test cases** chất lượng cao, phục vụ làm benchmark cho toàn nhóm.

2.  **Thiết kế Hard Cases & Red Teaming:**
    *   Trực tiếp triển khai logic sinh các loại câu hỏi medium, hard, để thử thách hệ thống RAG:
        *   **Adversarial:** Thử nghiệm các câu hỏi nhằm phá vỡ chính sách bảo mật.
        *   **Out-of-context:** Kiểm tra khả năng từ chối trả lời khi thông tin không có trong tài liệu.
        *   **Conflicting Info:** Đưa ra giả định sai để kiểm tra tính chính xác của Agent.
        *   **Ambiguous & Multi-turn:** Giả lập các tình huống hội thoại mập mờ hoặc cần hiệu chỉnh thông tin.

---

### 📚 Technical Depth (15/15 điểm)

Tôi đã áp dụng các kiến thức chuyên sâu về đánh giá hệ thống AI:

1.  **Cấu trúc Golden Dataset:** Hiểu rõ tầm quan trọng của việc mapping `expected_retrieval_ids` chính xác đến từng Section/Chunk để đánh giá Hit Rate và MRR một cách khách quan.
2.  **Kỹ thuật Ground Truth Engineering:** Đảm bảo `expected_answer` không chỉ đúng về nội dung mà còn bám sát văn phong của tài liệu nguồn để Judge có thể chấm điểm chính xác nhất.
3.  **Chiến lược Đa dạng hóa Dữ liệu:** Hiểu về sự cân bằng giữa các loại câu hỏi (Easy/Medium/Hard) để bộ benchmark không quá dễ (gây ảo tưởng về sức mạnh hệ thống) cũng không quá khó (gây nản lòng khi debug).
4.  **Trade-off trong SDG:** Sử dụng mô hình mạnh (GPT-4o) để sinh dữ liệu chất lượng cao làm "tiêu chuẩn vàng", chấp nhận chi phí cao hơn ở bước chuẩn bị để tiết kiệm thời gian fix lỗi logic về sau.

---

###  Problem Solving

Các vấn đề tôi đã giải quyết trong quá trình làm Data:

*   **Vấn đề Hallucination trong SDG:** LLM đôi khi tự bịa ra thông tin không có trong context. Tôi đã giải quyết bằng cách siết chặt System Prompt và yêu cầu LLM trích dẫn Section ID cụ thể cho mỗi câu trả lời.
*   **Xử lý định dạng JSON:** Đảm bảo kết quả trả về từ API luôn là JSON hợp lệ để không làm gãy pipeline tự động.
*   **Tối ưu hóa quy trình sinh dữ liệu:** Sử dụng `asyncio` và `tqdm` để quản lý quá trình sinh dữ liệu từ nhiều tệp tin lớn, đảm bảo hiệu suất và khả năng theo dõi tiến độ.

---

**Minh chứng kỹ thuật:** File dữ liệu `data/golden_set.jsonl` với 60 cases đầy đủ metadata, 
file code `data/synthetic_gen.py`


 

