import os
import sys
import threading
import time
import capture
import customtkinter as ctk
import input
import keyboard
import vision

# Cấu hình CustomTkinter Dark Mode
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Biến toàn cục
is_running = False
is_paused = False
bot_thread = None
start_time = None
skip_count = 0

DIALOGUE_ROI = {"top": 400, "left": 1000, "width": 800, "height": 600}


def get_template_path(filename="dialogue_option.png"):
  base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
  return os.path.join(base_path, "templates", filename)


class GenSkipDashboard(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("GenSkip v1.0.0 Control Center")
    self.geometry("900x560")
    self.resizable(False, False)
    self.configure(fg_color="#0f111a")

    self.grid_columnconfigure(1, weight=1)
    self.grid_rowconfigure(0, weight=1)

    self._build_sidebar()

    # Container chứa các Tab nội dung chính
    self.main_container = ctk.CTkFrame(self, fg_color="transparent")
    self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
    self.main_container.grid_rowconfigure(0, weight=1)
    self.main_container.grid_columnconfigure(0, weight=1)

    # Khởi tạo các View/Tab
    self.frames = {}
    self._build_dashboard_tab()
    self._build_settings_tab()
    self._build_activity_tab()

    # Mặc định hiển thị Dashboard
    self.show_tab("dashboard")
    self._update_timer()

  def _build_sidebar(self):
    """Thanh Sidebar điều hướng bên trái"""
    sidebar = ctk.CTkFrame(
        self, width=200, corner_radius=0, fg_color="#161926"
    )
    sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    sidebar.grid_propagate(False)

    app_title = ctk.CTkLabel(
        sidebar,
        text="GenSkip",
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color="#ffffff",
    )
    app_title.pack(anchor="w", padx=20, pady=(24, 2))

    sub_title = ctk.CTkLabel(
        sidebar,
        text="Control Center",
        font=ctk.CTkFont(size=12),
        text_color="#6c7293",
    )
    sub_title.pack(anchor="w", padx=20, pady=(0, 24))

    # Nút chuyển Tab Sidebar
    self.btn_nav_dash = ctk.CTkButton(
        sidebar,
        text="  Dashboard",
        anchor="w",
        fg_color="#1f2336",
        text_color="#00a8ff",
        height=38,
        corner_radius=6,
        command=lambda: self.show_tab("dashboard"),
    )
    self.btn_nav_dash.pack(fill="x", padx=12, pady=4)

    self.btn_nav_settings = ctk.CTkButton(
        sidebar,
        text="  Settings",
        anchor="w",
        fg_color="transparent",
        text_color="#a0a5ba",
        hover_color="#1f2336",
        height=38,
        corner_radius=6,
        command=lambda: self.show_tab("settings"),
    )
    self.btn_nav_settings.pack(fill="x", padx=12, pady=4)

    self.btn_nav_activity = ctk.CTkButton(
        sidebar,
        text="  Activity Log",
        anchor="w",
        fg_color="transparent",
        text_color="#a0a5ba",
        hover_color="#1f2336",
        height=38,
        corner_radius=6,
        command=lambda: self.show_tab("activity"),
    )
    self.btn_nav_activity.pack(fill="x", padx=12, pady=4)

    # Hotkey Footer
    footer_label = ctk.CTkLabel(
        sidebar,
        text="H Toggle  |  F12 Stop",
        font=ctk.CTkFont(size=11),
        text_color="#525875",
    )
    footer_label.pack(side="bottom", pady=20)

  def show_tab(self, name):
    """Chuyển đổi giao diện màn hình chính giữa các Tab"""
    for frame in self.frames.values():
      frame.grid_remove()

    self.frames[name].grid(row=0, column=0, sticky="nsew")

    # Đổi highlight nút trên Sidebar
    self.btn_nav_dash.configure(
        fg_color="#1f2336" if name == "dashboard" else "transparent",
        text_color="#00a8ff" if name == "dashboard" else "#a0a5ba",
    )
    self.btn_nav_settings.configure(
        fg_color="#1f2336" if name == "settings" else "transparent",
        text_color="#00a8ff" if name == "settings" else "#a0a5ba",
    )
    self.btn_nav_activity.configure(
        fg_color="#1f2336" if name == "activity" else "transparent",
        text_color="#00a8ff" if name == "activity" else "#a0a5ba",
    )

  def _build_dashboard_tab(self):
    """Giao diện Dashboard chính"""
    dash_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
    self.frames["dashboard"] = dash_frame

    # --- TOP METRICS CARDS ---
    metrics_frame = ctk.CTkFrame(dash_frame, fg_color="transparent")
    metrics_frame.pack(fill="x", pady=(0, 16))
    metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="card")

    # Card 1: State
    c1 = ctk.CTkFrame(metrics_frame, fg_color="#161926", corner_radius=8)
    c1.grid(row=0, column=0, padx=6, sticky="nsew")
    ctk.CTkLabel(
        c1, text="STATE", font=ctk.CTkFont(size=10), text_color="#6c7293"
    ).pack(anchor="w", padx=12, pady=(10, 0))
    self.lbl_state = ctk.CTkLabel(
        c1,
        text="Idle",
        font=ctk.CTkFont(size=22, weight="bold"),
        text_color="#ffffff",
    )
    self.lbl_state.pack(anchor="w", padx=12, pady=(2, 12))

    # Card 2: Skips Count
    c2 = ctk.CTkFrame(metrics_frame, fg_color="#161926", corner_radius=8)
    c2.grid(row=0, column=1, padx=6, sticky="nsew")
    ctk.CTkLabel(
        c2, text="SKIPS COUNT", font=ctk.CTkFont(size=10), text_color="#6c7293"
    ).pack(anchor="w", padx=12, pady=(10, 0))
    self.lbl_skips = ctk.CTkLabel(
        c2,
        text="0",
        font=ctk.CTkFont(size=22, weight="bold"),
        text_color="#ffffff",
    )
    self.lbl_skips.pack(anchor="w", padx=12, pady=(2, 12))

    # Card 3: Session Time
    c3 = ctk.CTkFrame(metrics_frame, fg_color="#161926", corner_radius=8)
    c3.grid(row=0, column=2, padx=6, sticky="nsew")
    ctk.CTkLabel(
        c3, text="SESSION TIME", font=ctk.CTkFont(size=10), text_color="#6c7293"
    ).pack(anchor="w", padx=12, pady=(10, 0))
    self.lbl_time = ctk.CTkLabel(
        c3,
        text="00:00:00",
        font=ctk.CTkFont(size=22, weight="bold"),
        text_color="#ffffff",
    )
    self.lbl_time.pack(anchor="w", padx=12, pady=(2, 12))

    # Card 4: Mode Status
    c4 = ctk.CTkFrame(metrics_frame, fg_color="#161926", corner_radius=8)
    c4.grid(row=0, column=3, padx=6, sticky="nsew")
    ctk.CTkLabel(
        c4, text="MODE", font=ctk.CTkFont(size=10), text_color="#6c7293"
    ).pack(anchor="w", padx=12, pady=(10, 0))
    self.lbl_mode = ctk.CTkLabel(
        c4,
        text="Auto Skip",
        font=ctk.CTkFont(size=22, weight="bold"),
        text_color="#ffffff",
    )
    self.lbl_mode.pack(anchor="w", padx=12, pady=(2, 12))

    # --- ACTION BUTTONS ---
    ctrl_frame = ctk.CTkFrame(dash_frame, fg_color="#161926", corner_radius=8)
    ctrl_frame.pack(fill="x", pady=(0, 16))

    btn_inner = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
    btn_inner.pack(padx=12, pady=12, anchor="w")

    self.btn_start = ctk.CTkButton(
        btn_inner,
        text="Start",
        width=100,
        height=36,
        fg_color="#00a8ff",
        hover_color="#0086cc",
        font=ctk.CTkFont(weight="bold"),
        command=self.start_bot,
    )
    self.btn_start.pack(side="left", padx=(0, 8))

    self.btn_pause = ctk.CTkButton(
        btn_inner,
        text="Pause",
        width=100,
        height=36,
        fg_color="#2f3651",
        hover_color="#3e4769",
        font=ctk.CTkFont(weight="bold"),
        command=self.pause_bot,
    )
    self.btn_pause.pack(side="left", padx=(0, 8))

    self.btn_stop = ctk.CTkButton(
        btn_inner,
        text="Stop",
        width=100,
        height=36,
        fg_color="#ff4757",
        hover_color="#d63031",
        font=ctk.CTkFont(weight="bold"),
        command=self.stop_bot,
    )
    self.btn_stop.pack(side="left", padx=(0, 8))

    self.lbl_status_text = ctk.CTkLabel(
        btn_inner,
        text="Stopped",
        font=ctk.CTkFont(size=13),
        text_color="#6c7293",
    )
    self.lbl_status_text.pack(side="left", padx=16)

    # --- LOWER SECTION: CONSOLE & TELEMETRY ---
    lower_frame = ctk.CTkFrame(dash_frame, fg_color="transparent")
    lower_frame.pack(fill="both", expand=True)
    lower_frame.grid_columnconfigure(0, weight=2)
    lower_frame.grid_columnconfigure(1, weight=1)

    log_panel = ctk.CTkFrame(lower_frame, fg_color="#161926", corner_radius=8)
    log_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

    ctk.CTkLabel(
        log_panel,
        text="Console Activity Log",
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color="#00a8ff",
    ).pack(anchor="w", padx=14, pady=(12, 6))

    self.dash_log_box = ctk.CTkTextbox(
        log_panel,
        fg_color="#0f111a",
        text_color="#a0a5ba",
        font=ctk.CTkFont(family="Consolas", size=11),
        corner_radius=6,
    )
    self.dash_log_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))
    self.dash_log_box.configure(state="disabled")

    tele_panel = ctk.CTkFrame(lower_frame, fg_color="#161926", corner_radius=8)
    tele_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

    ctk.CTkLabel(
        tele_panel,
        text="Telemetry",
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color="#a55eea",
    ).pack(anchor="w", padx=14, pady=(12, 10))

    self._add_telemetry_row(tele_panel, "Target ROI X", "1000 - 1800")
    self._add_telemetry_row(tele_panel, "Target ROI Y", "400 - 1000")
    self._add_telemetry_row(tele_panel, "Action Mode", "Auto Click F / Option")
    self._add_telemetry_row(tele_panel, "Hotkeys", "H / F12 Active")

  def _build_settings_tab(self):
    """Giao diện Cài đặt (Settings)"""
    settings_frame = ctk.CTkFrame(
        self.main_container, fg_color="#161926", corner_radius=8
    )
    self.frames["settings"] = settings_frame

    ctk.CTkLabel(
        settings_frame,
        text="Application Settings",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color="#00a8ff",
    ).pack(anchor="w", padx=20, pady=(16, 12))

    # Phím tắt Hotkey
    row1 = ctk.CTkFrame(settings_frame, fg_color="transparent")
    row1.pack(fill="x", padx=20, pady=8)
    ctk.CTkLabel(
        row1,
        text="Toggle Hotkey (Start/Pause):",
        font=ctk.CTkFont(size=13),
        text_color="#ffffff",
    ).pack(side="left")
    entry_toggle = ctk.CTkEntry(row1, width=120)
    entry_toggle.insert(0, "H")
    entry_toggle.pack(side="right")

    row2 = ctk.CTkFrame(settings_frame, fg_color="transparent")
    row2.pack(fill="x", padx=20, pady=8)
    ctk.CTkLabel(
        row2,
        text="Emergency Stop Hotkey:",
        font=ctk.CTkFont(size=13),
        text_color="#ffffff",
    ).pack(side="left")
    entry_stop = ctk.CTkEntry(row2, width=120)
    entry_stop.insert(0, "F12")
    entry_stop.pack(side="right")

    # Tốc độ quét
    row3 = ctk.CTkFrame(settings_frame, fg_color="transparent")
    row3.pack(fill="x", padx=20, pady=8)
    ctk.CTkLabel(
        row3,
        text="Scan Delay Interval (s):",
        font=ctk.CTkFont(size=13),
        text_color="#ffffff",
    ).pack(side="left")
    entry_delay = ctk.CTkEntry(row3, width=120)
    entry_delay.insert(0, "0.18")
    entry_delay.pack(side="right")

    # Độ phân giải
    row4 = ctk.CTkFrame(settings_frame, fg_color="transparent")
    row4.pack(fill="x", padx=20, pady=8)
    ctk.CTkLabel(
        row4,
        text="Game Resolution Preset:",
        font=ctk.CTkFont(size=13),
        text_color="#ffffff",
    ).pack(side="left")
    combo_res = ctk.CTkComboBox(
        row4, values=["1920x1080 (FullHD)", "2560x1440 (2K)", "3840x2160 (4K)"]
    )
    combo_res.set("1920x1080 (FullHD)")
    combo_res.pack(side="right")

    btn_save = ctk.CTkButton(
        settings_frame,
        text="Save Settings",
        fg_color="#00a8ff",
        hover_color="#0086cc",
        command=lambda: self.log("Settings saved successfully."),
    )
    btn_save.pack(anchor="e", padx=20, pady=20)

  def _build_activity_tab(self):
    """Giao diện xem nhật ký chi tiết (Activity Log)"""
    act_frame = ctk.CTkFrame(
        self.main_container, fg_color="#161926", corner_radius=8
    )
    self.frames["activity"] = act_frame

    ctk.CTkLabel(
        act_frame,
        text="Full Activity Log History",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color="#00a8ff",
    ).pack(anchor="w", padx=20, pady=(16, 8))

    self.full_log_box = ctk.CTkTextbox(
        act_frame,
        fg_color="#0f111a",
        text_color="#a0a5ba",
        font=ctk.CTkFont(family="Consolas", size=12),
        corner_radius=6,
    )
    self.full_log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    self.full_log_box.configure(state="disabled")

  def _add_telemetry_row(self, parent, label, value):
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=14, pady=4)
    ctk.CTkLabel(
        row, text=label, font=ctk.CTkFont(size=11), text_color="#6c7293"
    ).pack(side="left")
    ctk.CTkLabel(
        row, text=value, font=ctk.CTkFont(size=11), text_color="#ffffff"
    ).pack(side="right")

  def log(self, msg):
    """Ghi log đồng thời lên cả Dashboard và Activity Tab"""
    time_str = time.strftime("%H:%M:%S")
    formatted_msg = f"[{time_str}] {msg}\n"

    # Dashboard Log Box
    self.dash_log_box.configure(state="normal")
    self.dash_log_box.insert("1.0", formatted_msg)
    self.dash_log_box.configure(state="disabled")

    # Full Activity Log Box
    self.full_log_box.configure(state="normal")
    self.full_log_box.insert("1.0", formatted_msg)
    self.full_log_box.configure(state="disabled")

  def start_bot(self):
    global is_running, is_paused, bot_thread, start_time
    if not is_running:
      is_running = True
      is_paused = False
      start_time = time.time()
      self.lbl_state.configure(text="Running", text_color="#00ff88")
      self.lbl_status_text.configure(text="Running...", text_color="#00ff88")
      bot_thread = threading.Thread(
          target=self._bot_loop, args=(self,), daemon=True
      )
      bot_thread.start()
      self.log("GenSkip engine started.")

  def pause_bot(self):
    global is_paused
    if is_running:
      is_paused = not is_paused
      txt = "Paused" if is_paused else "Running"
      col = "#ffbe76" if is_paused else "#00ff88"
      self.lbl_state.configure(text=txt, text_color=col)
      self.lbl_status_text.configure(
          text="Paused" if is_paused else "Running...", text_color=col
      )
      self.log("GenSkip engine " + ("paused." if is_paused else "resumed."))

  def stop_bot(self):
    global is_running, is_paused
    if is_running:
      is_running = False
      is_paused = False
      self.lbl_state.configure(text="Idle", text_color="#ffffff")
      self.lbl_status_text.configure(text="Stopped", text_color="#6c7293")
      self.log("GenSkip engine stopped.")

  def increment_skip(self):
    global skip_count
    skip_count += 1
    self.lbl_skips.configure(text=str(skip_count))

  def _update_timer(self):
    if is_running and not is_paused and start_time:
      elapsed = int(time.time() - start_time)
      hrs, rem = divmod(elapsed, 3600)
      mins, secs = divmod(rem, 60)
      self.lbl_time.configure(text=f"{hrs:02d}:{mins:02d}:{secs:02d}")
    self.after(1000, self._update_timer)

  def _bot_loop(self, gui):
    global is_running, is_paused
    capturer = capture.ScreenCapturer()
    template_path = get_template_path()

    while is_running:
      if keyboard.is_pressed("f12"):
        gui.stop_bot()
        break

      # ĐỔI HOTKEY THÀNH PHÍM 'H'
      if keyboard.is_pressed("h"):
        if is_running:
          gui.pause_bot()
        else:
          gui.start_bot()
        time.sleep(0.3)

      if not is_paused:
        img_roi = capturer.grab_roi(DIALOGUE_ROI)
        found, coords = vision.VisionEngine.find_template(
            img_roi, template_path, threshold=0.75
        )

        if found and coords is not None:
          real_x = DIALOGUE_ROI["left"] + coords[0]
          real_y = DIALOGUE_ROI["top"] + coords[1]
          input.human_click(real_x, real_y)
          gui.increment_skip()
          gui.log("Selected dialogue option")
        else:
          input.human_press_f()

      time.sleep(0.18)


if __name__ == "__main__":
  app = GenSkipDashboard()
  app.mainloop()