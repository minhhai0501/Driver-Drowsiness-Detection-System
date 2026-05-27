# Hệ thống Nhận diện Buồn ngủ của Tài xế (Driver Drowsiness Detection System)

Ứng dụng thị giác máy tính thời gian thực, chi phí thấp nhằm phát hiện trạng thái mệt mỏi, buồn ngủ của tài xế bằng trí tuệ nhân tạo (AI) để chủ động giảm thiểu tai nạn giao thông.

---

## 🚀 Tính năng nổi bật
* **Nhận diện Thời gian thực (Real-time):** Tốc độ theo dõi các điểm mốc trên khuôn mặt cực nhanh, tối ưu hóa chạy trên CPU thông thường (không yêu cầu GPU mạnh).
* **Phân tích Điểm mốc Nâng cao:** Sử dụng lưới khuôn mặt 3D dày đặc với 478 điểm mốc (MediaPipe) để theo dõi mắt chính xác ngay cả trong điều kiện ánh sáng thay đổi.
* **Hệ thống Cảnh báo Thông minh:** Áp dụng thuật toán **EAR (Eye Aspect Ratio)**. Tự động kích hoạt âm thanh cảnh báo ngay lập tức nếu mắt tài xế nhắm quá thời gian quy định (khoảng 1-2 giây).
* **Kiến trúc Tối ưu & Nhẹ:** Được thiết kế tối giản, sẵn sàng cho định hướng nhúng và đóng gói lên các thiết bị phần cứng phần biên như **Raspberry Pi**.

---

## 🛠 Công nghệ & Thư viện lõi
* **Ngôn ngữ lập trình:** Python
* **Thị giác máy tính & AI:**
  * **MediaPipe Face Mesh (Google):** Trích xuất nhanh và chính xác tọa độ các điểm mốc trên khuôn mặt.
  * **OpenCV:** Đọc luồng video từ webcam, xử lý hình ảnh và hiển thị giao diện người dùng.
* **Toán học & Logic:** NumPy (tính toán khoảng cách vectơ và chỉ số EAR).

---

## 📐 Nguyên lý hoạt động (Giải thuật EAR)
Hệ thống tính toán tỷ lệ khung hình mắt (Eye Aspect Ratio - EAR) dựa trên 6 điểm mốc bao quanh mỗi mắt do MediaPipe cung cấp:

$$\text{EAR} = \frac{||p_2 - p_6|| + ||p_3 - p_5||}{2 \cdot ||p_1 - p_4||}$$

* **Khi mắt mở:** Khoảng cách dọc lớn $\rightarrow$ Chỉ số EAR cao.
* **Khi mắt nhắm:** Khoảng cách dọc tiến về 0 $\rightarrow$ Chỉ số EAR giảm xuống dưới ngưỡng cài đặt (thường là $\approx 0.25$).
* **Cơ chế kích hoạt:** Nếu EAR duy trì dưới ngưỡng liên tục trong 30 khung hình (frames), hệ thống sẽ phát âm thanh cảnh báo tài xế.

---
