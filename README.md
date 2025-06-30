# JustPingIt 🖧📶

JustPingIt is a Python-based network utility to ping hosts and log responses over time. It provides a simple interface for network diagnostics and stores data in a local SQLite database.

---

## 🚀 Features

- Ping any IP address or hostname
- GUI interface for ease of use
- Logs ping responses to a local SQLite database
- Exportable logs for network diagnostics
- Lightweight and executable via PyInstaller

---

## 🧱 Project Structure

```
JustPingIt/
│
├── main.py                  # Entry point of the application
├── requirements.txt         # Project dependencies
│
├── model/                   # Business logic and pinging functions
│   ├── ping.py              # Ping implementation
│   ├── pinger.py            # Pinger engine/controller
│   ├── path.py              # Path definitions and utils
│   └── database_logger.py   # DB logging module
│
├── view/                    # GUI logic
│   └── view.py              # GUI frontend
│
├── Data/
    ├── db/
    │   └── ping_log.db      # SQLite database file
    └── img/
        ├── logo_transparent.png
        └── JPI.ico          # App icon

```

---

## 🛠️ How to Run

### 🔧 Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

Then launch the app:

```bash
python main.py
```

---


## 🗃️ Database

SQLite DB is located at:
```
Data/db/ping_log.db
```

You can open it with any SQLite viewer or Python’s `sqlite3`.

---

## 🎨 Icons and Visuals

- App icon: `Data/img/JPI.ico`
- Logo: `Data/img/logo_transparent.png`
- UML Class Diagram: `UML/classes_JustPingIt.png`

---

## 📄 License

[MIT](LICENSE) — Feel free to use, modify, and distribute.

---

## 🙌 Acknowledgements

- Python & Standard Libraries
- PyInstaller for packaging
- Your inspiration to build useful network tools!
