# 🚀 Discord Message Shortcut (DMS)

Send a Discord message **instantly** to a specific channel by pressing a **keyboard shortcut**.
The message is sent **automatically using your own Discord account**.

## ✨ What does this do?

* ⌨️ Press a key → 💬 Message is sent to Discord
* 👤 Uses **your Discord account**
* ⚙️ Easy configurable (shortcut, message, channel)

---

## 📦 Installation

1. Go to the **Releases** page of this repository
2. Download the latest **`.exe`** file
3. Run it

✅ Once started, **DMS will appear in the bottom-right system tray**
(right side of the Windows taskbar)

DMS is now running and ready to be configured.

---

## ⚙️ Configure DMS

To work correctly, DMS needs **4 pieces of information**.

Open the app from the tray icon and go to **Settings**.

### 🧩 1. Obtain Discord Token

1. Open **DMS Settings**
2. Click **`Obtain Discord Token`**
3. A browser window will open
4. After logging into Discord, the token for **your account** will be obtained automatically

### 🧩 2. Enable Developer Mode in Discord

To obtain the remaining IDs, you must enable Developer Mode.

Steps:

1. Open **Discord**
2. Go to **User Settings**
3. Open **Advanced**
4. Enable **Developer Mode**

### 🧩 3. Get required IDs from Discord

Once Developer Mode is enabled:

#### 👤 Discord User ID

* Click on your **own profile**
* Select **Copy User ID**
* Paste it into DMS

#### 🏠 Server ID

* Right-click the **server**
* Select **Copy Server ID**

#### 💬 Channel ID

* Right-click the **channel**
* Select **Copy Channel ID**

---

### 🧩 4. Final configuration

In DMS Settings:

* ⌨️ Choose the **shortcut key** you want
* 💬 Write the **message** to be sent
* ▶️ Click **`Toggle Active`**

---

## ✅ Done!

🎉 **You are up and running!**

From now on:

* Press the shortcut
* The message is instantly sent to the selected Discord channel

---

## 🛠️ Compile it yourself (optional)

If you prefer to build the executable yourself, run:

```bash
uv run pyinstaller --onefile --windowed --name "DiscordMessageShortcut" --icon .\resources\dms_icon.png --add-data "resources;resources" .\src\discord_message_shortcut\main.py
```

---

## 🖥️ Platform

* ✅ Windows
* 🪟 Runs as a system tray application
* 📁 Stores configuration safely in user AppData

---

## 🔐 Security note

This tool uses your **Discord user token**:

* Keep it private
* Use at your own responsibility
* Intended for **personal automation and productivity**

---

If you want, next steps could be:

* Auto-start with Windows
* Multiple shortcuts
* Message templates
* UI themes

Just say the word 😄
