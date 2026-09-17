import io
import ctypes
from PIL import Image
import pyperclip

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Thiết lập kiểu dữ liệu chuẩn 64-bit cho Windows API
kernel32.GlobalAlloc.restype = ctypes.c_void_p
kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]

def copy_text_to_clipboard(text: str):
    """Nạp văn bản (hỗ trợ đầy đủ Unicode tiếng Việt) vào Windows Clipboard"""
    pyperclip.copy(text)

def copy_image_to_clipboard(image_path: str):
    """
    Nạp file ảnh từ đường dẫn vào Windows Clipboard dưới định dạng CF_DIB (Bitmap tiêu chuẩn).
    Sau khi nạp, bất kỳ ứng dụng nào (như Antigravity / VS Code) đều có thể nhận bằng lệnh Ctrl + V.
    """
    try:
        image = Image.open(image_path)
        # Chuyển đổi sang RGB nếu đang ở định dạng khác (RGBA / PNG...)
        if image.mode != "RGB":
            image = image.convert("RGB")

        output = io.BytesIO()
        image.save(output, "BMP")
        data = output.getvalue()[14:]  # Cắt bỏ 14 bytes BMP File Header để lấy DIB
        output.close()

        CF_DIB = 8
        GMEM_MOVEABLE = 0x0002

        h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not h_mem:
            return False

        p_mem = kernel32.GlobalLock(h_mem)
        if not p_mem:
            return False

        ctypes.memmove(p_mem, data, len(data))
        kernel32.GlobalUnlock(h_mem)

        if user32.OpenClipboard(None):
            user32.EmptyClipboard()
            user32.SetClipboardData(CF_DIB, h_mem)
            user32.CloseClipboard()
            return True
        return False
    except Exception as e:
        print(f"[ClipboardManager] Lỗi nạp ảnh vào Clipboard: {e}")
        try:
            user32.CloseClipboard()
        except Exception:
            pass
        return False
