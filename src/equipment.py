from src.db import get_db

def add_equipment(name, serial, date_in_service, condition, notes, image_path):
    db = get_db()
    db.execute(
        "INSERT INTO equipment (name, serial, date_in_service, condition, notes, image_path) VALUES (?, ?, ?, ?, ?, ?)",
        (name, serial, date_in_service, condition, notes, image_path)
    )
    db.commit()

def update_equipment(id, **fields):
    db = get_db()
    updates = ", ".join([f"{k}=?" for k in fields])
    values = list(fields.values())
    values.append(id)
    db.execute(f"UPDATE equipment SET {updates} WHERE id=?", values)
    db.commit()

def delete_equipment(id):
    db = get_db()
    db.execute("DELETE FROM equipment WHERE id=?", (id,))
    db.commit()
