import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Tải biến môi trường từ .env
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Cấu hình Telegram
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
raw_ids = os.getenv("ALLOWED_USER_IDS", "").strip()
ALLOWED_USER_IDS = [int(i.strip()) for i in raw_ids.split(",") if i.strip().isdigit()]

# Cấu hình cửa sổ & Tự động hoá
WINDOW_TITLE_KEYWORD = os.getenv("WINDOW_TITLE_KEYWORD", "Antigravity").strip()
PASTE_DELAY = float(os.getenv("PASTE_DELAY", "0.3"))

# Thư mục lưu trữ tạm
TEMP_DIR = BASE_DIR / "temp_images"
TEMPLATES_DIR = BASE_DIR / "templates"
CALIBRATION_FILE = BASE_DIR / "calibration.json"

TEMP_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

def load_calibration():
    """Tải toạ độ hiệu chỉnh nút bấm nếu có"""
    if CALIBRATION_FILE.exists():
        try:
            with open(CALIBRATION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "chat_input": None,      # Tọa độ ô chat [x, y]
        "accept_button": None,   # Tọa độ nút Accept [x, y]
        "reject_button": None,   # Tọa độ nút Reject [x, y]
        "proceed_button": None,  # Tọa độ nút Proceed [x, y]
        "stop_button": None      # Tọa độ nút Stop [x, y]
    }

def save_calibration(data):
    """Lưu toạ độ hiệu chỉnh nút bấm"""
    with open(CALIBRATION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
