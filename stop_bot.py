import os
import sys
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print("=" * 60)
print("       🛑 DỪNG TIẾN TRÌNH ANTIGRAVITY REMOTE BOT")
print("=" * 60)
print("Đang tắt bot và đóng bảng trạng thái...")

try:
    # Dùng WMIC / PowerShell an toàn
    cmd = (
        'powershell -NoProfile -Command "'
        "Get-CimInstance Win32_Process | "
        "Where-Object { $_.CommandLine -like '*main.py*' -or $_.CommandLine -like '*run_hidden.vbs*' } | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }\""
    )
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception as e:
    print(f"Lỗi: {e}")

print("\n✅ ĐÃ TẮT TOOL VÀ DỪNG TOÀN BỘ TIẾN TRÌNH THÀNH CÔNG!\n")
