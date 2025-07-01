import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from src.db import init_db
from src.user import verify_user

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
    from src.user import create_user
    try:
        create_user("admin", "admin123", True)
    except Exception:
        pass  # user already exists

    login = LoginDialog()
    if login.exec_() == QtWidgets.QDialog.Accepted:
        user = login.user
        main_window = QtWidgets.QMainWindow()
        main_window.setWindowTitle(f"GearTrack - Welcome, {user['username']}")
        main_window.setGeometry(100, 100, 900, 600)
        label = QtWidgets.QLabel(f"Hello, {user['username']}! (UI implementation goes here.)", main_window)
        label.move(50, 50)
        main_window.show()
        sys.exit(app.exec_())
