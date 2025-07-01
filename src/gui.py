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
        
        # Status and action buttons
        action_widget = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(action_widget)
        btn_check = QtWidgets.QPushButton("Check-Out")
        btn_img = QtWidgets.QPushButton("Image")
        btn_bar = QtWidgets.QPushButton("Barcode")
        h.addWidget(btn_check)
        h.addWidget(btn_img)
        h.addWidget(btn_bar)
        h.setContentsMargins(0,0,0,0)
        action_widget.setLayout(h)
        table.setCellWidget(row, 6, action_widget)

        # Connect actions
        def make_check_fn(equip_id=item["id"]):
            def fn():
                # In real app: log user and timestamp
                from src.db import get_db
                db = get_db()
                db.execute(
                    "INSERT INTO logs (equipment_id, user_id, action, timestamp, note) VALUES (?, ?, ?, datetime('now'), ?)",
                    (equip_id, user["id"], "checked-out", "")
                )
                db.commit()
                QtWidgets.QMessageBox.information(main_window, "Checked Out", "Item checked out!")
                load_equipment()
            return fn

        btn_check.clicked.connect(make_check_fn())

        def make_img_fn(equip_id=item["id"]):
            def fn():
                # Select and save image file path
                file, _ = QtWidgets.QFileDialog.getOpenFileName(main_window, "Select Image")
                if file:
                    db = get_db()
                    db.execute("UPDATE equipment SET image_path=? WHERE id=?", (file, equip_id))
                    db.commit()
                    QtWidgets.QMessageBox.information(main_window, "Image Added", "Image attached to item.")
            return fn

        btn_img.clicked.connect(make_img_fn())

        def make_bar_fn(equip=item):
            def fn():
                # Show dialog to select barcode type and generate/preview
                dlg = QtWidgets.QDialog(main_window)
                dlg.setWindowTitle("Generate Barcode/QR")
                v = QtWidgets.QVBoxLayout(dlg)
                typebox = QtWidgets.QComboBox()
                typebox.addItems(["Code128", "QR"])
                btn_gen = QtWidgets.QPushButton("Generate")
                img_label = QtWidgets.QLabel()
                v.addWidget(QtWidgets.QLabel("Type:")); v.addWidget(typebox)
                v.addWidget(btn_gen); v.addWidget(img_label)
                def gen():
                    import tempfile, os
                    data = f"{equip['name']} | {equip['serial']} | {equip['date_in_service']} | {equip['condition']} | {equip['notes']}"
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                    tmp.close()
                    if typebox.currentText() == "Code128":
                        from src.barcode_utils import generate_code128
                        generate_code128(data, tmp.name)
                    else:
                        from src.barcode_utils import generate_qr
                        generate_qr(data, tmp.name)
                    img = QtGui.QPixmap(tmp.name)
                    img_label.setPixmap(img.scaled(250, 80 if typebox.currentText()=="Code128" else 250))
                    os.unlink(tmp.name)
                btn_gen.clicked.connect(gen)
                dlg.exec_()
            return fn

        btn_bar.clicked.connect(make_bar_fn())

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

