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

is_running = False
bot_thread = None
DIALOGUE_ROI = {"top": 400, "left": 1000, "width": 800, "height": 600}


def log_message(textbox, msg):
  textbox.configure(state="normal")
  textbox.insert("1.0", f"{msg}\n")
  textbox.configure(state="disabled")


def bot_loop(status_label, log_box):
  global is_running
  capturer = capture.ScreenCapturer()
  missing_window_logged = False

  while is_running:
    if keyboard.is_pressed("H"):
      stop_bot(status_label, log_box)
      break

    game_hwnd = capturer.find_game_window()
    if game_hwnd is None:
      if not missing_window_logged:
        log_message(log_box, "Genshin window not found. Open the game before starting.")
        missing_window_logged = True
      time.sleep(0.5)
      continue
    missing_window_logged = False

    try:
      img_roi = capturer.grab_roi(DIALOGUE_ROI, hwnd=game_hwnd)
    except (OSError, ValueError) as error:
      log_message(log_box, f"Unable to capture the Genshin window: {error}")
      stop_bot(status_label, log_box)
      break

    found, coords = vision.VisionEngine.find_template(
        img_roi, "templates/dialouge_option.png", threshold=0.75
    )

    if found and coords is not None:
      real_x = DIALOGUE_ROI["left"] + coords[0]
      real_y = DIALOGUE_ROI["top"] + coords[1]
      try:
        input.human_click(real_x, real_y, hwnd=game_hwnd)
      except (OSError, ValueError) as error:
        log_message(log_box, f"Unable to send input to Genshin: {error}")
        stop_bot(status_label, log_box)
        break
      log_message(log_box, "[+] Phát hiện thoại -> Click")
    else:
      try:
        input.human_press_f(hwnd=game_hwnd)
      except (OSError, ValueError) as error:
        log_message(log_box, f"Unable to send input to Genshin: {error}")
        stop_bot(status_label, log_box)
        break

    time.sleep(0.2)


def start_bot(status_label, log_box):
  global is_running, bot_thread
  if not is_running:
    is_running = True
    status_label.configure(
        text="Trạng thái: ĐANG CHẠY", text_color="#00FF00"
    )
    bot_thread = threading.Thread(
        target=bot_loop, args=(status_label, log_box), daemon=True
    )
    bot_thread.start()
    log_message(log_box, "=== Bot đã khởi động ===")


def stop_bot(status_label, log_box):
  global is_running
  if is_running:
    is_running = False
    status_label.configure(
        text="Trạng thái: ĐÃ DỪNG", text_color="#FF0000"
    )
    log_message(log_box, "=== Bot đã dừng ===")


def render_gui():
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

  # Trạng thái
  status_label = ctk.CTkLabel(
      app,
      text="Trạng thái: ĐÃ DỪNG",
      font=ctk.CTkFont(size=14),
      text_color="#FF0000",
  )
  status_label.pack(pady=5)

  tip_label = ctk.CTkLabel(
      app, text="Mẹo: Nhấn phím H để DỪNG KHẨN CẤP", text_color="#AAAAAA"
  )
  tip_label.pack(pady=2)

  # Khung chứa nút bấm
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

  # Khung Log
  log_box = ctk.CTkTextbox(app, width=400, height=150, state="disabled")
  log_box.pack(pady=10)

  app.mainloop()