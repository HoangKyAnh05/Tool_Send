import time
import threading
from pathlib import Path
from PIL import Image

import config
from modules.window_manager import find_antigravity_window, get_all_antigravity_windows
from modules.screen_capturer import capture_screen

class TaskCompletionWatcher:
    """
    Luồng giám sát trạng thái Antigravity IDE ngầm (Background Thread):
    Tự động phát hiện khi Antigravity hoàn thành câu lệnh / code xong / xuất hiện nút Accept All,
    và gửi ngay thông báo kèm ảnh màn hình Live Screen về Telegram!
    """
    def __init__(self, bot, automator):
        self.bot = bot
        self.automator = automator
        self.running = False
        self.thread = None
        
        self.is_task_active = False
        self.task_start_time = 0
        self.last_notified_time = 0
        self.last_seen_accept_button = False

    def mark_task_started(self, project_title=""):
        """Được gọi khi người dùng vừa gửi câu lệnh từ điện thoại"""
        self.is_task_active = True
        self.task_start_time = time.time()
        self.last_seen_accept_button = False

    def mark_task_stopped(self):
        """Được gọi khi người dùng bấm dừng task"""
        self.is_task_active = False

    def start(self):
        """Bắt đầu chạy luồng giám sát ngầm"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _watch_loop(self):
        time.sleep(2)
        while self.running:
            try:
                time.sleep(1.5)
                now = time.time()

                # Không thông báo lặp lại trong vòng 6 giây
                if now - self.last_notified_time < 6:
                    continue

                hwnd, title = find_antigravity_window()
                if not hwnd:
                    continue

                # 1. Kiểm tra sự xuất hiện của nút Accept All bằng Computer Vision
                temp_scan = capture_screen(hwnd, output_filename="cv_watch_scan.jpg", max_dim=2000)
                from modules.window_manager import get_window_rect
                win_rect = get_window_rect(hwnd)
                
                has_accept_btn = False
                if win_rect and Path(temp_scan).exists():
                    coords = self.automator._detect_button_coords_cv(temp_scan, win_rect, "accept")
                    if coords is not None:
                        has_accept_btn = True

                # Điều kiện kích hoạt thông báo hoàn thành:
                # - Task vừa chạy xong và xuất hiện nút Accept All
                # - HOẶC vừa từ trạng thái không có nút sang có nút Accept All
                # - HOẶC task được đánh dấu đang chạy (is_task_active) và đã trôi qua ít nhất 3 giây
                should_notify = False
                duration_str = ""

                if self.is_task_active and (now - self.task_start_time >= 3):
                    if has_accept_btn or (now - self.task_start_time >= 8 and not self.last_seen_accept_button):
                        should_notify = True
                        dur = int(now - self.task_start_time)
                        duration_str = f"⏱️ Thời gian xử lý: ~{dur}s\n"

                elif has_accept_btn and not self.last_seen_accept_button:
                    # Người dùng thao tác hoặc AI vừa tạo diffs mới
                    should_notify = True

                self.last_seen_accept_button = has_accept_btn

                if should_notify:
                    self.is_task_active = False
                    self.last_notified_time = now
                    self._send_completion_alert(hwnd, title, duration_str)

            except Exception as e:
                # Tránh dừng luồng khi gặp lỗi tạm thời
                pass

    def _send_completion_alert(self, hwnd, title, duration_str=""):
        """Gửi thông báo hoàn thành câu lệnh kèm ảnh chụp thực tế về Telegram"""
        try:
            from modules.bot_handler import create_main_keyboard
            screen_path = capture_screen(hwnd, output_filename=f"completed_{int(time.time())}.jpg")
            
            # Trích xuất tên dự án ngắn gọn
            proj_name = title.split(" - Antigravity IDE")[0].strip() if " - Antigravity IDE" in title else title
            time_str = time.strftime("%H:%M:%S")

            alert_text = (
                "🎉 **ANTIGRAVITY ĐÃ HOÀN THÀNH CÂU LỆNH!** ⚡\n\n"
                f"🎯 **Dự án**: `{proj_name}`\n"
                f"🕒 **Hoàn thành lúc**: `{time_str}`\n"
                f"{duration_str}\n"
                "👉 **Kết quả đã sẵn sàng trên màn hình:**\n"
                "• Bấm **[✅ Accept All]** để duyệt tất cả thay đổi\n"
                "• Bấm **[❌ Reject All]** để từ chối\n"
                "• Bấm **[↩️ Undo Lệnh Trước]** hoặc gửi câu lệnh tiếp theo!"
            )

            # Gửi cho tất cả ID được phép
            target_ids = config.ALLOWED_USER_IDS if config.ALLOWED_USER_IDS else []
            for uid in target_ids:
                try:
                    if screen_path and Path(screen_path).exists():
                        with open(screen_path, 'rb') as photo_file:
                            self.bot.send_photo(
                                uid,
                                photo_file,
                                caption=alert_text,
                                reply_markup=create_main_keyboard(),
                                parse_mode="Markdown"
                            )
                    else:
                        self.bot.send_message(
                            uid,
                            alert_text,
                            reply_markup=create_main_keyboard(),
                            parse_mode="Markdown"
                        )
                except Exception as ex:
                    print(f"[Watcher] Lỗi gửi thông báo đến {uid}: {ex}")

        except Exception as e:
            print(f"[Watcher] Lỗi tạo thông báo: {e}")
