# ffxi_launcher.py

import sys
import subprocess
import json
import os
import shutil
import time
import psutil
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QHBoxLayout, QLineEdit, QCheckBox, QDialog, QFormLayout, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QIcon

ACCOUNTS_FILE = "accounts.json"
POL_DIRECTORY = "E:/PlayOnline/SquareEnix/PlayOnlineViewer/usr/all"
POL_TEMPLATE_FILE = "chars2.bin"
POL_ACTIVE_FILE = "login_w.bin"
WINDOWER_PATH = "C:/Path/To/Windower4/Windower.exe"
DELAY_BETWEEN_LAUNCHES = 10  # seconds
LOG_FILE = "ffxi_launcher.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

# Auto-generate PyInstaller .spec file if not present
SPEC_TEMPLATE = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['ffxi_launcher.py'],
             pathex=[],
             binaries=[],
             datas=[('ffxi.ico', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='ffxi_launcher',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False, icon='ffxi.ico')
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, upx_exclude=[], name='ffxi_launcher')
'''

if not os.path.exists("ffxi_launcher.spec"):
    with open("ffxi_launcher.spec", "w") as f:
        f.write(SPEC_TEMPLATE)

class AccountEditor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Accounts")
        self.setGeometry(150, 150, 400, 300)
        self.layout = QVBoxLayout()

        self.form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.pol_id_input = QLineEdit()
        self.pol_pass_input = QLineEdit()
        self.se_id_input = QLineEdit()
        self.se_pass_input = QLineEdit()
        self.use_otp_checkbox = QCheckBox("Use One-Time Password")

        self.form_layout.addRow("Account Name:", self.name_input)
        self.form_layout.addRow("POL ID:", self.pol_id_input)
        self.form_layout.addRow("POL Password:", self.pol_pass_input)
        self.form_layout.addRow("SE ID:", self.se_id_input)
        self.form_layout.addRow("SE Password:", self.se_pass_input)
        self.form_layout.addRow(self.use_otp_checkbox)

        self.layout.addLayout(self.form_layout)

        self.save_button = QPushButton("Save Account")
        self.save_button.clicked.connect(self.save_account)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_account(self):
        account = {
            "name": self.name_input.text(),
            "pol_id": self.pol_id_input.text(),
            "pol_pass": self.pol_pass_input.text(),
            "se_id": self.se_id_input.text(),
            "se_pass": self.se_pass_input.text(),
            "use_otp": self.use_otp_checkbox.isChecked()
        }

        if not os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, "w") as f:
                json.dump([], f)

        with open(ACCOUNTS_FILE, "r") as f:
            accounts = json.load(f)

        accounts.append(account)

        with open(ACCOUNTS_FILE, "w") as f:
            json.dump(accounts, f, indent=4)

        self.accept()

class FFXILauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFXI Account Launcher")
        self.setGeometry(100, 100, 500, 600)
        self.setWindowIcon(QIcon("ffxi.ico"))

        self.accounts = self.load_accounts()

        layout = QVBoxLayout()

        self.account_dropdown = QComboBox()
        self.refresh_account_dropdown()
        layout.addWidget(QLabel("Select Account:"))
        layout.addWidget(self.account_dropdown)

        self.otp_checkbox = QCheckBox("Use One-Time Password")
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("Enter OTP if enabled")
        layout.addWidget(self.otp_checkbox)
        layout.addWidget(self.otp_input)

        self.launch_btn = QPushButton("Launch Account")
        self.launch_btn.clicked.connect(self.launch_account)
        layout.addWidget(self.launch_btn)

        self.edit_btn = QPushButton("Edit/Add Accounts")
        self.edit_btn.clicked.connect(self.open_account_editor)
        layout.addWidget(self.edit_btn)

        layout.addWidget(QLabel("Multi-Launch Accounts:"))
        self.account_list = QListWidget()
        self.account_list.setSelectionMode(QListWidget.MultiSelection)
        for acc in self.accounts:
            item = QListWidgetItem(acc["name"])
            self.account_list.addItem(item)
        layout.addWidget(self.account_list)

        self.multi_launch_btn = QPushButton("Launch Selected Accounts")
        self.multi_launch_btn.clicked.connect(self.launch_multiple_accounts)
        layout.addWidget(self.multi_launch_btn)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(QLabel("Log Output:"))
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def log(self, message):
        self.log_output.append(message)
        logging.info(message)

    def load_accounts(self):
        if not os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, "w") as f:
                json.dump([], f)
        with open(ACCOUNTS_FILE, "r") as f:
            return json.load(f)

    def refresh_account_dropdown(self):
        self.account_dropdown.clear()
        self.accounts = self.load_accounts()
        for acc in self.accounts:
            self.account_dropdown.addItem(acc["name"])

    def open_account_editor(self):
        editor = AccountEditor(self)
        if editor.exec_():
            self.refresh_account_dropdown()
            self.account_list.clear()
            for acc in self.accounts:
                self.account_list.addItem(acc["name"])

    def swap_pol_config(self, account_name):
        src_file = os.path.join(POL_DIRECTORY, f"{account_name}_{POL_TEMPLATE_FILE}")
        dst_file = os.path.join(POL_DIRECTORY, POL_ACTIVE_FILE)
        if not os.path.exists(src_file):
            raise FileNotFoundError(f"Missing file for account: {src_file}")
        shutil.copy(src_file, dst_file)
        self.log(f"Swapped POL config: {src_file} -> {dst_file}")

    def is_process_running(self, process_name):
        for proc in psutil.process_iter(['name']):
            if process_name.lower() in proc.info['name'].lower():
                return True
        return False

    def launch_account(self):
        index = self.account_dropdown.currentIndex()
        if index < 0 or index >= len(self.accounts):
            self.log("No valid account selected.")
            return

        account = self.accounts[index]
        use_otp = self.otp_checkbox.isChecked()
        otp = self.otp_input.text().strip()

        self.log(f"Preparing to launch account: {account['name']}")

        try:
            self.swap_pol_config(account['name'])
            subprocess.Popen([WINDOWER_PATH, "--launch", "FFXI"])
            self.log("Launched Windower with selected account.")
        except Exception as e:
            self.log(f"Error launching account: {e}")

    def launch_multiple_accounts(self):
        selected_items = self.account_list.selectedItems()
        if not selected_items:
            self.log("No accounts selected for multi-launch.")
            return

        for item in selected_items:
            name = item.text()
            try:
                self.swap_pol_config(name)
                subprocess.Popen([WINDOWER_PATH, "--launch", "FFXI"])
                self.log(f"Launched Windower with account: {name}")
                self.log("Waiting for game to start and OTP input...")
                time.sleep(DELAY_BETWEEN_LAUNCHES)
            except Exception as e:
                self.log(f"Error launching account {name}: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = FFXILauncher()
    launcher.show()
    sys.exit(app.exec_())
