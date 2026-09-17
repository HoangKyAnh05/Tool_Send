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

# Tắt fail-safe của PyAutoGUI tránh lỗi gián đoạn khi chuột sát mép màn hình
pyautogui.FAILSAFE = False

class UIAutomator:
    def __init__(self):
        self.calibration = config.load_calibration()
        self.completion_watcher = None

    def set_watcher(self, watcher):
        self.completion_watcher = watcher

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
                # Ô chat Antigravity nằm ở góc dưới khu vực bên phải
                chat_x = rect["left"] + int(rect["width"] * 0.55)
                chat_y = rect["bottom"] - 80
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
        time.sleep(0.5)

        # Đánh dấu tác vụ đang chạy để watcher tự động thông báo khi hoàn thành
        if self.completion_watcher:
            self.completion_watcher.mark_task_started(title)

        # Chụp ảnh xác nhận gửi thành công
        screen_path = capture_screen(hwnd, output_filename="after_send.jpg")
        return True, f"Đã gửi câu lệnh vào {title}!", screen_path

    def undo_prompt(self):
        """
        Hoàn tác (Undo) câu lệnh gần nhất trong Antigravity IDE:
        1. Focus vào Antigravity IDE
        2. Click vào nút [ ← ] Rollback Checkpoint trên thanh trạng thái
        3. Rê chuột click nút Undo cạnh timestamp
        4. Focus vào ô Chat và gọi phím Up để lấy lại nội dung câu lệnh
        5. Chụp ảnh màn hình Live xác nhận
        """
        hwnd, title = self.get_target_window()
        rect = get_window_rect(hwnd) if hwnd else None

        if rect:
            # 1. Click nút [ ← ] Rollback trên thanh Checkpoint bar
            rollback_x = rect["left"] + int(rect["width"] * 0.37)
            rollback_y = rect["bottom"] - 170
            pyautogui.click(rollback_x, rollback_y)
            time.sleep(0.2)

            # 2. Rê chuột vào vùng tin nhắn cuối cùng để kích hoạt nút hover Undo
            hover_x = rect["left"] + int(rect["width"] * 0.70)
            hover_y = rect["bottom"] - 250
            pyautogui.moveTo(hover_x, hover_y, duration=0.1)
            time.sleep(0.15)
            undo_click_x = rect["left"] + int(rect["width"] * 0.76)
            pyautogui.click(undo_click_x, hover_y)
            time.sleep(0.2)

        # 3. Focus vào ô Chat và gọi lại prompt cũ bằng phím Up
        self.focus_chat_input(hwnd)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(0.05)
        pyautogui.press('up')
        time.sleep(0.3)

        screen_path = capture_screen(hwnd, output_filename="undo_done.jpg")
        return True, f"Đã hoàn tác (Undo) câu lệnh gần nhất trên {title}!", screen_path

    def stop_task(self):
        """
        Dừng ngay lập tức tác vụ đang chạy trong Antigravity IDE (Stop Task):
        1. Focus vào ô chat / vùng agent đang chạy
        2. Bấm Escape 3 lần liên tiếp
        3. Gửi Ctrl + C
        4. Click vào nút tròn Stop ở góc phải ô chat
        5. Click vào nút Stop trên thanh trạng thái
        """
        hwnd, title = self.get_target_window()
        rect = get_window_rect(hwnd) if hwnd else None

        # 1. Focus ô chat / vùng agent
        self.focus_chat_input(hwnd)
        time.sleep(0.05)

        # 2. Gửi chuỗi phím dừng tác vụ
        pyautogui.press('escape')
        time.sleep(0.05)
        pyautogui.press('escape')
        time.sleep(0.05)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.05)

        # 3. Click nút tròn Stop ở góc phải ô chat (Send đổi thành Stop)
        if rect:
            stop_circle_x = rect["right"] - 50
            stop_circle_y = rect["bottom"] - 50
            pyautogui.click(stop_circle_x, stop_circle_y)
            time.sleep(0.1)

            # Click nút Stop trên thanh Checkpoint / Status bar
            stop_bar_x = rect["left"] + int(rect["width"] * 0.94)
            stop_bar_y = rect["bottom"] - 150
            pyautogui.click(stop_bar_x, stop_bar_y)
            time.sleep(0.05)

            pyautogui.press('escape')

        if self.completion_watcher:
            self.completion_watcher.mark_task_stopped()

        time.sleep(0.3)
        screen_path = capture_screen(hwnd, output_filename="stop_done.jpg")
        return True, f"Đã gửi lệnh dừng tác vụ (Stop Task) trên {title}!", screen_path

    def accept_all(self):
        """Thực hiện hành động Accept All bằng Computer Vision + Click chuột trực tiếp"""
        return self._smart_click_button("accept")

    def reject_all(self):
        """Thực hiện hành động Reject All bằng Computer Vision + Click chuột trực tiếp"""
        return self._smart_click_button("reject")

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
                fallback_y = rect["bottom"] - 150
            else:  # Reject all nằm bên trái Accept all
                fallback_x = rect["left"] + int(rect["width"] * 0.88)
                fallback_y = rect["bottom"] - 150

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
            roi_y1, roi_y2 = int(img_h * 0.50), int(img_h * 0.98)
            roi_x1, roi_x2 = int(img_w * 0.40), int(img_w * 0.99)
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
            return None
