import sys
import time
import threading

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import config
from modules.bot_handler import setup_bot
from modules.window_manager import find_antigravity_window
from modules.overlay_widget import FloatingStatusWidget

def print_banner():
    print("=" * 60)
    print("       🤖 ANTIGRAVITY TELEGRAM REMOTE CONTROLLER 📱       ")
    print("=" * 60)
    print("  ✓ Điều khiển Antigravity từ điện thoại ở bất kỳ đâu")
    print("  ✓ Gửi Prompt tiếng Việt, gửi ảnh, chụp màn hình Live")
    print("  ✓ Duyệt lệnh Accept All / Reject All / Proceed tức thì")
    print("=" * 60)

def main():
    print_banner()

    # 1. Kiểm tra Token
    if not config.BOT_TOKEN or config.BOT_TOKEN == "your_telegram_bot_token_here":
        print("\n❌ LỖI: Chưa cấu hình TELEGRAM_BOT_TOKEN!")
        print("👉 Hướng dẫn: Mở file '.env' và dán Bot Token của bạn từ @BotFather vào.")
        return

    # 2. Kiểm tra cửa sổ Antigravity
    print(f"\n🔍 Đang kết nối Antigravity...")
    hwnd, title = find_antigravity_window(config.WINDOW_TITLE_KEYWORD)
    if hwnd:
        print(f"✅ Đã nhận diện cửa sổ: '{title}' (HWND: {hwnd})")
    else:
        print(f"ℹ️ Cửa sổ Antigravity sẽ được tự động nhận diện khi bạn gửi lệnh.")

    # 3. Khởi tạo Telegram Bot
    print("\n🚀 Đang khởi động Telegram Bot...")
    try:
        bot = setup_bot(config.BOT_TOKEN)
        bot_user = bot.get_me()
        print(f"✅ Bot đã kết nối thành công: @{bot_user.username} ({bot_user.first_name})")
        print(f"🔒 Danh sách User ID được phép: {config.ALLOWED_USER_IDS if config.ALLOWED_USER_IDS else 'Tất cả'}")
        print("\n👉 Hãy mở Telegram trên điện thoại và gửi tin nhắn /start để điều khiển!")
        print("=" * 60)

        # Chạy Telegram Polling trong luồng ngầm (Background Thread)
        def run_bot_polling():
            try:
                bot.infinity_polling(timeout=20, long_polling_timeout=20)
            except Exception as e:
                print(f"Polling error: {e}")

        bot_thread = threading.Thread(target=run_bot_polling, daemon=True)
        bot_thread.start()

        # Hiển thị Badge trạng thái nổi ở góc màn hình (Floating Widget)
        def on_stop():
            print("\n🛑 Người dùng đã tắt Bot từ giao diện góc màn hình.")
            try:
                bot.stop_polling()
            except Exception:
                pass

        try:
            widget = FloatingStatusWidget(on_stop_callback=on_stop)
            widget.start()
        except Exception as e:
            print(f"Chạy ở chế độ dòng lệnh (No GUI Widget): {e}")
            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Đã dừng Telegram Bot. Hẹn gặp lại!")
    except Exception as e:
        print(f"\n❌ Lỗi khi chạy Bot: {e}")
        time.sleep(3)

if __name__ == "__main__":
    main()
