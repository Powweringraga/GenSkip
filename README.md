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
- ⌨️ **Smart Key Pressing:** Auto-spams the `F` key when no dialogue choices are present to speed through text.
- 💻 **Modern Graphical User Interface:** Intuitive control panel allowing you to `START` and `STOP` with a single click.
- 🛑 **Emergency Stop Hotkey:** Press **`H`** anytime to instantly halt the bot directly from inside the game.
- 📦 **Standalone Executable:** Fully packaged `.exe` file—no Python installation or library setup required for end users.

---

### 📥 Installation & Usage Guide

#### For End Users (Executable Version)
1. Navigate to the **Releases** section of this repository and download `GenSkip.zip`.
2. Extract the `GenSkip` folder onto your computer.
3. Launch **Genshin Impact** (Borderless Windowed mode recommended).
4. Right-click **`main.exe`** and select **Run as administrator** (Required to send keystrokes and clicks to the game).
5. Click **START** on the GUI to begin, and press **STOP** or hit **`H`** to pause/stop at any time.

#### For Developers (Running from Source)
If you wish to modify or run the source code directly, install the required dependencies:
```powershell
py -m pip install mss pydirectinput opencv-python numpy customtkinter keyboard pyinstaller
