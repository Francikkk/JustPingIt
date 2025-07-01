import os
import csv
import markdown
from PySide6.QtCore import Qt, QSettings, QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextBrowser,
    QLineEdit, QSpinBox, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QDateEdit, QComboBox, QHeaderView, QSystemTrayIcon, QMenu, QMessageBox,
    QFileDialog, QMainWindow, QDialog, QTextEdit, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QIcon, QAction
from JustPingIt.model.database_logger import DatabaseLogger
from JustPingIt.model.pinger import Pinger, Ping
from JustPingIt.model.path import AppPaths


class AboutDialog(QDialog):
    """
    A dialog window that displays information about the JustPingIt application.
    This dialog provides details such as the application's name, author, version,
    license, GitHub repository, website, and contact information. It also includes
    a button to close the dialog.
    Attributes:
        parent (QWidget, optional): The parent widget of the dialog. Defaults to None.
    Methods:
        __init__(parent=None):
            Initializes the AboutDialog with the specified parent widget.
    """
    def __init__(self, parent=None) -> None:
        """
        Initializes the About dialog for the JustPingIt application.
        This dialog displays information about the application, including
        the author, version, license, GitHub repository, website, and contact details.
        It also provides an "OK" button to close the dialog.
        Args:
            parent (QWidget, optional): The parent widget of the dialog. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("About JustPingIt")
        self.setMinimumSize(500, 600)

# Testo markdown (potresti anche leggere da un file README.md)
        md_text = """

<img src="./data/img/logo_transparent.png" width="150" />

---
## JustPingIt V1.0.0
JustPingIt is a Python-based network utility to ping hosts and log responses over time. 
It provides a simple and effective GUI interface for network diagnostics and stores data in a local SQLite database.

---

## 🤝 Contributing

Got ideas? Bugs? Wanna collab? Just ping me back!

---

## 📬 Contact

[gestione.franci@gmail.com](mailto:gestione.franci@gmail.com)

## 💻 GitHub

[https://github.com/Francikkk/JustPingIt](https://github.com/Francikkk/JustPingIt)

## 🚀 Features

- Ping any IP address or hostname
- GUI interface for ease of use
- Background pinging operation for long-term test
- Logs ping responses to a local SQLite database
- Exportable logs for network diagnostics
- Lightweight and executable via PyInstaller

---

## 🗃️ Database

All ping results are logged into a handy SQLite database stored locally.

Want to peek inside? Fire up any SQLite viewer or just use Python’s built-in sqlite3 module.

---

## 📄 License

[MIT](LICENSE) — Feel free to use, modify, and distribute.

---

## 🙌 Acknowledgements

- Python & Standard Libraries
- PyInstaller for packaging
- PySide6 for GUI
- Your inspiration to build useful network tools!
---
"""

        html = markdown.markdown(md_text)
        text_browser = QTextBrowser()
        text_browser.setHtml(html)
        text_browser.setOpenExternalLinks(True)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        
        layout = QVBoxLayout(self)
        layout.addWidget(text_browser)
        layout.addWidget(ok_btn)


class LogViewer(QWidget):
    """
    LogViewer is a QWidget-based class that provides a graphical interface for viewing, filtering, 
    exporting, and deleting logs stored in a database.
    Attributes:
        logger (DatabaseLogger): An instance of the logger used to fetch and manage log entries.
        layout (QVBoxLayout): The main layout of the widget.
        filter_ip (QLineEdit): Input field for filtering logs by IP address.
        filter_result (QComboBox): Dropdown for filtering logs by result (e.g., "Success", "Failure").
        filter_from (QDateEdit): Date picker for specifying the start date of the filter range.
        filter_to (QDateEdit): Date picker for specifying the end date of the filter range.
        filter_button (QPushButton): Button to apply the selected filters.
        log_table (QTableWidget): Table widget for displaying the filtered logs.
        export_button (QPushButton): Button to export the displayed logs to a file.
        delete_button (QPushButton): Button to delete the displayed logs from the database.
        current_logs (list): A list of logs currently displayed in the table.
    Methods:
        __init__(logger: DatabaseLogger, icon_path: str = None):
            Initializes the LogViewer widget with the specified logger and optional icon.
        init_ui():
            Sets up the user interface, including filters, log table, and action buttons.
        load_logs():
            Loads logs from the database based on the current filter settings and displays them in the table.
        export_logs():
            Exports the currently displayed logs to a CSV or text file.
        delete_logs():
            Deletes the currently displayed logs from the database after user confirmation.
    """
    def __init__(self, logger: DatabaseLogger, icon_path: str = None) -> None:
        """
        Initializes the Pinger window.
        Args:
            logger (DatabaseLogger): The logger instance used for logging ping data.
            icon_path (str, optional): The file path to the window icon. If provided and the file exists, 
                                       it will be set as the window's icon. Defaults to None.
        """
        super().__init__()
        self.setWindowFlag(Qt.Tool)
        self.logger = logger
        self.setWindowTitle("Ping Logs")
        self.setMinimumSize(600, 400)
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.layout = QVBoxLayout(self)
        self.init_ui()

    def init_ui(self) -> None:
        """
        Initializes the user interface for the application.
        This method sets up the layout and widgets for filtering logs, displaying log data,
        and providing options to export or delete logs. It includes the following components:
        - Filter Section:
            - A QLineEdit for filtering logs by IP address.
            - A QComboBox for filtering logs by result ("All", "Success", "Failure").
            - Two QDateEdit widgets for specifying a date range (from and to).
            - A QPushButton to apply the filters.
        - Log Table:
            - A QTableWidget to display log entries with three columns: "Result", "Timestamp", and "IP Address".
            - The table is non-editable and allows row selection.
            - The header sections are set to stretch for better visibility.
        - Bottom Buttons:
            - A QPushButton for exporting logs.
            - A QPushButton for deleting logs.
            - A spacer to align the buttons to the right.
        Signal Connections:
            - The filter button is connected to the `load_logs` method to apply filters.
            - The export button is connected to the `export_logs` method to export log data.
            - The delete button is connected to the `delete_logs` method to delete selected logs.
        """
        filter_layout = QHBoxLayout()
        self.filter_ip = QLineEdit()
        self.filter_ip.setPlaceholderText("Filter by IP")

        self.filter_result = QComboBox()
        self.filter_result.addItem("All")
        self.filter_result.addItems(["Success", "Failure"])

        self.filter_from = QDateEdit()
        self.filter_from.setCalendarPopup(True)
        self.filter_from.setDate(QDate.currentDate().addDays(-7))

        self.filter_to = QDateEdit()
        self.filter_to.setCalendarPopup(True)
        self.filter_to.setDate(QDate.currentDate())

        self.filter_button = QPushButton("Apply")

        filter_layout.addWidget(self.filter_ip)
        filter_layout.addWidget(self.filter_result)
        filter_layout.addWidget(self.filter_from)
        filter_layout.addWidget(self.filter_to)
        filter_layout.addWidget(self.filter_button)

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(3)
        self.log_table.setHorizontalHeaderLabels(["Result", "Timestamp", "IP Address"])
        self.log_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.log_table.setSelectionBehavior(QTableWidget.SelectRows)
        header = self.log_table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(3):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        self.log_table.verticalHeader().setVisible(False)

        self.layout.addLayout(filter_layout)
        self.layout.addWidget(self.log_table)

        # New horizontal layout for buttons at the bottom
        button_layout = QHBoxLayout()
        self.export_button = QPushButton("Export")
        self.delete_button = QPushButton("Delete")

        # Spacer to push buttons to the right
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addItem(spacer)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.delete_button)

        self.layout.addLayout(button_layout)

        self.filter_button.clicked.connect(self.load_logs)
        self.export_button.clicked.connect(self.export_logs)
        self.delete_button.clicked.connect(self.delete_logs)

    def load_logs(self) -> None:
        """
        Loads logs from the logger based on the specified filters and populates the log table.
        Filters:
            - IP address: Retrieved from the `filter_ip` text input.
            - Result: Retrieved from the `filter_result` dropdown. If "All" is selected, no filter is applied.
            - Date range: Retrieved from the `filter_from` and `filter_to` date inputs.
        The method fetches logs from the logger using the specified filters and updates the `log_table` widget
        with the retrieved data. Each log entry is displayed in a row, excluding the ID column.
        Steps:
            1. Retrieve filter values from the UI components.
            2. Fetch logs from the logger using the filters.
            3. Populate the `log_table` with the fetched logs.
        Note:
            - The ID column (row[0]) is skipped when populating the table to avoid displaying it.
        """
        ip = self.filter_ip.text().strip()
        result = self.filter_result.currentText()
        result = "" if result == "All" else result
        from_date = self.filter_from.date().toPython()
        to_date = self.filter_to.date().toPython()
        self.current_logs = self.logger.fetch_logs(ip_filter=ip, result_filter=result, from_date=from_date, to_date=to_date)

        self.log_table.setRowCount(len(self.current_logs))
        for row_idx, row in enumerate(self.current_logs):
            for col_idx, value in enumerate(row[1:]):  # Skip ID (row[0]) to avoid index in rapresentation
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.log_table.setItem(row_idx, col_idx, item)

    def export_logs(self) -> None:
        """
        Exports the current logs to a file selected by the user.

        This method allows the user to save the current logs to a file in either
        CSV or plain text format. The user is prompted to select the file location
        and name through a file dialog. If the user cancels the dialog or no logs
        are available, the method exits without performing any action.

        The exported file contains a header row with the following columns:
        - "Result"
        - "Timestamp"
        - "IP Address"

        Each subsequent row corresponds to a log entry, excluding the ID field.

        Raises:
            Exception: If an error occurs while writing to the file, a critical
            message box is displayed with the error details.
        """
        if not self.current_logs:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Logs", "", "CSV Files (*.csv);;Text Files (*.txt)")
        if not file_path:
            return
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Result", "Timestamp", "IP Address"])
                for row in self.current_logs:
                    writer.writerow(row[1:])  # Skip ID
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def delete_logs(self) -> None:
        """
        Deletes the current log entries after user confirmation.

        If there are no current logs, the method returns immediately.
        Otherwise, it prompts the user with a confirmation dialog to delete
        the specified number of log entries. If the user confirms, the logs
        are deleted by their IDs, and the log list is reloaded.

        Raises:
            None

        Returns:
            None
        """
        if not self.current_logs:
            return
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {len(self.current_logs)} log entries?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ids_to_delete = [row[0] for row in self.current_logs]
            self.logger.delete_logs_by_ids(ids_to_delete)
            self.load_logs()


class MainUI(QMainWindow):
    """
    MainUI is the primary user interface class for the JustPingIt application. It provides
    a graphical interface for users to configure and start/stop pinging operations, view logs,
    and access application settings.
    Attributes:
        paths (AppPaths): An instance of AppPaths to manage application paths.
        settings (QSettings): Stores and retrieves application settings.
        logger (DatabaseLogger): Handles logging of ping results to a database.
        pinger (Pinger): The thread responsible for performing ping operations.
        tray_icon (QSystemTrayIcon): The system tray icon for the application.
        log_viewer (LogViewer): A dialog for viewing the ping logs.
        ip_input (QLineEdit): Input field for the IP address to ping.
        freq_input (QSpinBox): Input field for the ping frequency in seconds.
        start_button (QPushButton): Button to start the pinging process.
        stop_button (QPushButton): Button to stop the pinging process.
        view_logs_button (QPushButton): Button to open the log viewer.
        result_display (QLabel): Displays the result of the latest ping operation.
    Methods:
        __init__(tray_icon: QSystemTrayIcon, app_paths: AppPaths):
            Initializes the MainUI instance with the given tray icon and application paths.
        init_ui():
            Sets up the user interface components and layout.
        show_about_dialog():
            Displays the About dialog with application information.
        load_settings():
            Loads the saved IP address and ping frequency from application settings.
        save_settings():
            Saves the current IP address and ping frequency to application settings.
        start_pinging():
            Starts the pinging process with the specified IP address and frequency.
        stop_pinging():
            Stops the ongoing pinging process.
        display_result(ping: Ping):
            Updates the result display with the latest ping result and refreshes the log viewer if visible.
        show_log_viewer():
            Loads and displays the log viewer dialog.
        closeEvent(event):
            Overrides the close event to minimize the application to the system tray instead of exiting.
        cleanup():
            Cleans up resources, stops the pinger thread, and closes the log viewer.
    """
    def __init__(self, tray_icon: QSystemTrayIcon, app_paths: AppPaths) -> None:
        """
        Initializes the main application window and its components.
        Args:
            tray_icon (QSystemTrayIcon): The system tray icon for the application.
            app_paths (AppPaths): An object containing application paths for resources.
        Attributes:
            paths (AppPaths): Stores the application paths.
            settings (QSettings): Manages application settings.
            logger (DatabaseLogger): Handles logging to a database.
            pinger (None): Placeholder for the pinger functionality (to be initialized later).
            tray_icon (QSystemTrayIcon): The system tray icon for the application.
            log_viewer (LogViewer): A viewer for displaying logs.
        """
        super().__init__()
        self.paths = app_paths
        self.settings = QSettings("JustPingIt", "PingApp")
        self.logger = DatabaseLogger(self.paths.get_db_path())
        self.pinger = None
        self.tray_icon = tray_icon
        self.log_viewer = LogViewer(self.logger, icon_path=self.paths.get_icon_path())

        self.setWindowIcon(QIcon(self.paths.get_icon_path()))
        self.setWindowTitle("JustPingIt")
        self.setFixedSize(300, 230)

        self.init_ui()
        self.load_settings()

    def init_ui(self) -> None:
        """
        Initializes the user interface for the application.
        This method sets up the main window layout, including the menu bar, input fields,
        buttons, and labels. It also connects button actions to their respective methods.
        UI Components:
        - Menu Bar:
            - Help menu with an "About" action.
        - Central Widget:
            - Input fields for IP Address and Ping Rate (in seconds).
            - Start and Stop buttons for controlling the pinging process.
            - A button to view logs.
            - A label to display results or messages.
        Button Actions:
        - `Start` button: Starts the pinging process.
        - `Stop` button: Stops the pinging process.
        - `View Logs` button: Opens the log viewer.
        Note:
        - The "Stop" button is initially disabled and becomes enabled when the pinging process starts.
        """
        menu_bar = self.menuBar()

        # Spacer to push the Help menu to the right
        menu_bar.setCornerWidget(QWidget(), Qt.TopLeftCorner)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        menu_bar.setCornerWidget(spacer, Qt.TopRightCorner)

        help_menu = QMenu("Help", self)
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        menu_bar.addMenu(help_menu)

        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("IP Address:"))
        self.ip_input = QLineEdit()
        layout.addWidget(self.ip_input)

        layout.addWidget(QLabel("Ping Rate (seconds):"))
        self.freq_input = QSpinBox()
        self.freq_input.setMinimum(1)
        layout.addWidget(self.freq_input)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

        self.view_logs_button = QPushButton("View Logs")
        layout.addWidget(self.view_logs_button)

        self.result_display = QLabel(" ")
        layout.addWidget(self.result_display)

        self.start_button.clicked.connect(self.start_pinging)
        self.stop_button.clicked.connect(self.stop_pinging)
        self.view_logs_button.clicked.connect(self.show_log_viewer)

    def show_about_dialog(self) -> None:
        """
        Displays the "About" dialog for the application.

        This method creates an instance of the AboutDialog class, passing the
        current object as its parent, and executes it as a modal dialog.

        Returns:
            None
        """
        AboutDialog(self).exec()

    def load_settings(self) -> None:
        """
        Load application settings and update the input fields with stored values.

        This method retrieves the saved IP address and frequency values from the
        application's settings storage and populates the corresponding input fields
        in the user interface.

        - The IP address is set in the `ip_input` field.
        - The frequency value is set in the `freq_input` field, defaulting to 1 if
          no value is stored.

        """
        self.ip_input.setText(self.settings.value("ip", ""))
        self.freq_input.setValue(int(self.settings.value("frequency", 1)))

    def save_settings(self) -> None:
        """
        Saves the current settings for IP address and frequency.

        This method retrieves the values from the input fields for the IP address
        and frequency, processes them (e.g., strips whitespace from the IP address),
        and stores them persistently using the settings object.

        The following settings are saved:
        - "ip": The IP address entered in the ip_input field.
        - "frequency": The frequency value entered in the freq_input field.
        """
        self.settings.setValue("ip", self.ip_input.text().strip())
        self.settings.setValue("frequency", self.freq_input.value())

    def start_pinging(self) -> None:
        """
        Starts the pinging process with the specified IP address and frequency.

        This method retrieves the IP address and frequency from the user inputs,
        validates the IP address, and initializes a Pinger object to perform the
        pinging operation. It also updates the UI elements to reflect the current
        state of the application.

        Steps:
        1. Retrieves and validates the IP address from the input field.
        2. Saves the current settings.
        3. Stops any existing Pinger instance if running.
        4. Creates a new Pinger instance with the provided IP address and frequency.
        5. Connects the Pinger's signal to the result display method.
        6. Starts the Pinger thread.
        7. Updates the UI to disable inputs and enable the stop button.

        Returns:
            None
        """
        ip_address = self.ip_input.text().strip()
        frequency = self.freq_input.value()
        if not ip_address:
            self.result_display.setText("Please enter an IP address.")
            self.result_display.setStyleSheet("color: orange;")
            return
        self.save_settings()
        if self.pinger:
            self.pinger.stop()
            self.pinger.wait()
        self.pinger = Pinger(ip_address, frequency, self.logger)
        self.pinger.ping_signal.connect(self.display_result)
        self.pinger.start()
        self.ip_input.setEnabled(False)
        self.freq_input.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_pinging(self) -> None:
        """
        Stops the ongoing pinging process and resets the UI elements.

        This method checks if a pinging process is currently active. If so, it stops
        the process, waits for it to terminate, and cleans up the associated resources.
        Additionally, it re-enables the input fields and the start button while disabling
        the stop button to reset the user interface to its initial state.
        """
        if self.pinger:
            self.pinger.stop()
            self.pinger.wait()
            self.pinger = None
        self.ip_input.setEnabled(True)
        self.freq_input.setEnabled(True)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def display_result(self, ping: Ping) -> None:
        """
        Updates the result display with the outcome of a ping operation and refreshes the log viewer if visible.

        Args:
            ping (Ping): An instance of the Ping class containing the result and timestamp of the ping operation.

        Behavior:
            - Sets the text color of the result display to green if the ping was successful, otherwise red.
            - Updates the result display with the ping result and timestamp.
            - If the log viewer is visible, reloads the logs in the log viewer.
        """
        color = "green" if ping.result == "Success" else "red"
        self.result_display.setStyleSheet(f"color: {color};")
        self.result_display.setText(f"{ping.result} at {ping.timestamp}")
        if self.log_viewer.isVisible():
            self.log_viewer.load_logs()

    def show_log_viewer(self) -> None:
        """
        Displays the log viewer by loading the logs and making the viewer visible.

        This method first loads the logs into the log viewer and then displays
        the log viewer window to the user.
        """
        self.log_viewer.load_logs()
        self.log_viewer.show()

    def closeEvent(self, event) -> None:
        """
        Handles the close event of the application window.

        Overrides the default close event to prevent the application from exiting
        when the window is closed. Instead, the application is hidden and a 
        notification is displayed in the system tray to inform the user that the 
        application is still running in the background.

        Args:
            event (QCloseEvent): The close event triggered when the user attempts 
            to close the application window.
        """
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "JustPingIt",
            "Application running in the system tray.",
            QSystemTrayIcon.Information
        )

    def cleanup(self) -> None:
        """
        Perform cleanup operations for the application.

        This method stops the pinger process if it is running, waits for it to terminate,
        closes the log viewer, and then closes the main application window.
        """
        if self.pinger:
            self.pinger.stop()
            self.pinger.wait()
        self.log_viewer.close()
        self.close()