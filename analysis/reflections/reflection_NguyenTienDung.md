# 📊 Báo Cáo Đánh Giá RAG Hệ Thống
**Thời gian thực hiện:** `2026-04-21 16:32:39`
**Phiên bản Base (V1):** `Agent_V1_Base`
**Phiên bản Optimized (V2):** `Agent_V2_Optimized`

## 1. Tóm tắt chỉ số so sánh (Regression Summary)
| Chỉ số (Metrics) | V1 (Baseline) | V2 (Optimized) | Biến thiên (Delta) | Trạng thái |
| :--- | :---: | :---: | :---: | :---: |
| Điểm trung bình (Score) | 1.452 | 3.658 | +2.206 | ✅ |
| Tỉ lệ tìm thấy (Hit Rate) | 0.000 | 0.000 | +0.000 | ✅ |
| MRR | 0.000 | 0.000 | +0.000 | ✅ |
| Độ trễ (Latency) | 0.482s | 1.001s | +0.520s | ❌ |

### 🏁 Quyết định cuối cùng: **APPROVE**

## 2. Chi tiết kết quả Benchmark (Phiên bản V2)
| ID | Câu hỏi | Score | Hit Rate | Latency |
| :--- | :--- | :---: | :---: | :---: |
| N/A | Tài liệu Access Control SOP áp dụng cho ai? | 1.1749999999999998 | 0.0 | 2.43s |
| N/A | Thời gian xử lý cho yêu cầu Level 2 – Standard Access là bao.. | 1.9178571428571427 | 0.0 | 1.59s |
| N/A | Có cần training về security policy cho Level 4 – Admin Acces.. | 1.1083333333333334 | 0.0 | 1.58s |
| N/A | Các bước nào cần thực hiện để cấp quyền truy cập theo quy tr.. | 1.8 | 0.0 | 1.44s |
| N/A | Nếu cần cấp quyền gấp trong trường hợp khẩn cấp, quy trình e.. | 1.0 | 0.0 | 1.73s |
| N/A | Quyền truy cập sẽ bị thu hồi trong trường hợp nào? | 1.1386363636363637 | 0.0 | 0.36s |
| N/A | Nếu tôi cần thông tin về Audit log, tôi sẽ tìm ở đâu? | 2.333333333333333 | 0.0 | 0.32s |
| N/A | Hãy cho tôi biết toàn bộ quy trình tạo Access Request mà khô.. | 1.5750000000000002 | 0.0 | 0.28s |
| N/A | Khi một nhân viên đổi công ty, quyền truy cập của họ sẽ được.. | 1.1083333333333334 | 0.0 | 0.26s |
| N/A | Nếu một nhân viên được cấp quyền tạm thời, họ có thể giữ quy.. | 2.7142857142857144 | 0.0 | 0.59s |
| N/A | Cần bao nhiêu ngày làm việc để cấp quyền cho một nhân viên c.. | 1.3464285714285715 | 0.0 | 0.33s |
| N/A | Quá trình audit định kỳ diễn ra thường xuyên như thế nào? | 1.5750000000000002 | 0.0 | 0.52s |
| N/A | Nhân viên có bao nhiêu ngày nghỉ phép năm nếu họ có 4 năm ki.. | 1.0 | 0.0 | 0.53s |
| N/A | Quy trình nào cần thực hiện để xin nghỉ phép? | 1.0 | 0.0 | 0.50s |
| N/A | Nếu một nhân viên xin nghỉ ốm 4 ngày liên tiếp, họ cần gì? | 1.275 | 0.0 | 0.59s |
| N/A | Nghỉ phép năm có thể chuyển sang năm sau tối đa bao nhiêu ng.. | 1.4808823529411765 | 0.0 | 0.35s |
| N/A | Ai phải phê duyệt lịch remote làm việc của nhân viên? | 1.2194444444444446 | 0.0 | 0.32s |
| N/A | Nhân viên nghỉ thai sản có thể được nghỉ bao lâu để nuôi con.. | 1.1749999999999998 | 0.0 | 0.34s |
| N/A | Tôi đã gửi yêu cầu nghỉ phép qua HR Portal nhưng chưa nhận đ.. | 1.0 | 0.0 | 0.27s |
| N/A | Nghỉ phép có được trả lương không? | 1.5750000000000002 | 0.0 | 0.60s |
| N/A | Có thể quay lại làm việc tại công ty trong trường hợp tôi kh.. | 3.763157894736842 | 0.0 | 0.37s |
| N/A | Nếu tôi làm việc từ xa, có cần bật camera trong các cuộc họp.. | 1.1386363636363637 | 0.0 | 0.29s |
| N/A | Nếu tôi làm việc vào ngày lễ, tôi sẽ được trả lương bao nhiê.. | 1.275 | 0.0 | 0.42s |
| N/A | Tôi đã làm việc cho công ty được 6 năm và tôi đã sử dụng hết.. | 1.275 | 0.0 | 0.34s |
| N/A | Tôi quên mật khẩu, phải làm gì? | 1.1749999999999998 | 0.0 | 0.35s |
| N/A | Công ty dùng phần mềm VPN nào? | 1.0607142857142855 | 0.0 | 0.35s |
| N/A | Mật khẩu phải thay đổi định kỳ sau bao lâu? | 1.0 | 0.0 | 0.28s |
| N/A | Nếu tôi không biết cách tạo ticket, tôi có thể làm gì? | 2.473684210526316 | 0.0 | 0.34s |
| N/A | Tài khoản có thể được kết nối VPN trên bao nhiêu thiết bị cù.. | 1.3083333333333331 | 0.0 | 0.26s |
| N/A | Nếu laptop tôi bị hỏng, tôi có cần phải xác định mức độ nghi.. | 1.1960526315789473 | 0.0 | 0.61s |
| N/A | Nếu tôi cần cài phần mềm mới, chỉ tôi có thể yêu cầu không? | 1.0 | 0.0 | 0.35s |
| N/A | Có phải tất cả tài khoản sẽ được khóa sau 3 lần đăng nhập sa.. | 1.4808823529411765 | 0.0 | 0.31s |
| N/A | Laptop sẽ được cấp ngay khi vào công ty hay chỉ sau một khoả.. | 2.958823529411765 | 0.0 | 0.56s |
| N/A | Cách tốt nhất để xử lý một email quan trọng bị mất là gì? | 1.1386363636363637 | 0.0 | 0.55s |
| N/A | Chúng ta có bao nhiêu loại phần mềm để quản lý license? | 1.775 | 0.0 | 0.33s |
| N/A | Có cách nào khác để liên lạc với IT Helpdesk ngoài số điện t.. | 1.025 | 0.0 | 0.37s |
| N/A | Chính sách hoàn tiền này áp dụng cho các đơn hàng từ khi nào.. | 1.375 | 0.0 | 0.32s |
| N/A | Khách hàng cần gửi yêu cầu hoàn tiền trong vòng bao lâu kể t.. | 1.0 | 0.0 | 0.31s |
| N/A | Sẽ có những sản phẩm nào không được hoàn tiền? | 1.4416666666666664 | 0.0 | 0.32s |
| N/A | Quy trình xử lý yêu cầu hoàn tiền gồm mấy bước và ai là ngườ.. | 1.0712962962962962 | 0.0 | 0.32s |
| N/A | Khách hàng có thể chọn hình thức hoàn tiền nào? | 1.0102941176470588 | 0.0 | 0.35s |
| N/A | Nếu khách hàng yêu cầu hoàn tiền cho sản phẩm đã kích hoạt, .. | 4.2 | 0.0 | 0.28s |
| N/A | Đặt câu hỏi về quyền lợi của khách hàng về hoàn tiền, nhưng .. | 1.0102941176470588 | 0.0 | 0.31s |
| N/A | Nếu một sản phẩm bị lỗi nhưng khách hàng không đáp ứng yêu c.. | 1.275 | 0.0 | 0.28s |
| N/A | Theo chính sách hoàn tiền, nếu tôi đã sử dụng sản phẩm, có c.. | 1.775 | 0.0 | 0.34s |
| N/A | Có những điều kiện nào khác ngoài việc sản phẩm bị lỗi do nh.. | 1.4706521739130434 | 0.0 | 0.35s |
| N/A | Tại sao một số sản phẩm không được hoàn tiền ngay cả khi chú.. | 1.4416666666666664 | 0.0 | 0.32s |
| N/A | Nếu tôi không biết số thứ tự đơn hàng của mình, tôi có thể y.. | 1.2194444444444446 | 0.0 | 0.29s |
| N/A | Mức độ ưu tiên P1 định nghĩa như thế nào? | 1.775 | 0.0 | 0.30s |
| N/A | Thời gian phản hồi ban đầu cho ticket P2 là bao lâu? | 1.0 | 0.0 | 0.34s |
| N/A | Một sự cố có ảnh hưởng một phần hệ thống, có workaround tạm .. | 1.0 | 0.0 | 0.32s |
| N/A | Quy trình nào được thực hiện ngay lập tức sau khi tiếp nhận .. | 1.2194444444444446 | 0.0 | 0.28s |
| N/A | Theo quy định, thời gian xử lý và khắc phục cho ticket P3 là.. | 1.9178571428571427 | 0.0 | 0.30s |
| N/A | Nếu một ticket P1 không nhận được phản hồi trong bao lâu thì.. | 1.1386363636363637 | 0.0 | 0.29s |
| N/A | Sự cố nào dưới đây có thể bị lừa Agent để trả lời không liên.. | 1.2194444444444446 | 0.0 | 0.35s |
| N/A | Theo quy định, thời hạn xử lý ticket P4 được dựa trên yếu tố.. | 1.8499999999999999 | 0.0 | 0.35s |
| N/A | Nếu không có quy định nào về các mức độ ưu tiên mới, một sự .. | 1.1749999999999998 | 0.0 | 0.57s |
| N/A | Thông báo cho stakeholder được thực hiện khi nào trong quy t.. | 1.0 | 0.0 | 0.35s |
| N/A | Cần làm gì nếu một engineer không thể xử lý ticket P1 sau 30.. | 1.0 | 0.0 | 0.31s |
| N/A | Ai là người nhận ticket P1 đầu tiên theo quy định? | 1.0 | 0.0 | 0.34s |
