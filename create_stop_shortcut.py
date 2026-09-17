import os
import sys
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def create_stop_shortcut():
    base_dir = Path(__file__).resolve().parent
    assets_dir = base_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    # 1. Tạo icon Stop màu đỏ neon
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Nền bát giác đỏ Stop
    padding = 15
    draw.rounded_rectangle([padding, padding, size - padding, size - padding], radius=40, fill=(220, 38, 38, 255), outline=(255, 255, 255, 255), width=8)
    
    # Biểu tượng hình vuông Stop trắng ở giữa
    sq_size = 55
    cx, cy = size // 2, size // 2
    draw.rectangle([cx - sq_size, cy - sq_size, cx + sq_size, cy + sq_size], fill=(255, 255, 255, 255))
    
    ico_path = assets_dir / "stop_icon.ico"
    img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"✅ Đã tạo Icon Stop tại: {ico_path}")

    # 2. Tạo Shortcut trên Desktop
    bat_path = base_dir / "stop_bot.bat"
    
    ps_script = f"""
    $WshShell = New-Object -ComObject WScript.Shell
    $DesktopPath = $WshShell.SpecialFolders('Desktop')
    
    # Tạo Shortcut Tắt Tool trên Desktop
    $Shortcut = $WshShell.CreateShortcut("$DesktopPath\\Tat Tool Antigravity.lnk")
    $Shortcut.TargetPath = '{str(bat_path)}'
    $Shortcut.WorkingDirectory = '{str(base_dir)}'
    $Shortcut.IconLocation = '{str(ico_path)}, 0'
    $Shortcut.Description = 'Tắt toàn bộ tiến trình Antigravity Remote Bot'
    $Shortcut.Save()
    Write-Host "Created Stop Shortcut at: $DesktopPath\\Tat Tool Antigravity.lnk"
    """

    result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
    if result.returncode == 0:
        print("🎉 Đã tạo Shortcut 'Tắt Tool Antigravity' trên màn hình Desktop!")
    else:
        print(f"⚠️ Lỗi: {result.stderr or result.stdout}")

if __name__ == "__main__":
    create_stop_shortcut()
