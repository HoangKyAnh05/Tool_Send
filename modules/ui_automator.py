import time
import pyautogui
import cv2
import numpy as np
from pathlib import Path
from PIL import Image

import config
from modules.window_manager import find_antigravity_window, focus_window, get_window_rect
from modules.clipboard_manager import copy_text_to_clipboard, copy_image_to_clipboard
from modules.screen_capturer import capture_screen

# Tắt fail-safe của PyAutoGUI tránh lỗi ném ngoại lệ khi chuột di chuyển sát mép
pyautogui.FAILSAFE = False

class UIAutomator:
    def __init__(self):
        self.calibration = config.load_calibration()

    def reload_calibration(self):
        self.calibration = config.load_calibration()

    def get_target_window(self):
        """Tìm và focus vào đúng cửa sổ Antigravity IDE đang chọn"""
        hwnd, title = find_antigravity_window(config.WINDOW_TITLE_KEYWORD)
        if hwnd:
            focus_window(hwnd)
            time.sleep(0.15)
            return hwnd, title
        return None, "Cửa sổ Antigravity"

    def focus_chat_input(self, hwnd=None):
        """Đưa con trỏ chuột và tiêu điểm vào ô nhập liệu Chat của Antigravity IDE"""
        if self.calibration.get("chat_input"):
            cx, cy = self.calibration["chat_input"]
            pyautogui.click(cx, cy)
            time.sleep(0.1)
            return

        if hwnd:
            rect = get_window_rect(hwnd)
            if rect:
                # Ô chat Antigravity nằm ở góc dưới khu vực bên phải (khoảng 60% width, cách đáy 55px)
                chat_x = rect["left"] + int(rect["width"] * 0.60)
                chat_y = rect["bottom"] - 55
                pyautogui.click(chat_x, chat_y)
                time.sleep(0.1)

    def send_prompt(self, text: str = "", image_path: str = None):
        """
        Gửi câu lệnh văn bản tiếng Việt và/hoặc ảnh vào ô chat Antigravity IDE đang chọn
        """
        hwnd, title = self.get_target_window()

        # 1. Đưa tiêu điểm vào ô Chat
        self.focus_chat_input(hwnd)

        # 2. Nếu có ảnh: Copy vào Clipboard và Dán
        if image_path and Path(image_path).exists():
            img_ok = copy_image_to_clipboard(image_path)
            if img_ok:
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.6)

        # 3. Nếu có text: Copy vào Clipboard chuẩn Unicode tiếng Việt và Dán
        if text and text.strip():
            copy_text_to_clipboard(text.strip())
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(config.PASTE_DELAY)

        # 4. Bấm Enter để thực thi
        pyautogui.press('enter')
        time.sleep(0.6)

        # Chụp ảnh xác nhận gửi thành công
        screen_path = capture_screen(hwnd, output_filename="after_send.jpg")
        return True, f"Đã gửi câu lệnh vào {title}!", screen_path

    def undo_prompt(self):
        """
        Hoàn tác / Khôi phục lại câu lệnh trước trong ô chat Antigravity IDE
        (Phím mũi tên LÊN 'Up' hoặc Ctrl+Z trong ô Chat)
        """
        hwnd, title = self.get_target_window()

        # Focus ô chat
        self.focus_chat_input(hwnd)

        # Gửi phím mũi tên Lên để gọi lại prompt vừa gửi trước đó
        pyautogui.press('up')
        time.sleep(0.3)

        screen_path = capture_screen(hwnd, output_filename="undo_done.jpg")
        return True, f"Đã hoàn tác / gọi lại câu lệnh trước trên {title}!", screen_path

    def accept_all(self):
        """Thực hiện hành động Accept All bằng Computer Vision + Click chuột trực tiếp"""
        return self._smart_click_button("accept")

    def reject_all(self):
        """Thực hiện hành động Reject All bằng Computer Vision + Click chuột trực tiếp"""
        return self._smart_click_button("reject")

    def stop_task(self):
        """Dừng tiến trình hiện tại (Ctrl + C hoặc Escape)"""
        hwnd, title = self.get_target_window()
        pyautogui.hotkey('ctrl', 'c')
        pyautogui.press('escape')
        time.sleep(0.3)
        screen_path = capture_screen(hwnd, output_filename="stop_done.jpg")
        return True, f"Đã gửi lệnh dừng tác vụ trên {title}!", screen_path

    def _smart_click_button(self, action_type="accept"):
        """
        Thuật toán phát hiện vị trí nút bấm thông minh bằng Computer Vision:
        1. Chụp ảnh màn hình thực tế của Antigravity IDE
        2. Quét vùng góc dưới bên phải để nhận diện nút màu xanh 'Accept all' hoặc nút 'Reject all'
        3. Click chuột trực tiếp vào toạ độ thực tế của nút bấm trên màn hình Desktop
        """
        hwnd, title = self.get_target_window()
        rect = get_window_rect(hwnd) if hwnd else None

        # 1. Kiểm tra toạ độ thủ công đã hiệu chỉnh (nếu có)
        calib_key = f"{action_type}_button"
        if self.calibration.get(calib_key):
            cx, cy = self.calibration[calib_key]
            pyautogui.click(cx, cy)
            time.sleep(0.4)
            screen_path = capture_screen(hwnd, output_filename=f"{action_type}_done.jpg")
            return True, f"Đã click {action_type.upper()} tại toạ độ ({cx}, {cy})!", screen_path

        # 2. Sử dụng Computer Vision để tìm toạ độ nút màu xanh trên màn hình
        found_coords = None
        if rect:
            temp_scan_path = capture_screen(hwnd, output_filename="cv_button_scan.jpg", max_dim=4000)
            if Path(temp_scan_path).exists():
                found_coords = self._detect_button_coords_cv(temp_scan_path, rect, action_type)

        # 3. Thực hiện Click chuột nếu tìm thấy toạ độ
        if found_coords:
            click_x, click_y = found_coords
            pyautogui.moveTo(click_x, click_y, duration=0.1)
            pyautogui.click(click_x, click_y)
            time.sleep(0.4)
            screen_path = capture_screen(hwnd, output_filename=f"{action_type}_done.jpg")
            return True, f"Đã nhận diện và click nút {action_type.upper()} thành công!", screen_path

        # 4. Fallback ước lượng theo tỉ lệ màn hình chuẩn của Antigravity IDE
        if rect:
            # Trong Antigravity IDE:
            # Nút Accept all nằm ở khoảng 94% chiều ngang, 87% chiều dọc (ngay trên ô chat)
            if action_type == "accept":
                fallback_x = rect["left"] + int(rect["width"] * 0.94)
                fallback_y = rect["bottom"] - 95
            else:  # Reject all nằm bên trái Accept all
                fallback_x = rect["left"] + int(rect["width"] * 0.88)
                fallback_y = rect["bottom"] - 95

            pyautogui.moveTo(fallback_x, fallback_y, duration=0.1)
            pyautogui.click(fallback_x, fallback_y)
            time.sleep(0.4)
            screen_path = capture_screen(hwnd, output_filename=f"{action_type}_done.jpg")
            return True, f"Đã click vị trí {action_type.upper()} ({fallback_x}, {fallback_y})!", screen_path

        # 5. Phím tắt dự phòng cuối cùng
        hotkeys = {
            "accept": ["ctrl", "alt", "enter"],
            "reject": ["escape"]
        }
        hk = hotkeys.get(action_type, ["enter"])
        if len(hk) > 1:
            pyautogui.hotkey(*hk)
        else:
            pyautogui.press(hk[0])
        time.sleep(0.3)
        screen_path = capture_screen(hwnd, output_filename=f"{action_type}_done.jpg")
        return True, f"Đã gửi lệnh {action_type.upper()}!", screen_path

    def _detect_button_coords_cv(self, img_path, win_rect, action_type):
        """Phát hiện toạ độ nút màu xanh của Antigravity IDE bằng Computer Vision"""
        try:
            img = cv2.imread(str(img_path))
            if img is None:
                return None

            img_h, img_w, _ = img.shape

            # Vùng quét: Góc dưới bên phải (nơi đặt các nút Accept/Reject)
            roi_y1, roi_y2 = int(img_h * 0.6), int(img_h * 0.98)
            roi_x1, roi_x2 = int(img_w * 0.5), int(img_w * 0.99)
            roi = img[roi_y1:roi_y2, roi_x1:roi_x2]

            # Bộ lọc màu xanh dương (Blue/Cyan của nút Accept all trong Antigravity)
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            lower_blue = np.array([85, 70, 70])
            upper_blue = np.array([135, 255, 255])
            mask = cv2.inRange(hsv, lower_blue, upper_blue)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            accept_center = None
            for cnt in contours:
                bx, by, bw, bh = cv2.boundingRect(cnt)
                # Kích thước của nút Accept All tiêu chuẩn
                if 25 < bw < 250 and 10 < bh < 60:
                    accept_center = (roi_x1 + bx + bw // 2, roi_y1 + by + bh // 2)
                    break

            if not accept_center:
                return None

            # Tỉ lệ quy đổi từ ảnh chụp sang toạ độ màn hình Desktop thực tế
            scale_x = win_rect["width"] / img_w
            scale_y = win_rect["height"] / img_h

            if action_type == "accept":
                final_x = win_rect["left"] + int(accept_center[0] * scale_x)
                final_y = win_rect["top"] + int(accept_center[1] * scale_y)
            else:  # Nút Reject all nằm bên trái Accept all khoảng 65-70px
                offset = int(65 * scale_x)
                final_x = win_rect["left"] + int(accept_center[0] * scale_x) - offset
                final_y = win_rect["top"] + int(accept_center[1] * scale_y)

            return final_x, final_y
        except Exception as e:
            print(f"[UIAutomator] Lỗi nhận diện CV: {e}")
            return None
