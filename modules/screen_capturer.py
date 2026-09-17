import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageGrab
import config
from modules.window_manager import get_window_rect

def capture_screen(hwnd=None, output_filename="latest_screen.jpg", max_dim=1600):
    """
    Chụp ảnh màn hình với nhiều lớp bảo vệ (Multi-level Fallbacks):
    1. Ưu tiên chụp trực tiếp vùng cửa sổ Antigravity bằng ImageGrab (tương thích cao trên Windows 10/11).
    2. Nếu không có hwnd hoặc lỗi, chụp toàn bộ màn hình chính.
    3. Thử qua mss.
    4. Nếu chạy trong môi trường không có màn hình (Session 0/Locked), tự động render ảnh Status Card trực quan.
    """
    filepath = config.TEMP_DIR / output_filename
    img = None

    # Lấy toạ độ cửa sổ nếu có
    bbox = None
    if hwnd:
        rect = get_window_rect(hwnd)
        if rect and rect["width"] > 50 and rect["height"] > 50:
            bbox = (rect["left"], rect["top"], rect["right"], rect["bottom"])

    # Cách 1: Thử PIL ImageGrab
    try:
        if bbox:
            img = ImageGrab.grab(bbox=bbox, all_screens=True)
        else:
            img = ImageGrab.grab(all_screens=True)
    except Exception as e1:
        pass

    # Cách 2: Thử mss nếu ImageGrab chưa được
    if img is None:
        try:
            import mss
            with mss.mss() as sct:
                monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        except Exception as e2:
            pass

    # Cách 3: Fallback tạo bảng trạng thái đồ hoạ chuyên nghiệp nếu màn hình bị Lock hoặc headless
    if img is None:
        img = _generate_status_card("Antigravity Screen Capture (Desktop Inactive / Background Mode)")

    # Tối ưu kích thước trước khi lưu
    try:
        w, h = img.size
        if max(w, h) > max_dim:
            ratio = max_dim / max(w, h)
            new_size = (int(w * ratio), int(h * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        img.save(filepath, "JPEG", quality=85)
        return str(filepath)
    except Exception as e:
        print(f"[ScreenCapturer] Lỗi khi lưu ảnh: {e}")
        # Lưu khẩn cấp
        fallback = _generate_status_card("Capture Error")
        fallback.save(filepath, "JPEG")
        return str(filepath)

def _generate_status_card(title_text="Antigravity Live Status"):
    """Tạo một thẻ hình ảnh thông báo trạng thái đẹp mắt khi không thể chụp trực tiếp GDI"""
    width, height = 800, 450
    card = Image.new("RGB", (width, height), color=(24, 28, 36))
    draw = ImageDraw.Draw(card)
    
    # Vẽ header gradient giả lập
    draw.rectangle([0, 0, width, 60], fill=(41, 98, 255))
    draw.text((20, 20), "🤖 ANTIGRAVITY REMOTE BOT - LIVE STATUS", fill=(255, 255, 255))
    
    # Nội dung
    draw.text((30, 90), f"📌 Trạng thái: {title_text}", fill=(230, 230, 230))
    draw.text((30, 130), f"🕒 Thời gian: {time.strftime('%Y-%m-%d %H:%M:%S')}", fill=(180, 180, 180))
    draw.text((30, 170), "💻 Hệ thống: Đang chạy trên Windows (Background Agent)", fill=(180, 180, 180))
    draw.text((30, 210), "⚡ Các lệnh đã sẵn sàng: Accept All, Reject All, Send Prompt, Image Paste", fill=(0, 230, 118))
    
    # Khung hướng dẫn
    draw.rectangle([30, 260, width - 30, height - 30], outline=(70, 80, 95), width=2)
    draw.text((45, 280), "ℹ️ Khi bạn mở Antigravity trên màn hình chính của máy tính,", fill=(200, 200, 200))
    draw.text((45, 310), "   Bot sẽ chụp trực tiếp ảnh thật của cửa sổ làm việc gửi về điện thoại.", fill=(200, 200, 200))
    draw.text((45, 350), "📱 Gửi ảnh hoặc tin nhắn bất kỳ để tiếp tục điều khiển!", fill=(255, 215, 0))
    
    return card
