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

        # Main Window
        main_window = QtWidgets.QMainWindow()
        main_window.setWindowTitle(f"GearTrack - Welcome, {user['username']}")
        main_window.setGeometry(100, 100, 1000, 600)
        
        # Central widget and layout
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)

        # Equipment Table
        table = QtWidgets.QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "ID", "Name", "Serial", "In Service", "Condition", "Notes", "Status"
        ])
        table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(table)

        # Toolbar for actions
        toolbar = QtWidgets.QHBoxLayout()
        btn_refresh = QtWidgets.QPushButton("Refresh")
        btn_add = QtWidgets.QPushButton("Add Item")
        toolbar.addWidget(btn_refresh)
        toolbar.addWidget(btn_add)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        central.setLayout(layout)
        main_window.setCentralWidget(central)

        # --- Equipment logic ---
        from src.equipment import add_equipment
        import datetime

        def load_equipment():
            from src.db import get_db
            db = get_db()
            items = db.execute("SELECT * FROM equipment").fetchall()
            table.setRowCount(len(items))
            for row, item in enumerate(items):
                table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(item["id"])))
                table.setItem(row, 1, QtWidgets.QTableWidgetItem(item["name"]))
                table.setItem(row, 2, QtWidgets.QTableWidgetItem(item["serial"]))
                table.setItem(row, 3, QtWidgets.QTableWidgetItem(item["date_in_service"]))
                table.setItem(row, 4, QtWidgets.QTableWidgetItem(item["condition"]))
                table.setItem(row, 5, QtWidgets.QTableWidgetItem(item["notes"]))
                table.setItem(row, 6, QtWidgets.QTableWidgetItem("Available"))
            table.resizeColumnsToContents()

        def add_item():
            dialog = QtWidgets.QDialog(main_window)
            dialog.setWindowTitle("Add Equipment")
            vbox = QtWidgets.QVBoxLayout(dialog)
            name = QtWidgets.QLineEdit()
            name.setPlaceholderText("Item Name")
            serial = QtWidgets.QLineEdit()
            serial.setPlaceholderText("Serial Number")
            date_in_service = QtWidgets.QLineEdit(datetime.date.today().isoformat())
            condition = QtWidgets.QComboBox()
            condition.addItems(["Good", "Worn", "Needs Repair"])
            notes = QtWidgets.QLineEdit()
            notes.setPlaceholderText("Notes")
            ok = QtWidgets.QPushButton("Add")
            ok.clicked.connect(dialog.accept)
            vbox.addWidget(QtWidgets.QLabel("Name:")); vbox.addWidget(name)
            vbox.addWidget(QtWidgets.QLabel("Serial:")); vbox.addWidget(serial)
            vbox.addWidget(QtWidgets.QLabel("Date In Service:")); vbox.addWidget(date_in_service)
            vbox.addWidget(QtWidgets.QLabel("Condition:")); vbox.addWidget(condition)
            vbox.addWidget(QtWidgets.QLabel("Notes:")); vbox.addWidget(notes)
            vbox.addWidget(ok)

            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                add_equipment(
                    name.text(), serial.text(), date_in_service.text(),
                    condition.currentText(), notes.text(), ""
                )
                load_equipment()

        btn_refresh.clicked.connect(load_equipment)
        btn_add.clicked.connect(add_item)

        load_equipment()
        main_window.show()
        sys.exit(app.exec_())

