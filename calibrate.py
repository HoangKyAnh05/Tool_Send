import sys
import time
import pyautogui

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import config
from modules.window_manager import find_antigravity_window, get_all_windows, get_window_rect
from modules.screen_capturer import capture_screen

def print_menu():
    print("\n" + "=" * 50)
    print("      🛠️ CÔNG CỤ HIỆU CHỈNH & KIỂM TRA (CALIBRATE)      ")
    print("=" * 50)
    print("1. 🔍 Kiểm tra tìm kiếm cửa sổ Antigravity")
    print("2. 📸 Chụp thử ảnh màn hình Antigravity")
    print("3. 🎯 Lấy toạ độ chuột để lưu vị trí nút bấm (Accept / Chat Input...)")
    print("4. 📋 Xem cấu hình toạ độ hiện tại (calibration.json)")
    print("0. 🚪 Thoát")
    print("=" * 50)

def test_find_window():
    print(f"\n🔍 Đang tìm cửa sổ với từ khóa: '{config.WINDOW_TITLE_KEYWORD}'...")
    hwnd, title = find_antigravity_window(config.WINDOW_TITLE_KEYWORD)
    if hwnd:
        rect = get_window_rect(hwnd)
        print(f"✅ TÌM THẤY CỬA SỔ:")
        print(f"   • Tiêu đề: {title}")
        print(f"   • HWND: {hwnd}")
        print(f"   • Vị trí: Left={rect['left']}, Top={rect['top']}, Width={rect['width']}, Height={rect['height']}")
    else:
        print("❌ Không tìm thấy cửa sổ nào chứa từ khóa.")
        print("\n📋 Danh sách các cửa sổ đang mở trên máy tính:")
        for h, t in get_all_windows():
            print(f"   - [{h}] {t}")

def test_screenshot():
    hwnd, _ = find_antigravity_window(config.WINDOW_TITLE_KEYWORD)
    path = capture_screen(hwnd, output_filename="test_calibration_screen.jpg")
    print(f"✅ Đã chụp ảnh màn hình thành công! Lưu tại: {path}")

def record_coordinates():
    calib = config.load_calibration()
    print("\n🎯 Chọn vị trí bạn muốn lưu toạ độ:")
    print("1. Ô nhập Chat (chat_input)")
    print("2. Nút Accept All (accept_button)")
    print("3. Nút Reject All (reject_button)")
    print("4. Nút Proceed (proceed_button)")
    print("5. Nút Stop (stop_button)")
    
    choice = input("👉 Nhập số (1-5): ").strip()
    key_map = {
        "1": "chat_input",
        "2": "accept_button",
        "3": "reject_button",
        "4": "proceed_button",
        "5": "stop_button"
    }
    
    if choice not in key_map:
        print("❌ Lựa chọn không hợp lệ.")
        return
        
    target_key = key_map[choice]
    print(f"\n⏳ Chuẩn bị: Hãy di chuyển chuột đến vị trí '{target_key}' trên màn hình trong 3 giây...")
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
        
    pos = pyautogui.position()
    calib[target_key] = [pos.x, pos.y]
    config.save_calibration(calib)
    print(f"✅ ĐÃ LƯU TOẠ ĐỘ: {target_key} -> ({pos.x}, {pos.y}) vào calibration.json")

def view_calibration():
    calib = config.load_calibration()
    print("\n📋 Dữ liệu toạ độ hiện tại:")
    for k, v in calib.items():
        print(f"   • {k}: {v}")

def main():
    while True:
        print_menu()
        choice = input("👉 Chọn chức năng (0-4): ").strip()
        if choice == "1":
            test_find_window()
        elif choice == "2":
            test_screenshot()
        elif choice == "3":
            record_coordinates()
        elif choice == "4":
            view_calibration()
        elif choice == "0":
            break
        else:
            print("❌ Vui lòng chọn từ 0 đến 4.")

if __name__ == "__main__":
    main()
