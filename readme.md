# 🌐 FFXI Multi-Account Launcher

A custom launcher for Final Fantasy XI that allows **multi-account login**, profile management, and PlayOnline config swapping — all through a GUI.

> 🧙 Built with ❤️ for multiboxing adventurers of Vana'diel.

---

## 🚀 Features

- 🔑 **Manage up to 6 FFXI accounts**
- 🗂️ Account editor with SE ID, POL ID, passwords, and OTP toggle
- ⚙️ Automatically swaps `.bin` to log in new accounts
- 🪟 Uses Windower to launch in windowed full screen
- 🛠️ Built-in log viewer and file logger (`ffxi_launcher.log`)
- 🔁 Launch multiple accounts with automatic delays
- 🧪 One-time password (OTP) input handled manually with wait time
- 🖼️ Customizable launcher icon (uses `ffxi.ico`)
- 📦 PyInstaller-ready `.spec` generation and EXE packaging

---

## 🧾 Requirements

- ✅ Python 3.8+
- ✅ PyQt5
- ✅ psutil
- ✅ Windower4 installed and configured

### 🛠 Install Dependencies

```bash
pip install pyqt5 psutil
```

---

## 💻 Running the Launcher

```bash
python ffxi_launcher.py
```

🔒 First-time use? Edit your accounts with the **“Edit/Add Accounts”** button.

💡 Each account populated POL must have its own `.bin` file that swaps the POL accounts.

Building the `.bin` (Make sure to change the directory to match your own installation of FFXI):

```
Load up POL, add in your four accounts, log in with all of them so you get through all the stupid one-time prompts.

Go to C:\ProgFiles\POL\SE\POLView\usr\all

Rename login_w.bin to 1.bin

Load up POL again, it should make a new login_w.bin and everything cleared. Add your other two accounts and login in with both of them.

Rename login_w.bin to 2.bin

Open notepad and add the following, edit path as necessary:

Copy "C:\PFiles\POL\SE\POLView\usr\all\1.bin"

"C:\PFiles\POL\SE\POLView\usr\all\login_w.bin"

"C:\Users\me\Desktop\Windower\Windower.lnk" <-this is a shortcut made that opens windower with your default profile

Save the file to your desktop as whatever.bat

Make a copy of it and edit 1.bin to 2.bin

If its all the same SEID, you can add the following to the batch file:
echo|set/p=yourpassword|clip

This will add "yourpassword" to clipboard. Loading up XI or entering a wrong password will clear the clipboard if you werent aware.
```

---

## 🔧 Building an EXE

Install [PyInstaller](https://www.pyinstaller.org/):

```bash
pip install pyinstaller
```

Then run:

```bash
pyinstaller --onefile --icon=ffxi.ico ffxi_launcher.py
```

A `.spec` file is auto-generated if not present and will bundle the icon and code.

📁 The final `.exe` will be in the `dist/` folder.

---

## 🖼️ Preview

---

## 💬 Notes

- Set `WINDOWER_PATH` and `POL_DIRECTORY` to match your install.
- Ensure `chars2.bin` backups are stored per account.
- OTP support expects a delay (customizable) to give you time to input from your phone.

---

## 📜 License

MIT — Free to use, modify, and expand.

---

## 🔗 Links

📦 [Windower](https://windower.net/)\
📚 [PyQt5 Docs](https://doc.qt.io/qtforpython/)\
🧰 [PyInstaller Docs](https://pyinstaller.org/en/stable/)

---

> _"May your journeys through Vana'diel be swift and smooth."_
