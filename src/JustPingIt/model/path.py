import os
import sys

from PySide6.QtCore import QStandardPaths


class AppPaths:
    """
    A class to manage application paths for resources like icons and databases.
    Attributes:
        dev_mode (bool): Indicates whether the application is running in
        development mode.
        base_path (str): The base path of the application, determined
        dynamically.
        icon_filename (str): The filename of the application icon.
        db_filename (str): The filename of the database file.
    Methods:
        _get_base_path():
            Determines the base path of the application. If running in a
            PyInstaller
            bundle, it uses the `_MEIPASS` attribute; otherwise, it uses the
            directory
            of the current script.
        get_icon_path():
            Constructs and returns the full path to the application icon file.
        get_db_path():
            Constructs and returns the full path to the database file. In
            development
            mode, it uses the base path. In production mode, it uses the
            application
            data directory, creating it if necessary.
    """

    def __init__(self) -> None:
        """
        Initializes the class instance.

        Attributes:
            dev_mode (bool): Indicates whether the application is running in
            development mode.
                             It is set to True if the '_MEIPASS' attribute is
                             not present in the sys module.
            base_path (str): The base path of the application, determined by
            the `_get_base_path` method.
            icon_filename (str): The filename of the application icon, default
            is "JPI.ico".
            db_filename (str): The filename of the database file, default is
            "ping_log.db".
        """
        self.dev_mode = not hasattr(sys, "_MEIPASS")
        self.base_path = self._get_base_path()
        self.icon_filename = "JPI.ico"
        self.db_filename = "ping_log.db"

    def _get_base_path(self) -> str:
        """
        Determines the base path of the application.

        If the application is running as a PyInstaller bundle, it returns the
        temporary folder where the bundled files are extracted (sys._MEIPASS).
        Otherwise, it returns the directory of the current script file.

        Returns:
            str: The base path of the application.
        """
        if hasattr(sys, "_MEIPASS"):
            return sys._MEIPASS  # type: ignore
        else:
            return os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "..")
            )

    def get_icon_path(self) -> str:
        """
        Constructs and returns the full file path to the icon file.

        This method combines the base path and the icon filename to generate
        the complete path to the icon file.

        Returns:
            str: The full file path to the icon file.
        """
        if self.dev_mode:
            return os.path.join(
                self.base_path, "data", "img", self.icon_filename
            )
        else:
            return os.path.join(self.base_path, self.icon_filename)

    def get_db_path(self) -> str:
        """
        Determines the file path for the database based on the current mode.

        If the application is in development mode (`dev_mode` is True), the
        database
        path is constructed using the base path and database filename.
        Otherwise, the
        database path is located in the application's writable AppData
        directory.

        Returns:
            str: The full file path to the database.

        Raises:
            OSError: If the AppData directory cannot be created.
        """
        if self.dev_mode:
            return os.path.join(self.base_path, "data", "db", self.db_filename)
        else:
            app_data = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppDataLocation
            )
            data_folder = os.path.join(app_data, "data")
            os.makedirs(app_data, exist_ok=True)
            os.makedirs(data_folder, exist_ok=True)
            return os.path.join(data_folder, self.db_filename)
