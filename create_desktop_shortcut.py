import os
import sys
from pathlib import Path
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def create_shortcuts():
    base_dir = Path(__file__).resolve().parent
    vbs_path = base_dir / "run_hidden.vbs"
    ico_path = base_dir / "assets" / "ai_icon.ico"

    ps_script = f"""
    $WshShell = New-Object -ComObject WScript.Shell
    $DesktopPath = $WshShell.SpecialFolders('Desktop')
    $StartupPath = $WshShell.SpecialFolders('Startup')

    # 1. Tạo trên Desktop
    $s1 = $WshShell.CreateShortcut("$DesktopPath\\Antigravity Remote AI.lnk")
    $s1.TargetPath = 'wscript.exe'
    $s1.Arguments = '"{str(vbs_path)}"'
    $s1.WorkingDirectory = '{str(base_dir)}'
    $s1.IconLocation = '{str(ico_path)}, 0'
    $s1.Description = 'Điều khiển Antigravity từ điện thoại qua Telegram'
    $s1.Save()

    # 2. Tạo trong thư mục Startup (Tự động chạy cùng Windows khi bật máy)
    $s2 = $WshShell.CreateShortcut("$StartupPath\\Antigravity Remote AI.lnk")
    $s2.TargetPath = 'wscript.exe'
    $s2.Arguments = '"{str(vbs_path)}"'
    $s2.WorkingDirectory = '{str(base_dir)}'
    $s2.IconLocation = '{str(ico_path)}, 0'
    $s2.Description = 'Tự động chạy Antigravity Remote Bot khi bật máy tính'
    $s2.Save()

    # 3. Tạo bản sao tại thư mục dự án
    $s3 = $WshShell.CreateShortcut('{str(base_dir)}\\Antigravity Remote AI.lnk')
    $s3.TargetPath = 'wscript.exe'
    $s3.Arguments = '"{str(vbs_path)}"'
    $s3.WorkingDirectory = '{str(base_dir)}'
    $s3.IconLocation = '{str(ico_path)}, 0'
    $s3.Description = 'Điều khiển Antigravity từ điện thoại qua Telegram'
    $s3.Save()
    """

    result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)

    if result.returncode == 0:
        print("🎉 ĐÃ TẠO VÀ CẬP NHẬT SHORTCUT THÀNH CÔNG:")
        print(f"   📍 Màn hình Desktop: Shortcut 'Antigravity Remote AI.lnk'")
        print(f"   🚀 Tự khởi động cùng Windows: Đã thêm vào thư mục Startup")
        print(f"   📂 Thư mục dự án: {base_dir}\\Antigravity Remote AI.lnk")
        print(f"   🎨 Icon AI: {ico_path}")
        print(f"   ⚡ Chế độ: Chạy ẩn hoàn toàn (Hidden Background - Không hiện cửa sổ đen)")
        return True
    else:
        print(f"⚠️ Lỗi tạo shortcut: {result.stderr or result.stdout}")
        return False

if __name__ == "__main__":
    create_shortcuts()
