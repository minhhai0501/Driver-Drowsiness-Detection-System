# ============================================================
# HỆ THỐNG CẢNH BÁO TÀI XẾ - MEDIAPIPE + YOLOv8
# ============================================================

import cv2
import numpy as np
import time
import threading
from playsound import playsound
import mediapipe as mp

# ---------------------- CÀI ĐẶT THAM SỐ ----------------------
EAR_THRESH = 0.25          # Ngưỡng EAR (Eye Aspect Ratio)
EAR_CONSEC_FRAMES = 30     # Số frame liên tiếp mắt nhắm
ALARM_SOUND_PATH = "alert.wav"
YOLO_CONF_THRESH = 0.5     # Ngưỡng tin cậy YOLO

# ---------------------- KHỞI TẠO -----------------------------
print("[INFO] Đang khởi động hệ thống...")

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False,
                                  max_num_faces=1,
                                  refine_landmarks=True,
                                  min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)
COUNTER = 0
ALARM_ON = False
PHONE_DETECTED = False

# ---------------------- HÀM HỖ TRỢ ---------------------------
def sound_alarm(path):
    """Phát âm thanh cảnh báo trong luồng riêng"""
    playsound(path)

def euclidean_dist(a, b):
    return np.linalg.norm(a - b)

def eye_aspect_ratio(landmarks, eye_indices):
    """Tính EAR (Eye Aspect Ratio) dựa vào các điểm mốc mắt"""
    p1 = np.array(landmarks[eye_indices[0]])
    p2 = np.array(landmarks[eye_indices[1]])
    p3 = np.array(landmarks[eye_indices[2]])
    p4 = np.array(landmarks[eye_indices[3]])
    p5 = np.array(landmarks[eye_indices[4]])
    p6 = np.array(landmarks[eye_indices[5]])

    A = euclidean_dist(p2, p6)
    B = euclidean_dist(p3, p5)
    C = euclidean_dist(p1, p4)

    ear = (A + B) / (2.0 * C)
    return ear

# Các chỉ số điểm mốc cho mắt trái và phải trong MediaPipe
LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]

# ---------------------- LUỒNG VIDEO --------------------------
cap = cv2.VideoCapture(0)
time.sleep(1.0)
print("[INFO] Camera sẵn sàng...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #PHÁT HIỆN BUỒN NGỦ (EYE BLINK) ---
    results = face_mesh.process(rgb)
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            
            # Chuyển đổi 478 điểm mốc sang tọa độ pixel
            landmarks = []
            for lm in face_landmarks.landmark:
                # Ép kiểu int ngay tại đây để dùng cho cv2
                landmarks.append((int(lm.x * w), int(lm.y * h))) 

            # =======================================================
            # PHẦN VẼ MẶT VÀ MẮT (THEO YÊU CẦU)
            # =======================================================

            # 1. Vẽ lưới bao phủ khuôn mặt (Face Mesh Tessellation)
            mp_drawing = mp.solutions.drawing_utils
            custom_connections = []
            custom_connections.extend(mp_face_mesh.FACEMESH_LEFT_EYE)
            custom_connections.extend(mp_face_mesh.FACEMESH_RIGHT_EYE)
            custom_connections.extend(mp_face_mesh.FACEMESH_FACE_OVAL)

            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                
                # Sử dụng danh sách đường nối tùy chỉnh ở trên
                connections=custom_connections, 
                
                landmark_drawing_spec=None, # Không vẽ 478 chấm
                connection_drawing_spec=mp_drawing.DrawingSpec(
                    color=(0, 255, 0), thickness=1, circle_radius=1) # Viền màu xanh lá
            )

            # 2. Vẽ 12 chấm tròn ở hai mắt (dùng để tính EAR)
            # Nối 2 danh sách chỉ số mắt trái và phải lại
            eye_indices_to_draw = LEFT_EYE_IDX + RIGHT_EYE_IDX
            
            for idx in eye_indices_to_draw:
                if 0 <= idx < len(landmarks): # Kiểm tra chỉ số hợp lệ
                    point = landmarks[idx] # Lấy tọa độ (x, y) đã tính
                    
                    # Vẽ chấm tròn màu VÀNG (BGR: 0, 255, 255), bán kính 2px, tô đầy
                    cv2.circle(frame, point, 2, (0, 255, 255), -1) 
            # =======================================================

            # Tính toán EAR
            leftEAR = eye_aspect_ratio(landmarks, LEFT_EYE_IDX)
            rightEAR = eye_aspect_ratio(landmarks, RIGHT_EYE_IDX)
            ear = (leftEAR + rightEAR) / 2.0

            # Hiển thị EAR
            cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Logic phát hiện buồn ngủ
            if ear < EAR_THRESH:
                COUNTER += 1
                if COUNTER >= EAR_CONSEC_FRAMES:
                    if not ALARM_ON:
                        ALARM_ON = True
                        threading.Thread(target=sound_alarm,
                                         args=(ALARM_SOUND_PATH,),
                                         daemon=True).start()
                    cv2.putText(frame, "BUON NGU!", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            else:
                COUNTER = 0
                if not PHONE_DETECTED:
                    ALARM_ON = False

    # --- 3. HIỂN THỊ CẢNH BÁO CHUNG ---
    if PHONE_DETECTED and not ALARM_ON:
        ALARM_ON = True
        threading.Thread(target=sound_alarm,
                         args=(ALARM_SOUND_PATH,),
                         daemon=True).start()

    if ALARM_ON:
        cv2.putText(frame, "** CANH BAO! **", (w - 230, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # --- HIỂN THỊ VIDEO ---
    cv2.imshow("He thong canh bao tai xe - MediaPipe", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

print("[INFO] Dang tat ung dung...")
cap.release()
cv2.destroyAllWindows()
