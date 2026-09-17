import os
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def create_shortcut():
    base_dir = Path(__file__).resolve().parent
    vbs_path = base_dir / "run_hidden.vbs"
    ico_path = base_dir / "assets" / "ai_icon.ico"
    
    ps_script = f"""
    $WshShell = New-Object -ComObject WScript.Shell
    $DesktopPath = $WshShell.SpecialFolders('Desktop')
    
    # 1. Tạo trên Desktop thực tế của người dùng
    $Shortcut = $WshShell.CreateShortcut("$DesktopPath\\Antigravity Remote AI.lnk")
    $Shortcut.TargetPath = 'wscript.exe'
    $Shortcut.Arguments = '"{str(vbs_path)}"'
    $Shortcut.WorkingDirectory = '{str(base_dir)}'
    $Shortcut.IconLocation = '{str(ico_path)}, 0'
    $Shortcut.Description = 'Điều khiển Antigravity từ điện thoại qua Telegram'
    $Shortcut.Save()
    Write-Host "Created Desktop Shortcut at: $DesktopPath\\Antigravity Remote AI.lnk"

    # 2. Tạo thêm bản sao tại thư mục dự án
    $LocalShortcut = "$PSScriptRoot\\Antigravity Remote AI.lnk"
    $Shortcut2 = $WshShell.CreateShortcut('{str(base_dir)}\\Antigravity Remote AI.lnk')
    $Shortcut2.TargetPath = 'wscript.exe'
    $Shortcut2.Arguments = '"{str(vbs_path)}"'
    $Shortcut2.WorkingDirectory = '{str(base_dir)}'
    $Shortcut2.IconLocation = '{str(ico_path)}, 0'
    $Shortcut2.Description = 'Điều khiển Antigravity từ điện thoại qua Telegram'
    $Shortcut2.Save()
    """

    import subprocess
    result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("🎉 ĐÃ TẠO SHORTCUT DESKTOP THÀNH CÔNG:")
        print(f"   📍 Vị trí màn hình Desktop: D:\\Desktop\\Antigravity Remote AI.lnk")
        print(f"   📍 Vị trí thư mục dự án: {base_dir}\\Antigravity Remote AI.lnk")
        print(f"   🎨 Icon AI: {ico_path}")
        print(f"   ⚡ Chế độ: Chạy ẩn hoàn toàn (Hidden Background - Không hiện cửa sổ đen)")
        return True
    else:
        print(f"⚠️ Lỗi tạo shortcut: {result.stderr or result.stdout}")
        return False

if __name__ == "__main__":
    create_shortcut()
