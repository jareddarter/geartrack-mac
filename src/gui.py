import sys
import datetime
import tempfile
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from src.db import init_db, get_db
from src.user import verify_user, create_user
from src.equipment import add_equipment
from src.barcode_utils import generate_code128, generate_qr

INACTIVITY_TIMEOUT = 15 * 60 * 1000  # 15 minutes in ms

class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - GearTrack")
        self.setModal(True)
        self.resize(350, 160)
        layout = QtWidgets.QVBoxLayout(self)

        self.user_field = QtWidgets.QLineEdit()
        self.user_field.setPlaceholderText("Username")
        self.pass_field = QtWidgets.QLineEdit()
        self.pass_field.setPlaceholderText("Password")
        self.pass_field.setEchoMode(QtWidgets.QLineEdit.Password)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setStyleSheet("color: red;")

        btn_login = QtWidgets.QPushButton("Login")
        btn_login.clicked.connect(self.try_login)

        layout.addWidget(QtWidgets.QLabel("Username:"))
        layout.addWidget(self.user_field)
        layout.addWidget(QtWidgets.QLabel("Password:"))
        layout.addWidget(self.pass_field)
        layout.addWidget(btn_login)
        layout.addWidget(self.status_label)

        self.user = None

    def try_login(self):
        username = self.user_field.text()
        password = self.pass_field.text()
        user = verify_user(username, password)
        if user:
            self.user = user
            self.accept()
        else:
            self.status_label.setText("Invalid login.")

def run_app():
    app = QtWidgets.QApplication(sys.argv)
    init_db()

    # Prepopulate default admin if not exists
    try:
        create_user("admin", "admin123", True)
    except Exception:
        pass  # user already exists

    login = LoginDialog()
    if login.exec_() == QtWidgets.QDialog.Accepted:
        user = login.user

        main_window = QtWidgets.QMainWindow()
        main_window.setWindowTitle(f"GearTrack - Welcome, {user['username']}")
        main_window.setGeometry(100, 100, 1100, 650)

        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)

        # Search/filter bar
        search_layout = QtWidgets.QHBoxLayout()
        search_field = QtWidgets.QLineEdit()
        search_field.setPlaceholderText("Search by name, serial, condition...")
        search_layout.addWidget(QtWidgets.QLabel("Search:"))
        search_layout.addWidget(search_field)
        layout.addLayout(search_layout)

        # Equipment Table
        table = QtWidgets.QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "ID", "Name", "Serial", "In Service", "Condition", "Notes", "Status", "Actions"
        ])
        table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(table)

        # Toolbar for actions
        toolbar = QtWidgets.QHBoxLayout()
        btn_refresh = QtWidgets.QPushButton("Refresh")
        btn_add = QtWidgets.QPushButton("Add Item")
        btn_export_csv = QtWidgets.QPushButton("Export CSV")
        btn_export_pdf = QtWidgets.QPushButton("Export PDF")
        toolbar.addWidget(btn_refresh)
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_export_csv)
        toolbar.addWidget(btn_export_pdf)

        # Admin
