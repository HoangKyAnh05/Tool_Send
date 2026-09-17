"""
🛑 FILE KIỂM THỬ TÍNH NĂNG STOP TASK (DỪNG TÁC VỤ TỪ XA)
"""
import time
import sys

def main():
    print("=" * 60)
    print("🚀 TIẾN TRÌNH TEST STOP TASK ĐANG CHẠY...")
    print("👉 HÃY MỞ TELEGRAM VÀ BẤM NÚT [🛑 Stop Task] ĐỂ DỪNG NGAY!")
    print("=" * 60)

    try:
        step = 1
        while True:
            print(f"⏳ [Đang xử lý...] Bước thứ {step} (Đang chờ lệnh dừng từ Telegram...)")
            sys.stdout.flush()
            time.sleep(1)
            step += 1
    except KeyboardInterrupt:
        print("\n\n🛑 ĐÃ NHẬN TÍN HIỆU STOP TASK TỪ TELEGRAM THÀNH CÔNG! TIẾN TRÌNH ĐÃ DỪNG! ✅")

if __name__ == "__main__":
    main()
