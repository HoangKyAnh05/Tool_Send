import os
import time
from pathlib import Path
import telebot
from telebot import types

import config
from modules.ui_automator import UIAutomator
from modules.screen_capturer import capture_screen
from modules.window_manager import (
    find_antigravity_window,
    get_all_antigravity_windows,
    set_active_target_window,
    focus_window
)

def create_main_keyboard():
    """Tạo bảng nút bấm điều khiển nhanh gắn kèm tin nhắn"""
    markup = types.InlineKeyboardMarkup(row_width=2)

    btn_accept = types.InlineKeyboardButton("✅ Accept All", callback_data="act_accept")
    btn_reject = types.InlineKeyboardButton("❌ Reject All", callback_data="act_reject")
    btn_undo = types.InlineKeyboardButton("↩️ Undo Lệnh Trước", callback_data="act_undo")
    btn_stop = types.InlineKeyboardButton("🛑 Stop Task", callback_data="act_stop")
    btn_switch = types.InlineKeyboardButton("🔀 Đổi Cửa Sổ Dự Án", callback_data="act_switch_menu")
    btn_screen = types.InlineKeyboardButton("📷 Xem Màn Hình Live", callback_data="act_screen")
    btn_status = types.InlineKeyboardButton("🔍 Kiểm Tra Kết Nối", callback_data="act_status")

    markup.add(btn_accept, btn_reject)
    markup.add(btn_undo, btn_stop)
    markup.add(btn_switch)
    markup.add(btn_screen, btn_status)
    return markup

def create_window_switch_keyboard():
    """Tạo bàn phím danh sách các cửa sổ Antigravity IDE đang mở để chọn"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    windows = get_all_antigravity_windows()

    if not windows:
        markup.add(types.InlineKeyboardButton("🔄 Quét Lại Danh Sách", callback_data="act_switch_menu"))
        markup.add(types.InlineKeyboardButton("⬅️ Quay Lại Menu", callback_data="act_back_main"))
        return markup, "⚠️ **Chưa phát hiện cửa sổ Antigravity IDE nào đang mở.**\n_Hãy mở một dự án Antigravity trên máy tính rồi bấm Quét Lại._"

    msg_text = "🔀 **DANH SÁCH DỰ ÁN ANTIGRAVITY ĐANG MỞ:**\n\n_Bấm vào dự án bạn muốn điều khiển:_\n"

    for win in windows:
        icon = "🟢" if win["is_active"] else "⚪"
        active_tag = " (ĐANG CHỌN)" if win["is_active"] else ""
        btn_text = f"{icon} {win['display_name']}{active_tag}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"sel_win_{win['hwnd']}"))
        
        file_info = f" _({win['active_file']})_" if win.get('active_file') else ""
        msg_text += f"{icon} **{win['project_name']}**{file_info}\n"

    markup.add(types.InlineKeyboardButton("🔄 Quét Lại", callback_data="act_switch_menu"))
    markup.add(types.InlineKeyboardButton("⬅️ Quay Lại Menu", callback_data="act_back_main"))
    return markup, msg_text

def setup_bot(bot_token: str):
    bot = telebot.TeleBot(bot_token)
    automator = UIAutomator()

    def is_authorized(user_id: int) -> bool:
        if not config.ALLOWED_USER_IDS:
            return True
        return user_id in config.ALLOWED_USER_IDS

    def check_auth_decorator(func):
        def wrapper(message, *args, **kwargs):
            uid = message.from_user.id
            if not is_authorized(uid):
                bot.reply_to(
                    message,
                    f"⛔ **Từ chối truy cập!**\n\nTelegram ID của bạn là: `{uid}`\n"
                    f"Vui lòng thêm ID này vào biến `ALLOWED_USER_IDS` trong file `.env` trên máy tính.",
                    parse_mode="Markdown"
                )
                return
            return func(message, *args, **kwargs)
        return wrapper

    # --- LỆNH /start, /help, /menu ---
    @bot.message_handler(commands=['start', 'help', 'menu'])
    @check_auth_decorator
    def handle_start(message):
        hwnd, cur_title = find_antigravity_window()
        all_wins = get_all_antigravity_windows()
        
        text = (
            "👋 **Antigravity Remote Controller**\n\n"
            f"🎯 **Dự án đang chọn**: `{cur_title}`\n"
            f"📂 **Tổng số dự án Antigravity phát hiện**: `{len(all_wins)}`\n\n"
            "✨ **Cách dùng:**\n"
            "1. 💬 Gõ tin nhắn bất kỳ $\\rightarrow$ Tự động dán Prompt vào ô Chat.\n"
            "2. 📷 Gửi ảnh $\\rightarrow$ Tự động dán ảnh vào Antigravity.\n"
            "3. 🔀 Bấm **Đổi Cửa Sổ Dự Án** để chuyển giữa các dự án đang mở.\n"
            "4. ↩️ Bấm **Undo Lệnh Trước** để hoàn tác / gọi lại câu lệnh trước.\n"
            "5. ✅ Bấm **Accept All / Reject All** để duyệt mã code."
        )
        bot.send_message(message.chat.id, text, reply_markup=create_main_keyboard(), parse_mode="Markdown")

    # --- LỆNH /windows, /switch ---
    @bot.message_handler(commands=['windows', 'switch'])
    @check_auth_decorator
    def handle_windows_cmd(message):
        markup, text = create_window_switch_keyboard()
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

    # --- LỆNH /undo ---
    @bot.message_handler(commands=['undo'])
    @check_auth_decorator
    def handle_undo_cmd(message):
        bot.send_chat_action(message.chat.id, 'typing')
        success, msg, screen_path = automator.undo_prompt()
        _send_action_result(message.chat.id, "↩️ Undo Lệnh", msg, screen_path)

    # --- LỆNH /screen ---
    @bot.message_handler(commands=['screen'])
    @check_auth_decorator
    def handle_screen_cmd(message):
        send_live_screen(message.chat.id)

    # --- XỬ LÝ ẢNH TỪ ĐIỆN THOẠI ---
    @bot.message_handler(content_types=['photo'])
    @check_auth_decorator
    def handle_photo(message):
        try:
            bot.send_chat_action(message.chat.id, 'upload_photo')
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            local_image_path = config.TEMP_DIR / f"received_{int(time.time())}.jpg"
            with open(local_image_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            caption = message.caption or ""
            success, msg, screen_path = automator.send_prompt(text=caption, image_path=str(local_image_path))

            if screen_path and Path(screen_path).exists():
                with open(screen_path, 'rb') as photo_file:
                    bot.send_photo(
                        message.chat.id,
                        photo_file,
                        caption=f"📸 {msg}",
                        reply_markup=create_main_keyboard()
                    )
            else:
                bot.send_message(message.chat.id, f"ℹ️ {msg}", reply_markup=create_main_keyboard())

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Lỗi xử lý ảnh: {e}", reply_markup=create_main_keyboard())

    # --- XỬ LÝ TIN NHẮN VĂN BẢN (PROMPT) ---
    @bot.message_handler(content_types=['text'])
    @check_auth_decorator
    def handle_text(message):
        user_text = message.text.strip()
        if user_text.startswith('/'):
            return

        bot.send_chat_action(message.chat.id, 'typing')
        success, msg, screen_path = automator.send_prompt(text=user_text)

        if screen_path and Path(screen_path).exists():
            with open(screen_path, 'rb') as photo_file:
                bot.send_photo(
                    message.chat.id,
                    photo_file,
                    caption=f"🚀 **Đã gửi câu lệnh!**\n`{user_text[:150]}`\n\n_{msg}_",
                    reply_markup=create_main_keyboard(),
                    parse_mode="Markdown"
                )
        else:
            bot.send_message(message.chat.id, f"ℹ️ {msg}", reply_markup=create_main_keyboard())

    # --- XỬ LÝ NÚT BẤM (INLINE CALLBACKS) ---
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        uid = call.from_user.id
        if not is_authorized(uid):
            bot.answer_callback_query(call.id, "⛔ Bạn không có quyền điều khiển!", show_alert=True)
            return

        action = call.data
        chat_id = call.message.chat.id

        # 1. Menu đổi cửa sổ
        if action == "act_switch_menu":
            bot.answer_callback_query(call.id, "🔍 Đang quét các dự án Antigravity...")
            markup, text = create_window_switch_keyboard()
            try:
                bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")
            except Exception:
                bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

        # 2. Xử lý khi chọn 1 cửa sổ cụ thể (sel_win_<hwnd>)
        elif action.startswith("sel_win_"):
            target_hwnd = int(action.replace("sel_win_", ""))
            bot.answer_callback_query(call.id, "⚡ Đang chuyển cửa sổ dự án...")

            # Tìm thông tin cửa sổ được chọn
            all_anti = get_all_antigravity_windows()
            selected_win = next((w for w in all_anti if w["hwnd"] == target_hwnd), None)

            if selected_win:
                set_active_target_window(target_hwnd, selected_win["full_title"])
                focus_window(target_hwnd)
                time.sleep(0.3)

                # Chụp ảnh cửa sổ mới được chọn gửi cho người dùng
                screen_path = capture_screen(target_hwnd, output_filename="switched_win.jpg")
                confirm_text = f"🎯 **ĐÃ CHUYỂN SANG ĐIỀU KHIỂN DỰ ÁN:**\n`{selected_win['project_name']}`\n_{selected_win['full_title']}_"

                if screen_path and Path(screen_path).exists():
                    with open(screen_path, 'rb') as photo_file:
                        bot.send_photo(chat_id, photo_file, caption=confirm_text, reply_markup=create_main_keyboard(), parse_mode="Markdown")
                else:
                    bot.send_message(chat_id, confirm_text, reply_markup=create_main_keyboard(), parse_mode="Markdown")
            else:
                bot.send_message(chat_id, "⚠️ Cửa sổ này có thể đã bị đóng. Vui lòng quét lại danh sách.", reply_markup=create_main_keyboard())

        # 3. Quay lại menu chính
        elif action == "act_back_main":
            bot.answer_callback_query(call.id)
            hwnd, cur_title = find_antigravity_window()
            text = f"📱 **Menu Điều Khiển**\n🎯 Cửa sổ hiện tại: `{cur_title}`"
            try:
                bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=create_main_keyboard(), parse_mode="Markdown")
            except Exception:
                bot.send_message(chat_id, text, reply_markup=create_main_keyboard(), parse_mode="Markdown")

        elif action == "act_screen":
            bot.answer_callback_query(call.id, "📸 Đang chụp màn hình...")
            send_live_screen(chat_id)

        elif action == "act_accept":
            bot.answer_callback_query(call.id, "✅ Đang thực hiện Accept All...")
            success, msg, screen_path = automator.accept_all()
            _send_action_result(chat_id, "✅ Accept All", msg, screen_path)

        elif action == "act_reject":
            bot.answer_callback_query(call.id, "❌ Đang thực hiện Reject All...")
            success, msg, screen_path = automator.reject_all()
            _send_action_result(chat_id, "❌ Reject All", msg, screen_path)

        elif action == "act_undo":
            bot.answer_callback_query(call.id, "↩️ Đang hoàn tác / gọi lại lệnh trước...")
            success, msg, screen_path = automator.undo_prompt()
            _send_action_result(chat_id, "↩️ Undo Lệnh", msg, screen_path)

        elif action == "act_stop":
            bot.answer_callback_query(call.id, "🛑 Đang dừng tác vụ...")
            success, msg, screen_path = automator.stop_task()
            _send_action_result(chat_id, "🛑 Stop Task", msg, screen_path)

        elif action == "act_status":
            hwnd, title = find_antigravity_window()
            all_wins = get_all_antigravity_windows()
            status_text = (
                f"🖥️ **Trạng Thái Hệ Thống:**\n"
                f"• Cửa sổ đang điều khiển: `{title}`\n"
                f"• Tổng số dự án Antigravity: **{len(all_wins)} dự án**\n"
                f"• ID Telegram của bạn: `{uid}`"
            )
            bot.send_message(chat_id, status_text, reply_markup=create_main_keyboard(), parse_mode="Markdown")

    def send_live_screen(chat_id):
        hwnd, cur_title = find_antigravity_window()
        screen_path = capture_screen(hwnd, output_filename="live_view.jpg")

        with open(screen_path, 'rb') as photo_file:
            bot.send_photo(
                chat_id,
                photo_file,
                caption=f"📸 **Live Screen**: `{cur_title}`",
                reply_markup=create_main_keyboard(),
                parse_mode="Markdown"
            )

    def _send_action_result(chat_id, action_title, msg, screen_path):
        if screen_path and Path(screen_path).exists():
            with open(screen_path, 'rb') as photo_file:
                bot.send_photo(
                    chat_id,
                    photo_file,
                    caption=f"{action_title}: {msg}",
                    reply_markup=create_main_keyboard()
                )
        else:
            bot.send_message(chat_id, f"{action_title}: {msg}", reply_markup=create_main_keyboard())

    return bot
