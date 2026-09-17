import time
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
WINSTA_ALL_ACCESS = 0x37F
DESKTOP_ALL_ACCESS = 0x1FF

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
user32.EnumWindows.restype = wintypes.BOOL

class RECT(ctypes.Structure):
    _fields_ = [
        ('left', ctypes.c_long),
        ('top', ctypes.c_long),
        ('right', ctypes.c_long),
        ('bottom', ctypes.c_long)
    ]

# Biến toàn cục lưu cửa sổ mục tiêu đang được chọn
ACTIVE_TARGET_HWND = None
ACTIVE_TARGET_TITLE = "Tự động (Mặc định)"

# Danh sách từ khóa loại trừ (các app âm thanh/tiện ích/overlay không phải dự án Antigravity IDE)
EXCLUDED_KEYWORDS = [
    "sound tool",
    "remote controller",
    "remote ai",
    "status badge",
    "overlay",
    "task switching",
    "program manager",
    "gdi+",
    "textinputhost",
    "popup host",
    "hardwaremonitor"
]

def ensure_desktop_attached():
    """
    Đảm bảo thread hiện tại được gắn kết với Interactive Desktop (winsta0\\default).
    Giúp phát hiện cửa sổ 100% ổn định trong mọi môi trường (terminal, shortcut, background thread).
    """
    try:
        hwinsta = user32.OpenWindowStationW("winsta0", False, WINSTA_ALL_ACCESS)
        if hwinsta:
            user32.SetProcessWindowStation(hwinsta)
            hdesk = user32.OpenDesktopW("default", 0, False, DESKTOP_ALL_ACCESS)
            if hdesk:
                user32.SetThreadDesktop(hdesk)
    except Exception:
        pass

def get_all_windows():
    """Lấy danh sách tất cả các cửa sổ đang hiển thị trên Desktop"""
    ensure_desktop_attached()
    windows = []

    def enum_cb(hwnd, lparam):
        try:
            if not user32.IsWindow(hwnd) or not user32.IsWindowVisible(hwnd):
                return True

            length = user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return True

            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value.strip()

            rect = RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            w = rect.right - rect.left
            h = rect.bottom - rect.top

            # Lấy Process Name & Path
            pname = ""
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value:
                h_proc = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
                if h_proc:
                    pbuff = ctypes.create_unicode_buffer(512)
                    size = wintypes.DWORD(512)
                    if kernel32.QueryFullProcessImageNameW(h_proc, 0, pbuff, ctypes.byref(size)):
                        pname = pbuff.value
                    kernel32.CloseHandle(h_proc)

            # Chỉ lấy các cửa sổ có kích thước thực tế
            if w > 100 and h > 100 and title:
                windows.append({
                    "hwnd": hwnd,
                    "pid": pid.value,
                    "title": title,
                    "process": pname,
                    "width": w,
                    "height": h
                })
        except Exception:
            pass
        return True

    cb = WNDENUMPROC(enum_cb)
    user32.EnumWindows(cb, 0)
    return windows

def get_all_antigravity_windows():
    """
    Lấy danh sách TẤT CẢ các cửa sổ DỰ ÁN Antigravity IDE thực tế đang mở.
    Loại trừ tuyệt đối các cửa sổ Sound Tool, Remote Widget hay cửa sổ tiện ích.
    """
    global ACTIVE_TARGET_HWND, ACTIVE_TARGET_TITLE
    windows = get_all_windows()
    anti_windows = []
    seen_hwnds = set()

    for win in windows:
        hwnd = win["hwnd"]
        if hwnd in seen_hwnds:
            continue

        raw_title = win["title"]
        pname = win["process"].lower()
        t_lower = raw_title.lower()

        # 1. Kiểm tra danh sách đen loại trừ
        if any(ex in t_lower for ex in EXCLUDED_KEYWORDS):
            continue

        # 2. Nhận diện cửa sổ Antigravity IDE thực thụ
        is_anti_proc = "antigravity ide" in pname or pname.endswith("antigravity.exe") or pname.endswith("antigravity ide.exe")
        is_anti_title = "- antigravity ide" in t_lower or "antigravity ide" in t_lower

        # Kích thước phải đủ lớn để là cửa sổ IDE (tránh tooltip hoặc dialog nhỏ)
        is_valid_size = win["width"] >= 400 and win["height"] >= 300

        if (is_anti_proc or is_anti_title) and is_valid_size:
            seen_hwnds.add(hwnd)

            # 3. Trích xuất tên Dự án (Project Name) chuẩn xác
            project_name = ""
            active_file = ""

            if " - Antigravity IDE" in raw_title:
                parts = raw_title.split(" - Antigravity IDE")
                project_name = parts[0].strip()
                if len(parts) > 1 and parts[1].strip():
                    active_file = parts[1].strip().lstrip("- ").strip()
            elif " - " in raw_title:
                parts = raw_title.split(" - ")
                project_name = parts[0].strip()
                if len(parts) > 1:
                    active_file = parts[-1].strip()
            else:
                project_name = raw_title

            if not project_name:
                project_name = "Antigravity Project"

            # Rút gọn tên hiển thị trên nút bấm Telegram (tối đa 30 ký tự)
            display_name = project_name
            if len(display_name) > 28:
                display_name = display_name[:25] + "..."

            is_active = (hwnd == ACTIVE_TARGET_HWND)
            anti_windows.append({
                "hwnd": hwnd,
                "project_name": project_name,
                "display_name": display_name,
                "active_file": active_file,
                "full_title": raw_title,
                "is_active": is_active
            })

    # Nếu chưa có cửa sổ nào được chọn (hoặc cửa sổ cũ đã bị đóng)
    if anti_windows:
        active_exists = any(w["hwnd"] == ACTIVE_TARGET_HWND for w in anti_windows)
        if not active_exists:
            ACTIVE_TARGET_HWND = anti_windows[0]["hwnd"]
            ACTIVE_TARGET_TITLE = anti_windows[0]["full_title"]
            anti_windows[0]["is_active"] = True

    return anti_windows

def set_active_target_window(hwnd: int, title: str = ""):
    """Chuyển đổi cửa sổ Antigravity mục tiêu"""
    global ACTIVE_TARGET_HWND, ACTIVE_TARGET_TITLE
    ACTIVE_TARGET_HWND = hwnd
    ACTIVE_TARGET_TITLE = title or f"Window {hwnd}"
    focus_window(hwnd)
    return True

def find_antigravity_window(keyword="Antigravity"):
    """
    Tìm cửa sổ mục tiêu hiện tại:
    - Nếu đã chọn và còn tồn tại: trả về cửa sổ đó
    - Nếu chưa: quét danh sách và tự động gán cửa sổ đầu tiên
    """
    global ACTIVE_TARGET_HWND, ACTIVE_TARGET_TITLE

    # 1. Kiểm tra cửa sổ đã chọn có còn hợp lệ không
    if ACTIVE_TARGET_HWND and user32.IsWindow(ACTIVE_TARGET_HWND):
        tlen = user32.GetWindowTextLengthW(ACTIVE_TARGET_HWND)
        if tlen > 0:
            buff = ctypes.create_unicode_buffer(tlen + 1)
            user32.GetWindowTextW(ACTIVE_TARGET_HWND, buff, tlen + 1)
            ACTIVE_TARGET_TITLE = buff.value.strip()
        return ACTIVE_TARGET_HWND, ACTIVE_TARGET_TITLE

    # 2. Quét danh sách các dự án Antigravity IDE thực tế
    anti_list = get_all_antigravity_windows()
    if anti_list:
        ACTIVE_TARGET_HWND = anti_list[0]["hwnd"]
        ACTIVE_TARGET_TITLE = anti_list[0]["full_title"]
        return ACTIVE_TARGET_HWND, ACTIVE_TARGET_TITLE

    # 3. Fallback lấy cửa sổ Foreground
    fg_hwnd = user32.GetForegroundWindow()
    if fg_hwnd and user32.IsWindow(fg_hwnd):
        tlen = user32.GetWindowTextLengthW(fg_hwnd)
        if tlen > 0:
            buff = ctypes.create_unicode_buffer(tlen + 1)
            user32.GetWindowTextW(fg_hwnd, buff, tlen + 1)
            return fg_hwnd, buff.value.strip()

    return None, "Chưa tìm thấy Antigravity IDE"

def focus_window(hwnd):
    """Kích hoạt và đưa cửa sổ lên trên cùng (Foreground) tuyệt đối"""
    if not hwnd or not user32.IsWindow(hwnd):
        return False

    try:
        SW_RESTORE = 9
        SW_SHOW = 5

        # Đính kèm thread để đảm bảo quyền SetForegroundWindow
        current_thread_id = kernel32.GetCurrentThreadId()
        window_thread_id = user32.GetWindowThreadProcessId(hwnd, None)
        if current_thread_id != window_thread_id:
            user32.AttachThreadInput(current_thread_id, window_thread_id, True)

        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, SW_RESTORE)
        else:
            user32.ShowWindow(hwnd, SW_SHOW)

        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
        user32.SetFocus(hwnd)

        if current_thread_id != window_thread_id:
            user32.AttachThreadInput(current_thread_id, window_thread_id, False)

        time.sleep(0.15)
        return True
    except Exception as e:
        try:
            user32.SetForegroundWindow(hwnd)
            return True
        except Exception:
            return False

def get_window_rect(hwnd):
    """Lấy toạ độ hình chữ nhật của cửa sổ"""
    if not hwnd or not user32.IsWindow(hwnd):
        return None
    try:
        rect = RECT()
        if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return {
                "left": rect.left,
                "top": rect.top,
                "right": rect.right,
                "bottom": rect.bottom,
                "width": rect.right - rect.left,
                "height": rect.bottom - rect.top
            }
    except Exception as e:
        print(f"[WindowManager] Lỗi lấy kích thước cửa sổ: {e}")
    return None
