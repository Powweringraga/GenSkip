import os
import sys
import threading
import time
import capture
import customtkinter as ctk
import input
import keyboard
import vision

# Cấu hình giao diện CustomTkinter Dark Mode
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Biến toàn cục quản lý trạng thái
is_running = False
bot_thread = None

# Tọa độ vùng quét hộp thoại chọn (Màn hình 1920x1080)
DIALOGUE_ROI = {"top": 400, "left": 1000, "width": 800, "height": 600}


def get_template_path(filename="dialogue_option.png"):
  """Lấy đường dẫn ảnh mẫu chuẩn xác (chạy được cả file .py và .exe đóng gói)"""
  base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
  return os.path.join(base_path, "templates", filename)


def log_message(textbox, msg):
  """Ghi thông báo nhật ký vào bảng Log trên GUI"""
  textbox.configure(state="normal")
  textbox.insert("1.0", f"[{time.strftime('%H:%M:%S')}] {msg}\n")
  textbox.configure(state="disabled")


def run_skip_lore(capturer, template_path, log_box):
  """Vòng lặp tua nhanh thoại và tự động bấm chọn tuỳ chọn hội thoại"""
  img_roi = capturer.grab_roi(DIALOGUE_ROI)
  found, coords = vision.VisionEngine.find_template(
      img_roi, template_path, threshold=0.75
  )

  if found and coords is not None:
    real_x = DIALOGUE_ROI["left"] + coords[0]
    real_y = DIALOGUE_ROI["top"] + coords[1]
    input.human_click(real_x, real_y)
    log_message(log_box, "[+] Bấm chọn tùy chọn hội thoại")
  else:
    input.human_press_f()

  time.sleep(0.18)  # Tốc độ nhấn F tối ưu không lo dính delay game


def bot_loop(status_label, log_box):
  """Luồng điều khiển chính của Bot Skip Lore"""
  global is_running
  capturer = capture.ScreenCapturer()
  template_path = get_template_path()

  while is_running:
    if keyboard.is_pressed("H"):
      stop_bot(status_label, log_box)
      break

    run_skip_lore(capturer, template_path, log_box)


def start_bot(status_label, log_box):
  """Khởi động Bot"""
  global is_running, bot_thread
  if not is_running:
    is_running = True
    status_label.configure(text="Trạng thái: ĐANG CHẠY", text_color="#00FF00")
    bot_thread = threading.Thread(
        target=bot_loop, args=(status_label, log_box), daemon=True
    )
    bot_thread.start()
    log_message(log_box, "=== GenSkip đã khởi động [Skip Lore] ===")


def stop_bot(status_label, log_box):
  """Tạm dừng Bot"""
  global is_running
  if is_running:
    is_running = False
    status_label.configure(text="Trạng thái: ĐÃ DỪNG", text_color="#FF0000")
    log_message(log_box, "=== GenSkip đã dừng ===")


def main():
  app = ctk.CTk()
  app.title("GenSkip - Auto Skip Lore")
  app.geometry("440x360")
  app.resizable(False, False)

  # Tiêu đề
  title = ctk.CTkLabel(
      app, text="GENSKIP AUTOMATION", font=ctk.CTkFont(size=20, weight="bold")
  )
  title.pack(pady=(16, 4))

  # Nhãn trạng thái
  status_label = ctk.CTkLabel(
      app,
      text="Trạng thái: ĐÃ DỪNG",
      font=ctk.CTkFont(size=14, weight="bold"),
      text_color="#FF0000",
  )
  status_label.pack(pady=4)

  tip_label = ctk.CTkLabel(
      app, text="Phím tắt: Nhấn H để DỪNG KHẨN CẤP", text_color="#AAAAAA"
  )
  tip_label.pack(pady=4)

  # Khung Nút Bấm
  btn_frame = ctk.CTkFrame(app, fg_color="transparent")
  btn_frame.pack(pady=16)

  btn_start = ctk.CTkButton(
      btn_frame,
      text="START (Bắt đầu)",
      width=150,
      height=40,
      fg_color="#28a745",
      hover_color="#218838",
      command=lambda: start_bot(status_label, log_box),
  )
  btn_start.grid(row=0, column=0, padx=10)

  btn_stop = ctk.CTkButton(
      btn_frame,
      text="STOP (Tạm dừng)",
      width=150,
      height=40,
      fg_color="#dc3545",
      hover_color="#c82333",
      command=lambda: stop_bot(status_label, log_box),
  )
  btn_stop.grid(row=0, column=1, padx=10)

  # Khung hiển thị Log
  log_box = ctk.CTkTextbox(app, width=390, height=130, state="disabled")
  log_box.pack(pady=8)

  app.mainloop()


if __name__ == "__main__":
  main()