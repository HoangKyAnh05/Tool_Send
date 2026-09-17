import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def create_ai_icon():
    """Tạo icon AI chuyên nghiệp với các kích thước đa độ phân giải (.ico)"""
    assets_dir = Path(__file__).parent / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    size = 256
    # Tạo nền vòng tròn gradient bo góc trong suốt
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 1. Vẽ nền tròn bóng bẩy (Modern Dark Neon AI theme)
    padding = 10
    draw.ellipse([padding, padding, size - padding, size - padding], fill=(18, 22, 36, 255), outline=(0, 229, 255, 255), width=6)
    
    # 2. Vẽ vòng sáng nội vi (Glow effect)
    draw.ellipse([padding + 12, padding + 12, size - padding - 12, size - padding - 12], outline=(99, 102, 241, 180), width=3)
    
    # 3. Vẽ biểu tượng AI Brain / Chip Circuit / Sparkle ở trung tâm
    cx, cy = size // 2, size // 2
    
    # Vẽ chip vi xử lý AI trung tâm
    chip_size = 50
    draw.rounded_rectangle(
        [cx - chip_size, cy - chip_size, cx + chip_size, cy + chip_size],
        radius=14,
        fill=(30, 41, 59, 255),
        outline=(0, 229, 255, 255),
        width=4
    )
    
    # Vẽ các chân chip (pins)
    for offset in [-25, 0, 25]:
        # Top & Bottom pins
        draw.line([cx + offset, cy - chip_size, cx + offset, cy - chip_size - 18], fill=(0, 229, 255, 255), width=4)
        draw.line([cx + offset, cy + chip_size, cx + offset, cy + chip_size + 18], fill=(0, 229, 255, 255), width=4)
        # Left & Right pins
        draw.line([cx - chip_size, cy + offset, cx - chip_size - 18, cy + offset], fill=(0, 229, 255, 255), width=4)
        draw.line([cx + chip_size, cy + offset, cx + chip_size + 18, cy + offset], fill=(0, 229, 255, 255), width=4)

    # Chữ "AI" phong cách Neon nổi bật ở giữa chip
    # Vẽ chữ A
    a_color = (0, 255, 200, 255)
    draw.line([cx - 28, cy + 22, cx - 14, cy - 22], fill=a_color, width=6)
    draw.line([cx - 14, cy - 22, cx, cy + 22], fill=a_color, width=6)
    draw.line([cx - 22, cy + 4, cx - 6, cy + 4], fill=a_color, width=5)
    
    # Vẽ chữ I
    i_color = (129, 140, 248, 255)
    draw.line([cx + 18, cy - 22, cx + 18, cy + 22], fill=i_color, width=6)
    draw.line([cx + 10, cy - 22, cx + 26, cy - 22], fill=i_color, width=5)
    draw.line([cx + 10, cy + 22, cx + 26, cy + 22], fill=i_color, width=5)

    # 4. Lưu ra file PNG và ICO đa kích thước
    png_path = assets_dir / "ai_icon.png"
    ico_path = assets_dir / "ai_icon.ico"
    
    img.save(png_path, "PNG")
    
    # Tạo các icon resolutions: 256, 128, 64, 48, 32, 16
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save(ico_path, format="ICO", sizes=icon_sizes)
    
    print(f"✅ Đã tạo Icon AI thành công tại: {ico_path}")
    return str(ico_path)

if __name__ == "__main__":
    create_ai_icon()
