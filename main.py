import os
import sys
import threading
import time
import capture
import customtkinter as ctk
import input
import keyboard
import requests
import vision
from LLM_engine import GenSkipAI

# Cấu hình CustomTkinter Dark Mode
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Biến toàn cục
is_running = False
is_paused = False
bot_thread = None
start_time = None
skip_count = 0

DEFAULT_SERVER_URL = "https://genskipserver.vercel.app"

DIALOGUE_ROI = {"top": 400, "left": 1000, "width": 800, "height": 600}


def get_template_path(filename="dialouge_option.png"):
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, "templates", filename)


def _send_game_input(gui, action, *args, **kwargs):
    try:
        action(*args, **kwargs)
    except (OSError, ValueError) as error:
        gui.log(f"Unable to send input to Genshin: {error}")
        gui.stop_bot()
        return False
    return True


class GenSkipDashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("GenSkip v1.1.0 Control Center")
        self.geometry("900x620")
        self.resizable(False, False)
        self.configure(fg_color="#0f111a")

        # Khởi tạo AI Engine trỏ tới Server Proxy Vercel chuẩn /api
        try:
            self.ai_engine = GenSkipAI(server_url=DEFAULT_SERVER_URL)
        except Exception as e:
            self.ai_engine = None

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

        footer_label = ctk.CTkLabel(
            sidebar,
            text="H Toggle  |  F12 Stop",
            font=ctk.CTkFont(size=11),
            text_color="#525875",
        )
        footer_label.pack(side="bottom", pady=20)

    def show_tab(self, name):
        for frame in self.frames.values():
            frame.grid_remove()

        self.frames[name].grid(row=0, column=0, sticky="nsew")

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
        dash_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frames["dashboard"] = dash_frame

        # METRICS CARDS
        metrics_frame = ctk.CTkFrame(dash_frame, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 12))
        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="card")

        c1 = ctk.CTkFrame(metrics_frame, fg_color="#161926", corner_radius=8)
        c1.grid(row=0, column=0, padx=4, sticky="nsew")
        ctk.CTkLabel(
            c1, text="STATE", font=ctk.CTkFont(size=10), text_color="#6c7293"
        ).pack(anchor="w", padx=12, pady=(8, 0))
        self.lbl_state = ctk.CTkLabel(
            c1,
            text="Idle",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ffffff",
        )
        self.lbl_state.pack(anchor="w", padx=12, pady=(2, 8))

        c2 = ctk.CTkFrame(metrics_frame, fg_color="#161926", corner_radius=8)
        c2.grid(row=0, column=1, padx=4, sticky="nsew")
        ctk.CTkLabel(
            c2, text="SKIPS COUNT", font=ctk.CTkFont(size=10), text_color="#6c7293"
        ).pack(anchor="w", padx=12, pady=(8, 0))
        self.lbl_skips = ctk.CTkLabel(
            c2,
            text="0",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ffffff",
        )
        self.lbl_skips.pack(anchor="w", padx=12, pady=(2, 8))

        c3 = ctk.CTkFrame(metrics_frame, fg_color="#161926", corner_radius=8)
        c3.grid(row=0, column=2, padx=4, sticky="nsew")
        ctk.CTkLabel(
            c3, text="SESSION TIME", font=ctk.CTkFont(size=10), text_color="#6c7293"
        ).pack(anchor="w", padx=12, pady=(8, 0))
        self.lbl_time = ctk.CTkLabel(
            c3,
            text="00:00:00",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ffffff",
        )
        self.lbl_time.pack(anchor="w", padx=12, pady=(2, 8))

        c4 = ctk.CTkFrame(metrics_frame, fg_color="#161926", corner_radius=8)
        c4.grid(row=0, column=3, padx=4, sticky="nsew")
        ctk.CTkLabel(
            c4, text="MODE", font=ctk.CTkFont(size=10), text_color="#6c7293"
        ).pack(anchor="w", padx=12, pady=(8, 0))
        self.lbl_mode = ctk.CTkLabel(
            c4,
            text="Auto Skip",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ffffff",
        )
        self.lbl_mode.pack(anchor="w", padx=12, pady=(2, 8))

        # ACTION BUTTONS
        ctrl_frame = ctk.CTkFrame(dash_frame, fg_color="#161926", corner_radius=8)
        ctrl_frame.pack(fill="x", pady=(0, 12))

        btn_inner = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        btn_inner.pack(padx=12, pady=10, anchor="w")

        self.btn_start = ctk.CTkButton(
            btn_inner,
            text="Start",
            width=90,
            height=34,
            fg_color="#00a8ff",
            hover_color="#0086cc",
            font=ctk.CTkFont(weight="bold"),
            command=self.start_bot,
        )
        self.btn_start.pack(side="left", padx=(0, 8))

        self.btn_pause = ctk.CTkButton(
            btn_inner,
            text="Pause",
            width=90,
            height=34,
            fg_color="#2f3651",
            hover_color="#3e4769",
            font=ctk.CTkFont(weight="bold"),
            command=self.pause_bot,
        )
        self.btn_pause.pack(side="left", padx=(0, 8))

        self.btn_stop = ctk.CTkButton(
            btn_inner,
            text="Stop",
            width=90,
            height=34,
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

        # CONSOLE & TELEMETRY
        lower_frame = ctk.CTkFrame(dash_frame, fg_color="transparent")
        lower_frame.pack(fill="x", pady=(0, 12))
        lower_frame.grid_columnconfigure(0, weight=2)
        lower_frame.grid_columnconfigure(1, weight=1)

        log_panel = ctk.CTkFrame(lower_frame, fg_color="#161926", corner_radius=8)
        log_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        ctk.CTkLabel(
            log_panel,
            text="Console Activity Log",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00a8ff",
        ).pack(anchor="w", padx=12, pady=(8, 4))

        self.dash_log_box = ctk.CTkTextbox(
            log_panel,
            fg_color="#0f111a",
            text_color="#a0a5ba",
            font=ctk.CTkFont(family="Consolas", size=10),
            corner_radius=6,
            height=130,
        )
        self.dash_log_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.dash_log_box.configure(state="disabled")

        tele_panel = ctk.CTkFrame(lower_frame, fg_color="#161926", corner_radius=8)
        tele_panel.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

        ctk.CTkLabel(
            tele_panel,
            text="Telemetry",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#a55eea",
        ).pack(anchor="w", padx=12, pady=(8, 6))

        self._add_telemetry_row(tele_panel, "Target ROI X", "1000 - 1800")
        self._add_telemetry_row(tele_panel, "Target ROI Y", "400 - 1000")
        self._add_telemetry_row(tele_panel, "AI Mode", "Smart Choice & Summarize")
        self._add_telemetry_row(tele_panel, "Hotkeys", "H / F12 Active")

        # LLM LORE SUMMARY PANEL
        ai_panel = ctk.CTkFrame(dash_frame, fg_color="#161926", corner_radius=8)
        ai_panel.pack(fill="x")

        ctk.CTkLabel(
            ai_panel,
            text="✨ Live Quest Dialogue Summary (Powered by Proxy AI)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00e676",
        ).pack(anchor="w", padx=12, pady=(8, 2))

        self.lbl_ai_summary = ctk.CTkLabel(
            ai_panel,
            text="Đang chờ thoại... AI Engine kết nối qua Proxy Server sẵn sàng.",
            font=ctk.CTkFont(size=11),
            text_color="#a0a5ba",
            wraplength=620,
            justify="left",
        )
        self.lbl_ai_summary.pack(anchor="w", padx=12, pady=(0, 10))

    def _build_settings_tab(self):
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

      row_server = ctk.CTkFrame(settings_frame, fg_color="transparent")
      row_server.pack(fill="x", padx=20, pady=8)

      ctk.CTkLabel(
          row_server,
          text="Proxy Server Base URL:",
          font=ctk.CTkFont(size=13),
          text_color="#00e676",
      ).pack(side="left")

      # Nút Unlock có biểu tượng khóa
      self.btn_unlock = ctk.CTkButton(
          row_server,
          text="🔒 Unlock",
          width=70,
          fg_color="#2f3651",
          hover_color="#3e4769",
          command=self.unlock_settings,
      )
      self.btn_unlock.pack(side="right", padx=(8, 0))

      # Ô nhập URL ở trạng thái mặc định bị khóa (disabled)
      self.entry_server_url = ctk.CTkEntry(
          row_server, width=280, state="disabled"
      )
      self.entry_server_url.configure(state="normal")
      self.entry_server_url.insert(0, DEFAULT_SERVER_URL)
      self.entry_server_url.configure(state="disabled")
      self.entry_server_url.pack(side="right")

      # Nút Save Settings mặc định bị ẩn/khóa
      self.btn_save = ctk.CTkButton(
          settings_frame,
          text="Save Settings",
          fg_color="#1f2336",
          text_color="#6c7293",
          state="disabled",
          command=self.save_settings,
      )
      self.btn_save.pack(anchor="e", padx=20, pady=20)

    def unlock_settings(self):
      """Mở dialog yêu cầu nhập mật khẩu để cho phép chỉnh sửa Settings."""
      dialog = ctk.CTkInputDialog(
          text="Nhập mật khẩu quản trị để mở khóa Settings:",
          title="Xác thực Admin",
      )
      password = dialog.get_input()

      # Đặt mật khẩu mở khóa tại đây (Ví dụ: admin123)
      ADMIN_PASSWORD = "p0wwie"

      if password == ADMIN_PASSWORD:
        # Nhập đúng password -> Mở khóa ô URL và nút Save
        self.entry_server_url.configure(state="normal")
        self.btn_save.configure(
            state="normal", fg_color="#00a8ff", text_color="#ffffff"
        )
        self.btn_unlock.configure(
            text="🔓 Unlocked", state="disabled", fg_color="#00e676"
        )
        self.log("Settings đã được mở khóa thành công.")
      elif password is not None:
        # Nhập sai password -> Thông báo lỗi
        self.log("Mở khóa thất bại: Mật khẩu không chính xác!")

    def save_settings(self):
        try:
            server_url = self.entry_server_url.get().strip()
            # Khởi tạo lại GenSkipAI với Base URL mới
            self.ai_engine = GenSkipAI(server_url=server_url)
            self.lbl_ai_summary.configure(
                text="AI Engine sẵn sàng tóm tắt hội thoại."
            )
            self.log(f"Gemini AI Proxy Engine re-initialized with URL: {server_url}")
        except Exception as e:
            self.log(f"Error initializing AI: {e}")

    def _build_activity_tab(self):
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
        row.pack(fill="x", padx=10, pady=3)
        ctk.CTkLabel(
            row, text=label, font=ctk.CTkFont(size=11), text_color="#6c7293"
        ).pack(side="left")
        ctk.CTkLabel(
            row, text=value, font=ctk.CTkFont(size=11), text_color="#ffffff"
        ).pack(side="right")

    def log(self, msg):
        time_str = time.strftime("%H:%M:%S")
        formatted_msg = f"[{time_str}] {msg}\n"

        self.dash_log_box.configure(state="normal")
        self.dash_log_box.insert("1.0", formatted_msg)
        self.dash_log_box.configure(state="disabled")

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
        last_llm_time = time.time()
        missing_window_logged = False

        while is_running:
            if keyboard.is_pressed("f12"):
                gui.stop_bot()
                break

            if keyboard.is_pressed("h"):
                if is_running:
                    gui.pause_bot()
                else:
                    gui.start_bot()
                time.sleep(0.03)  # Tránh nhấn liên tục

            if not is_paused:
                game_hwnd = capturer.find_game_window()
                if game_hwnd is None:
                    if not missing_window_logged:
                        gui.log("Genshin window not found. Open the game before starting.")
                        missing_window_logged = True
                    time.sleep(0.5)
                    continue
                missing_window_logged = False

                try:
                    img_roi = capturer.grab_roi(DIALOGUE_ROI, hwnd=game_hwnd)
                except (OSError, ValueError) as error:
                    gui.log(f"Unable to capture the Genshin window: {error}")
                    gui.stop_bot()
                    break

                # 1. Thu thập chữ thoại liên tục vào bộ đệm (Buffer)
                if gui.ai_engine:
                    try:
                        gui.ai_engine.extract_text(img_roi)
                    except RuntimeError as error:
                        gui.log(f"Dialogue OCR unavailable: {error}")
                        gui.ai_engine = None

                # 2. Phát hiện các phương án lựa chọn hội thoại
                options_text, options_coords = vision.VisionEngine.extract_all_choices(
                    img_roi, template_path, threshold=0.70
                )

                if options_text and options_coords:
                    # NẾU CÓ TỪ 2 LỰA CHỌN TRỞ LÊN ➔ GỌI AI SMART CHOICE
                    if len(options_text) > 1 and gui.ai_engine:
                        gui.log(f"Phát hiện {len(options_text)} phương án lựa chọn...")
                        recent_context = "\n".join(gui.ai_engine.buffer[-5:])
                        try:
                            best_idx = gui.ai_engine.select_best_choice(
                                context=recent_context, options=options_text
                            )
                        except (requests.RequestException, ValueError) as error:
                            gui.log(
                                f"AI choice unavailable; selecting the first option: {error}"
                            )
                            best_idx = 1

                        # Click vào tọa độ Y tương ứng với lựa chọn AI khuyên (Index 1-based)
                        target_rel_x, target_rel_y = options_coords[best_idx - 1]
                        real_x = DIALOGUE_ROI["left"] + target_rel_x
                        real_y = DIALOGUE_ROI["top"] + target_rel_y

                        if not _send_game_input(
                            gui,
                            input.human_click,
                            real_x,
                            real_y,
                            hwnd=game_hwnd,
                        ):
                            break
                        gui.increment_skip()
                        gui.log(
                            f"🤖 AI chọn Option {best_idx}: '{options_text[best_idx-1]}'"
                        )
                    else:
                        # Nếu chỉ có 1 nút duy nhất
                        target_rel_x, target_rel_y = options_coords[0]
                        real_x = DIALOGUE_ROI["left"] + target_rel_x
                        real_y = DIALOGUE_ROI["top"] + target_rel_y
                        if not _send_game_input(
                            gui,
                            input.human_click,
                            real_x,
                            real_y,
                            hwnd=game_hwnd,
                        ):
                            break
                        gui.increment_skip()
                        gui.log("Click option mặc định.")
                else:
                    # Không có bảng lựa chọn ➔ Nhấn F tua thoại thông thường
                    if not _send_game_input(
                        gui, input.human_press_f, hwnd=game_hwnd
                    ):
                        break

                # 3. Summarize captured dialogue for the current quest.
                if gui.ai_engine and (time.time() - last_llm_time > 8):
                    last_llm_time = time.time()
                    summary = gui.ai_engine.summarize_buffered_lore()
                    if summary and not summary.startswith("AI summary unavailable:"):
                        gui.lbl_ai_summary.configure(text=summary)
                    elif summary:
                        gui.log(summary)

            time.sleep(0.18)


if __name__ == "__main__":
    app = GenSkipDashboard()
    app.mainloop()