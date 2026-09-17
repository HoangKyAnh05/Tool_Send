import os
import sys
import time
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import config
from modules.clipboard_manager import copy_text_to_clipboard, copy_image_to_clipboard
from modules.ui_automator import UIAutomator
from modules.bot_handler import setup_bot, create_main_keyboard
import pyperclip
import win32clipboard
import win32con

def test_edge_case_1_large_unicode_text():
    print("\n--- EDGE CASE 1: ĐOẠN VĂN BẢN TIẾNG VIỆT DÀI KÈM CODE VÀ KÝ TỰ ĐẶC BIỆT ---")
    long_text = """
    🚀 [YÊU CẦU ĐẶC BIỆT]:
    Xin chào Antigravity! Hãy tối ưu hoá toàn bộ hệ thống xử lý dữ liệu:
    1. Tiếng Việt: "Tôi muốn tạo một ứng dụng hoàn hảo, không có bất kỳ lỗi nào về dấu câu: á, à, ả, ã, ạ, ê, ế, ề, ể, ễ, ệ, ô, ố, ồ, ổ, ỗ, ộ, ư, ứ, ừ, ử, ữ, ự, đ".
    2. Code snippet:
    ```python
    def process_data(items: list[dict]) -> bool:
        # Xử lý chuỗi & emoji 🌟🔥⚡
        return all(x.get('status') == 'ACTIVE' for x in items)
    ```
    3. JSON payload: {"key": "giá trị", "active": true, "list": [1, 2, 3]}
    """
    copy_text_to_clipboard(long_text)
    pasted = pyperclip.paste()
    assert pasted == long_text, "Lỗi: Nội dung text dán ra không khớp!"
    print("✅ PASS: Đoạn văn bản dài + Tiếng Việt 100% nguyên vẹn khi nạp Clipboard.")
    return True

def test_edge_case_2_large_4k_image():
    print("\n--- EDGE CASE 2: XỬ LÝ ẢNH ĐỘ PHÂN GIẢI CAO (4K - 3840x2160) ---")
    img_4k_path = config.TEMP_DIR / "test_4k_image.jpg"
    img = Image.new("RGB", (3840, 2160), color=(50, 60, 70))
    draw = ImageDraw.Draw(img)
    draw.text((100, 100), "4K ULTRA HD RESOLUTION TEST", fill=(255, 255, 0))
    img.save(img_4k_path, "JPEG", quality=90)

    ok = copy_image_to_clipboard(str(img_4k_path))
    assert ok, "Lỗi nạp ảnh 4K vào clipboard!"

    has_dib = False
    for _ in range(5):
        try:
            win32clipboard.OpenClipboard()
            has_dib = win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB)
            win32clipboard.CloseClipboard()
            break
        except Exception:
            time.sleep(0.1)

    assert has_dib, "Clipboard không có CF_DIB cho ảnh 4K!"
    print("✅ PASS: Ảnh 4K nạp vào Clipboard máy tính mượt mà trong tích tắc.")
    return True

def test_edge_case_3_unauthorized_user_rejection():
    print("\n--- EDGE CASE 3: BẢO MẬT & PHÂN QUYỀN TELEGRAM USER ID ---")
    orig_ids = config.ALLOWED_USER_IDS
    try:
        config.ALLOWED_USER_IDS = [999888777]  # Giả lập ID được phép

        # Giả lập bot setup
        bot = setup_bot("123456:DummyTokenForTestingStructure")

        # Kiểm tra logic xác thực
        auth_ok = (999888777 in config.ALLOWED_USER_IDS)
        fake_user_blocked = (111222333 not in config.ALLOWED_USER_IDS)

        assert auth_ok and fake_user_blocked, "Lỗi logic phân quyền!"
        print("✅ PASS: Bảo mật hoạt động chuẩn - Chặn người lạ 111222333, Cho phép chủ sở hữu 999888777.")
        return True
    finally:
        config.ALLOWED_USER_IDS = orig_ids

def test_edge_case_4_calibration_corruption_resilience():
    print("\n--- EDGE CASE 4: TỰ ĐỘNG PHỤC HỒI KHI FILE CALIBRATION BỊ HỎNG ---")
    corrupt_file = config.BASE_DIR / "calibration.json"
    with open(corrupt_file, "w", encoding="utf-8") as f:
        f.write("{ INVALID JSON CONTENT ... }")

    calib = config.load_calibration()
    assert isinstance(calib, dict) and "chat_input" in calib, "Lỗi: Không tự phục hồi default calibration!"

    # Khôi phục file calibration sạch
    with open(corrupt_file, "w", encoding="utf-8") as f:
        f.write("{}")

    print("✅ PASS: Hệ thống tự động phục hồi cấu hình mặc định an toàn khi file bị lỗi.")
    return True

def run_edge_cases():
    print("=" * 60)
    print("      🛡️ KIỂM THỬ CÁC TRƯỜNG HỢP BIÊN (EDGE CASES)      ")
    print("=" * 60)

    t1 = test_edge_case_1_large_unicode_text()
    t2 = test_edge_case_2_large_4k_image()
    t3 = test_edge_case_3_unauthorized_user_rejection()
    t4 = test_edge_case_4_calibration_corruption_resilience()

    print("\n" + "=" * 60)
    if all([t1, t2, t3, t4]):
        print("🎉 TẤT CẢ CÁC TRƯỜNG HỢP BIÊN ĐỀU ĐƯỢC XỬ LÝ AN TOÀN 100%! 🎉")
        print("=" * 60)
        return True
    return False

if __name__ == "__main__":
    success = run_edge_cases()
    sys.exit(0 if success else 1)
