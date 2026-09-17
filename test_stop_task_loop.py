"""
🛑 FILE TEST DỪNG TÁC VỤ (STOP TASK) TỪ ĐIỆN THOẠI
"""
import time

def long_running_task():
    print("🚀 Đang chạy tác vụ kiểm thử...")
    print("👉 Hãy mở Telegram và bấm nút [🛑 Stop Task] để dừng ngay lập tức!")
    for i in range(1, 100):
        print(f"⏳ Tác vụ đang xử lý bước {i}/100...")
        time.sleep(1)

if __name__ == "__main__":
    long_running_task()
