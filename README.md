# WhatsApp Web Desktop Wrapper

A lightweight, modern Windows desktop wrapper for WhatsApp Web built using **PyQt6** and **QtWebEngine**.

![License](https://img.shields.io/github/license/ArpitG420/Whatsapp-Wrapper)
![Platform](https://img.shields.io/badge/platform-Windows-blue)

---

## ⚡ Features

* 🎨 **Native Windows Dark Title Bar:** Clean, custom borderless window with smooth rounded corners (Windows 11 DWM native integration).
* 🚀 **Hardware Acceleration:** Forces GPU acceleration flags for smooth scrolling and low resource usage.
* 📌 **System Tray Integration:** Runs quietly in the background with standard tray icon handling.
* 💾 **Persistent Session & Downloads:** Saves login session data locally (`~/.whatsapp_app_profile`) and handles file downloads seamlessly.
* 🔗 **External Links:** Opens links inside default system browser automatically.

---

## 📞 Enabling Voice & Video Calls

WhatsApp Web supports native voice and video calls through its **Beta feature**. To enable calling inside this app:

1. Open the app and log in to your WhatsApp account.
2. Click the **three dots ⋮** menu above your chat list (or open **Settings** ⚙️).
3. Go to **Help** (or **Settings** ➔ **Help**).
4. Select **Join the Beta** (if available) and confirm.
5. Refresh/restart the app. Once updated, you will see the **Phone 📞** and **Video 📹** call icons at the top of individual chats!

---

## 📦 Installation & Usage

### Option 1: Download Pre-built Executable (Recommended)
1. Go to the [Releases](https://github.com/ArpitG420/Whatsapp-Wrapper/releases) section.
2. Download `WhatsApp.exe`.
3. Double-click to run! *(If Windows SmartScreen appears due to an un-signed binary, click **More Info** ➔ **Run Anyway**).*

### Option 2: Run / Build from Source

**Requirements:** Python 3.10+

1. Clone the repository:
   ```bash
   git clone [https://github.com/ArpitG420/Whatsapp-Wrapper.git](https://github.com/ArpitG420/Whatsapp-Wrapper.git)
   cd Whatsapp-Wrapper

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the script:
   ```bash
   python src/whatsapp.pyw
   ```

4. Package into `.exe`:
   ```bash
   pyinstaller --noconsole --onefile --icon=assets/whatsapp.ico --add-data "assets/whatsapp.ico;assets" --name "WhatsApp" src/whatsapp.pyw
   ```

---

## 📁 Project Structure

```text
Whatsapp-Desktop/
├── assets/
│   └── whatsapp.ico
├── src/
│   └── whatsapp.pyw
├── .gitignore
├── README.md
└── requirements.txt
```

---

## ⚠️ Known Limitations

* **Video Uploads (.mp4):** Pre-compiled `PyQt6-WebEngine` binaries do not ship with proprietary H.264/AAC video codecs due to licensing constraints. Drag-and-dropping videos for in-app preview will show an "unsupported file" error.
  * **Workaround:** To send `.mp4` or other video files, attach them using **Document** (click **📎 Paperclip icon** ➔ **Document**) instead of dragging them directly or selecting "Photos & Videos".

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more details.

---

## ⚠️ Disclaimer

This project is an unofficial, community-driven desktop wrapper for WhatsApp Web. It is **not** affiliated with, authorized, maintained, sponsored, or endorsed by WhatsApp LLC, Meta Platforms, Inc., or any of their affiliates or subsidiaries. All product and company names are trademarks™ or registered® trademarks of their respective holders.

