import os
import sys
import threading
import time
import capture
import customtkinter as ctk
import input
import keyboard
import vision

# Cấu hình giao diện Dark Mode
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Biến toàn cục quản lý luồng Bot
is_running = False
bot_thread = None

# Tọa độ vùng quét hội thoại (Tùy chỉnh theo màn hình)
DIALOGUE_ROI = {"top": 400, "left": 1000, "width": 800, "height": 600}


def get_template_path(filename="dialogue_option.png"):
  """Xác định đường dẫn ảnh mẫu chuẩn khi chạy dạng .py hoặc .exe"""
  base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
  return os.path.join(base_path, "templates", filename)

def log_message(textbox, msg):
  """Hàm ghi log vào giao diện GUI"""
  textbox.configure(state="normal")
  textbox.insert("1.0", f"{msg}\n")
  textbox.configure(state="disabled")


def bot_loop(status_label, log_box):
  """Luồng xử lý chính của Bot"""
  global is_running
  capturer = capture.ScreenCapturer()
  template_path = get_template_path()

  while is_running:
    # Kiểm tra phím F12 để dừng khẩn cấp
    if keyboard.is_pressed("f12"):
      stop_bot(status_label, log_box)
      break

    # 1. Chụp vùng màn hình hội thoại
    img_roi = capturer.grab_roi(DIALOGUE_ROI)

    # 2. Nhận diện thoại
    found, coords = vision.VisionEngine.find_template(
        img_roi, template_path, threshold=0.75
    )

    if found and coords is not None:
      real_x = DIALOGUE_ROI["left"] + coords[0]
      real_y = DIALOGUE_ROI["top"] + coords[1]
      input.human_click(real_x, real_y)
      log_message(log_box, "[+] Phát hiện thoại -> Click chọn")
    else:
      input.human_press_f()

    time.sleep(0.2)


def start_bot(status_label, log_box):
  """Bắt đầu chạy Bot"""
  global is_running, bot_thread
  if not is_running:
    is_running = True
    status_label.configure(text="Trạng thái: ĐANG CHẠY", text_color="#00FF00")
    bot_thread = threading.Thread(
        target=bot_loop, args=(status_label, log_box), daemon=True
    )
    bot_thread.start()
    log_message(log_box, "=== Bot đã khởi động ===")


def stop_bot(status_label, log_box):
  """Tạm dừng Bot"""
  global is_running
  if is_running:
    is_running = False
    status_label.configure(text="Trạng thái: ĐÃ DỪNG", text_color="#FF0000")
    log_message(log_box, "=== Bot đã dừng ===")


def main():
  app = ctk.CTk()
  app.title("Genshin Lore Skip Control Center")
  app.geometry("450x380")
  app.resizable(False, False)

  # Tiêu đề
  title = ctk.CTkLabel(
      app,
      text="GENSHIN AUTO LORE SKIP",
      font=ctk.CTkFont(size=18, weight="bold"),
  )
  title.pack(pady=10)

  # Nhãn trạng thái
  status_label = ctk.CTkLabel(
      app,
      text="Trạng thái: ĐÃ DỪNG",
      font=ctk.CTkFont(size=14),
      text_color="#FF0000",
  )
  status_label.pack(pady=5)

  tip_label = ctk.CTkLabel(
      app, text="Mẹo: Nhấn phím F12 để DỪNG KHẨN CẤP", text_color="#AAAAAA"
  )
  tip_label.pack(pady=2)

  # Khung chứa các nút bấm
  btn_frame = ctk.CTkFrame(app, fg_color="transparent")
  btn_frame.pack(pady=15)

  btn_start = ctk.CTkButton(
      btn_frame,
      text="START (Bắt đầu)",
      width=160,
      height=40,
      fg_color="#28a745",
      hover_color="#218838",
      command=lambda: start_bot(status_label, log_box),
  )
  btn_start.grid(row=0, column=0, padx=10)

  btn_stop = ctk.CTkButton(
      btn_frame,
      text="STOP (Tạm dừng)",
      width=160,
      height=40,
      fg_color="#dc3545",
      hover_color="#c82333",
      command=lambda: stop_bot(status_label, log_box),
  )
  btn_stop.grid(row=0, column=1, padx=10)

  # Bảng Log
  log_box = ctk.CTkTextbox(app, width=400, height=150, state="disabled")
  log_box.pack(pady=10)

  app.mainloop()


if __name__ == "__main__":
  main()