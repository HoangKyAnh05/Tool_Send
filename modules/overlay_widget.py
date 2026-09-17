import sys
import os
import threading
import tkinter as tk

class FloatingStatusWidget:
    def __init__(self, on_stop_callback=None):
        self.on_stop_callback = on_stop_callback
        self.root = None
        self._drag_data = {"x": 0, "y": 0}

    def start(self):
        """Khởi chạy giao diện widget nổi góc màn hình"""
        self.root = tk.Tk()
        self.root.title("Antigravity Remote Controller")
        
        # Cửa sổ không viền, luôn nổi trên cùng
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-alpha", 0.95)

        # Màu sắc chủ đạo (Cyberpunk Dark Mode)
        self.bg_color = "#111827"        # Dark slate
        self.border_color = "#00e5ff"    # Cyan Neon
        self.text_color = "#f9fafb"      # Trắng
        self.green_color = "#10b981"     # Emerald Green
        self.red_color = "#ef4444"       # Red Stop
        self.red_hover = "#dc2626"

        # Kích thước rộng rãi chống tràn viền trên màn hình độ phân giải cao
        self.w = 320
        self.h = 100
        
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        pos_x = screen_w - self.w - 30
        pos_y = screen_h - self.h - 70
        
        self.root.geometry(f"{self.w}x{self.h}+{pos_x}+{pos_y}")

        # Khung viền chính
        self.main_frame = tk.Frame(
            self.root,
            bg=self.bg_color,
            highlightbackground=self.border_color,
            highlightthickness=2,
            cursor="fleur"
        )
        self.main_frame.pack(fill="both", expand=True)

        # Kéo thả di chuyển widget
        self.main_frame.bind("<Button-1>", self._start_move)
        self.main_frame.bind("<B1-Motion>", self._do_move)

        self._build_ui()
        self.root.mainloop()

    def _build_ui(self):
        # 1. Hàng Tiêu Đề
        top_row = tk.Frame(self.main_frame, bg=self.bg_color)
        top_row.pack(fill="x", padx=12, pady=(8, 2))
        top_row.bind("<Button-1>", self._start_move)
        top_row.bind("<B1-Motion>", self._do_move)

        title_lbl = tk.Label(
            top_row,
            text="🤖 Antigravity Remote AI",
            font=("Segoe UI", 10, "bold"),
            fg=self.border_color,
            bg=self.bg_color
        )
        title_lbl.pack(side="left")
        title_lbl.bind("<Button-1>", self._start_move)
        title_lbl.bind("<B1-Motion>", self._do_move)

        # Nút [✕] đóng nhỏ ở góc trên
        btn_x = tk.Label(
            top_row,
            text=" ✕ ",
            font=("Segoe UI", 11, "bold"),
            fg="#9ca3af",
            bg=self.bg_color,
            cursor="hand2"
        )
        btn_x.pack(side="right")
        btn_x.bind("<Enter>", lambda e: btn_x.config(fg=self.red_color))
        btn_x.bind("<Leave>", lambda e: btn_x.config(fg="#9ca3af"))
        btn_x.bind("<Button-1>", lambda e: self.stop_app())

        # 2. Hàng Trạng Thái & Nút Tắt Tool Nổi Bật
        bottom_row = tk.Frame(self.main_frame, bg=self.bg_color)
        bottom_row.pack(fill="x", padx=12, pady=(4, 8))
        bottom_row.bind("<Button-1>", self._start_move)
        bottom_row.bind("<B1-Motion>", self._do_move)

        # Cụm trạng thái bên trái
        status_box = tk.Frame(bottom_row, bg=self.bg_color)
        status_box.pack(side="left", fill="y")
        status_box.bind("<Button-1>", self._start_move)
        status_box.bind("<B1-Motion>", self._do_move)

        status_lbl = tk.Label(
            status_box,
            text="● ĐANG BẬT (24/7)",
            font=("Segoe UI", 9, "bold"),
            fg=self.green_color,
            bg=self.bg_color
        )
        status_lbl.pack(anchor="w")
        status_lbl.bind("<Button-1>", self._start_move)
        status_lbl.bind("<B1-Motion>", self._do_move)

        bot_name_lbl = tk.Label(
            status_box,
            text="📱 @Tool_Send_bot",
            font=("Segoe UI", 8),
            fg="#9ca3af",
            bg=self.bg_color
        )
        bot_name_lbl.pack(anchor="w")
        bot_name_lbl.bind("<Button-1>", self._start_move)
        bot_name_lbl.bind("<B1-Motion>", self._do_move)

        # 3. NÚT [🛑 TẮT TOOL] TO RÕ RÀNG Ở BÊN PHẢI
        btn_stop = tk.Button(
            bottom_row,
            text="🛑 TẮT TOOL",
            font=("Segoe UI", 9, "bold"),
            fg="#ffffff",
            bg=self.red_color,
            activebackground=self.red_hover,
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.stop_app
        )
        btn_stop.pack(side="right", padx=(8, 0))

    def _start_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _do_move(self, event):
        deltax = event.x - self._drag_data["x"]
        deltay = event.y - self._drag_data["y"]
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def stop_app(self):
        """Dừng toàn bộ hệ thống ngay lập tức khi người dùng bấm nút"""
        try:
            if self.on_stop_callback:
                self.on_stop_callback()
        except Exception:
            pass

        try:
            if self.root:
                self.root.destroy()
        except Exception:
            pass

        # Dừng triệt để tiến trình python
        os._exit(0)
