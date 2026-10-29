# ⚡ GenSkip (Genshin Impact Auto Lore Skip) - Beta

[![GitHub Release](https://img.shields.io/github/v/release/Powweringraga/GenSkip?color=blue)](https://github.com/Powweringraga/GenSkip/releases)
[![GitHub Downloads](https://img.shields.io/github/downloads/Powweringraga/GenSkip/total?color=green)](https://github.com/Powweringraga/GenSkip/releases)
[![GitHub License](https://img.shields.io/github/license/Powweringraga/GenSkip?color=orange)](https://github.com/Powweringraga/GenSkip/blob/main/LICENSE)
---

### 📖 Introduction
**GenSkip** is a lightweight automation utility built with Python and a modern **CustomTkinter** GUI. It helps players automatically skip long dialogue sequences and lore cutscenes in Genshin Impact smoothly and seamlessly.

> [!WARNING]
> **Disclaimer:** This software is developed purely for educational and personal use. Using automation tools in games may violate the publisher's Terms of Service. Use at your own discretion.

---

### ✨ Key Features
- 🚀 **Automatic Dialogue Detection:** Real-time screen scanning and dialogue choice detection via OpenCV Template Matching.
- ⌨️ **Smart Key Pressing:** Auto-spams the `Space` key when no dialogue choices are present to speed through text.
- 🪟 **Background Support:** Captures and sends input to the Genshin window while another app is active.
- 💻 **Modern Graphical User Interface:** Intuitive control panel allowing you to `START` and `STOP` with a single click.
- 🛑 **Hotkeys:** Press **`H`** to pause/resume and **`F12`** to stop the bot.
- 📦 **Standalone Executable:** Fully packaged `.exe` file—no Python installation or library setup required for end users.

---

### 📥 Installation & Usage Guide

#### For End Users (Executable Version)
1. Navigate to the **Releases** section of this repository and download `GenSkip.zip`.
2. Extract the `GenSkip` folder onto your computer.
3. Launch **Genshin Impact** in **Borderless Windowed** mode. Keep the game open and do not minimize it.
4. Launch `main.exe`, click **START**, then switch to Chrome, Spotify, or another app.
5. Press **STOP** in GenSkip or use **`H`** to pause/resume. Press **`F12`** to stop.

Background input depends on Genshin accepting Windows window messages, and background capture depends on the game exposing its window image. If the game ignores input or the captured image is blank, keep Genshin in the foreground; these behaviors can vary by game version and display mode.

#### For Developers (Running from Source)
If you wish to modify or run the source code directly, install the required dependencies:
```

Dialogue transcription also requires the Tesseract OCR application with its English language data. Add Tesseract to `PATH`, or set `TESSERACT_CMD` to its executable path before launching GenSkip.powershell
py -m pip install mss pyautogui pillow opencv-python numpy customtkinter keyboard pyinstaller pytesseract
