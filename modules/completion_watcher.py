import os
import glob
import json
import time
import threading
from pathlib import Path
from PIL import Image

import config
from modules.window_manager import find_antigravity_window, get_all_antigravity_windows, get_window_rect
from modules.screen_capturer import capture_screen

class TaskCompletionWatcher:
    """
    Luồng giám sát trạng thái Antigravity IDE ngầm (Background Thread):
    1. Giám sát chính xác 100% qua file transcript logs của Antigravity Engine:
       - Theo dõi luồng xử lý câu lệnh, các bước Tool Call và phản hồi cuối cùng.
       - Chỉ kích hoạt thông báo khi Antigravity đã hoàn thành TOÀN BỘ câu lệnh (PLANNER_RESPONSE DONE, không còn pending tool call).
    2. Kết hợp Computer Vision quét nút 'Accept All' trên màn hình thực tế.
    3. Tự động gửi thông báo + ảnh màn hình Live Screen về Telegram.
    """
    def __init__(self, bot, automator):
        self.bot = bot
        self.automator = automator
        self.running = False
        self.thread = None

        self.is_task_active = False
        self.task_start_time = 0
        self.task_had_activity = False
        self.last_notified_time = 0
        self.last_notified_step = None
        self.last_seen_accept_button = False
        self.monitored_transcript_path = None
        self.initial_line_count = 0

    def _get_brain_dir(self) -> Path:
        """Đường dẫn thư mục brain lưu log Antigravity"""
        return Path.home() / ".gemini" / "antigravity-ide" / "brain"

    def _get_latest_transcripts(self, limit=5):
        """Lấy danh sách các file transcript.jsonl gần nhất"""
        brain_dir = self._get_brain_dir()
        if not brain_dir.exists():
            return []
        pattern = str(brain_dir / "*" / ".system_generated" / "logs" / "transcript.jsonl")
        files = glob.glob(pattern)
        if not files:
            return []
        files.sort(key=os.path.getmtime, reverse=True)
        return files[:limit]

    def _check_transcript_state(self, file_path):
        """
        Đọc và phân tích trạng thái bước cuối cùng trong file transcript.jsonl.
        Trả về (is_done, reason, step_index, total_lines, mtime)
        """
        if not file_path or not os.path.exists(file_path):
            return False, "File không tồn tại", 0, 0, 0
        try:
            mtime = os.path.getmtime(file_path)
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = [l.strip() for l in f if l.strip()]
            if not lines:
                return False, "File rỗng", 0, 0, mtime

            last_obj = json.loads(lines[-1])
            step_index = last_obj.get("step_index", 0)
            msg_type = last_obj.get("type", "")
            status = last_obj.get("status", "")
            tool_calls = last_obj.get("tool_calls", [])

            # Task hoàn thành khi:
            # - Bước cuối cùng là PLANNER_RESPONSE
            # - Status là DONE
            # - KHÔNG có pending tool_calls (đã hoàn thành tất cả tool execution và trả về câu trả lời cuối cùng)
            if msg_type == "PLANNER_RESPONSE" and not tool_calls and status == "DONE":
                return True, "Planner response done", step_index, len(lines), mtime

            return False, f"In progress ({msg_type}, status={status}, tool_calls={bool(tool_calls)})", step_index, len(lines), mtime
        except Exception as e:
            return False, str(e), 0, 0, 0

    def mark_task_started(self, project_title=""):
        """Được gọi khi người dùng vừa gửi câu lệnh từ điện thoại"""
        self.is_task_active = True
        self.task_start_time = time.time()
        self.task_had_activity = False
        self.last_seen_accept_button = False

        # Xác định file transcript mới nhất tại thời điểm bắt đầu
        latest_files = self._get_latest_transcripts(limit=1)
        if latest_files:
            self.monitored_transcript_path = latest_files[0]
            _, _, _, line_count, _ = self._check_transcript_state(self.monitored_transcript_path)
            self.initial_line_count = line_count
        else:
            self.monitored_transcript_path = None
            self.initial_line_count = 0

    def mark_task_stopped(self):
        """Được gọi khi người dùng dừng task"""
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
        time.sleep(1.5)
        while self.running:
            try:
                time.sleep(1.0)
                now = time.time()

                # Không gửi thông báo dồn dập (cách nhau tối thiểu 5s)
                if now - self.last_notified_time < 5:
                    continue

                hwnd, title = find_antigravity_window()
                if not hwnd:
                    continue

                # 1. Quét nút Accept All bằng Computer Vision nếu có cửa sổ
                has_accept_btn = False
                win_rect = get_window_rect(hwnd)
                if win_rect:
                    temp_scan = capture_screen(hwnd, output_filename="cv_watch_scan.jpg", max_dim=2000)
                    if Path(temp_scan).exists():
                        coords = self.automator._detect_button_coords_cv(temp_scan, win_rect, "accept")
                        if coords is not None:
                            has_accept_btn = True

                # 2. Xử lý logic khi task được đánh dấu đang chạy (Active Task từ Telegram Prompt)
                if self.is_task_active:
                    # Kiểm tra xem có file transcript nào mới hơn không
                    latest_files = self._get_latest_transcripts(limit=3)
                    target_file = self.monitored_transcript_path
                    if latest_files:
                        # Nếu file gần nhất mới hơn và được cập nhật sau khi bắt đầu task
                        if os.path.getmtime(latest_files[0]) >= (self.task_start_time - 1.0):
                            target_file = latest_files[0]

                    if target_file and os.path.exists(target_file):
                        is_done, reason, step_idx, total_lines, mtime = self._check_transcript_state(target_file)

                        # Xác nhận Antigravity đã bắt đầu ghi nhận và xử lý lệnh
                        if total_lines > self.initial_line_count or mtime >= self.task_start_time:
                            self.task_had_activity = True

                        # Hoàn thành câu lệnh khi:
                        # - File transcript đã ghi nhận hoạt động (task_had_activity)
                        # - Bước cuối cùng là PLANNER_RESPONSE DONE và không có tool call (is_done)
                        # - File transcript đã ổn định không có ghi mới trong >= 1.2 giây
                        # - Đã trôi qua ít nhất 2 giây từ khi bắt đầu
                        if self.task_had_activity and is_done:
                            if (now - mtime >= 1.2) and (now - self.task_start_time >= 2.0):
                                dur = int(now - self.task_start_time)
                                duration_str = f"⏱️ Thời gian xử lý: ~{dur}s\n" if dur > 0 else ""
                                self.is_task_active = False
                                self.last_notified_time = now
                                self.last_notified_step = (target_file, step_idx)
                                self.last_seen_accept_button = has_accept_btn
                                self._send_completion_alert(hwnd, title, duration_str)
                                continue

                    # Fallback CV: Nếu xuất hiện nút Accept All (tạo diffs) và task đã chạy ít nhất 3s
                    if has_accept_btn and (now - self.task_start_time >= 3.0):
                        dur = int(now - self.task_start_time)
                        duration_str = f"⏱️ Thời gian xử lý: ~{dur}s\n" if dur > 0 else ""
                        self.is_task_active = False
                        self.last_notified_time = now
                        self.last_seen_accept_button = True
                        self._send_completion_alert(hwnd, title, duration_str)
                        continue

                # 3. Xử lý trường hợp người dùng gõ lệnh trực tiếp trên máy tính (External Prompt)
                elif not self.is_task_active:
                    # A. Phát hiện qua nút Accept All mới xuất hiện
                    if has_accept_btn and not self.last_seen_accept_button:
                        self.last_seen_accept_button = True
                        self.last_notified_time = now
                        self._send_completion_alert(hwnd, title, "")
                        continue

                    self.last_seen_accept_button = has_accept_btn

                    # B. Phát hiện qua file transcript mới hoàn thành gần đây (< 8s)
                    latest_files = self._get_latest_transcripts(limit=1)
                    if latest_files:
                        l_file = latest_files[0]
                        is_done, reason, step_idx, total_lines, mtime = self._check_transcript_state(l_file)
                        step_key = (l_file, step_idx)

                        if is_done and (now - mtime <= 8.0) and (now - mtime >= 1.5):
                            if step_key != self.last_notified_step:
                                self.last_notified_step = step_key
                                self.last_notified_time = now
                                self._send_completion_alert(hwnd, title, "")
                                continue

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
                "• Gửi tin nhắn tiếp theo để ra lệnh mới!"
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
