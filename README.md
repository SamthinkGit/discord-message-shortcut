# 🚀 Discord Message Shortcut (DMS)

Send a Discord message **instantly** to a specific channel by pressing a **keyboard shortcut**.
The message is sent **automatically using your own Discord account**.

## ✨ What does this do?

* ⌨️ Press a key → 💬 Message is sent to Discord
* 👤 Uses **your Discord account**
* ⚙️ Easy configurable (shortcut, message, channel)

---

## 📦 Installation

1. Go to the [Releases](https://github.com/SamthinkGit/discord-message-shortcut/releases/tag/1.0.0) page of this repository to download DMS and download `DiscordMessageShortcut.exe`

✅ Once started, **DMS will appear in the bottom-right system tray**

<div align="center">
<img width="890" height="374" alt="image (1)" src="https://github.com/user-attachments/assets/aa8096f8-e00d-423c-9d54-96762ad0356e" />
</div>

---


## ⚙️ Configure DMS

To work correctly, DMS needs **4 pieces of information**.

Open the app from the tray icon and go to **Settings**.

### 🧩 1. Obtain Discord Token

<div align="center">
<img width="665" alt="image (2)" src="https://github.com/user-attachments/assets/142a0395-e168-478c-9b49-751ba8af61a7" />
</div>

1. Right click on DMS
2. Open **DMS Settings**
3. Click **`Obtain Discord Token`**
4. After logging into Discord, the token for **your account** will be shown.
5. Save that token as your **Discord Token** in DMS
 
<div align="center">
<img width="877" alt="image (3)" src="https://github.com/user-attachments/assets/c57fee64-9eb5-414c-b05a-fc1b964d428c" />
</div>

### 🧩 2. Enable Developer Mode in Discord

To obtain the remaining IDs, you must enable Developer Mode.

Steps:

1. Open **Discord**
2. Go to **User Settings**
3. Open **Advanced**
4. Enable **Developer Mode**

<div align="center">
<img width="1369" height="848" alt="image (4)" src="https://github.com/user-attachments/assets/99cfca55-be75-4f99-a16e-b21ece8d8c69" />
</div>

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

<div align="center">
  <img width="1069" alt="image (5)" src="https://github.com/user-attachments/assets/ecf1168a-3e69-4a3b-aa3d-95a855f4f06f" />
</div>


### 🧩 4. Final configuration

In DMS Settings:

* ⌨️ Choose the **shortcut key** you want
* 💬 Write the **message** to be sent
* ▶️ Click **`Toggle Active`**

## ✅ Done!

🎉 **You are up and running!**

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

