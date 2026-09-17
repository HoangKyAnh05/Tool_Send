# File dùng để test tính năng Accept All từ điện thoại
import datetime

def test_remote_accept():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🎯 [CV ACCEPT CLICK TEST] Nút Accept All bằng Computer Vision đã kích hoạt lúc {now}!")
    print("🔥 Click chuột trực tiếp vào nút màu xanh hoàn hảo 100%!")
    return True

if __name__ == "__main__":
    test_remote_accept()
