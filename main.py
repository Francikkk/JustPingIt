import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from model.path import AppPaths
from view import MainUI

# ----------------- App Entry -----------------

def main() -> None:
    """
    Entry point for the application.
    This function initializes the PyQt application, sets up the system tray icon,
    and creates the main user interface. It also defines actions for opening the
    main UI and exiting the application.
    The system tray icon is configured with a context menu containing options to
    open the application or exit. Double-clicking the tray icon also opens the
    main UI.
    The application runs until explicitly exited by the user.
    Note:
        Ensure that the required PyQt modules and resources (e.g., icons) are
        available before running this function.
    """
    paths = AppPaths()
    
    app = QApplication(sys.argv)
    app.setApplicationName("JustPingIt")
    app.setApplicationVersion("1.0.0")
    app.setWindowIcon(QIcon(paths.get_icon_path()))

    tray_icon = QSystemTrayIcon(QIcon(paths.get_icon_path()), parent=app)
    tray_menu = QMenu()

    main_ui = MainUI(tray_icon, paths)

    open_action = QAction("Open")
    open_action.triggered.connect(main_ui.show)

    exit_action = QAction("Exit")
    exit_action.triggered.connect(lambda: exit_app(main_ui, tray_icon, app))

    tray_menu.addAction(open_action)
    tray_menu.addSeparator()
    tray_menu.addAction(exit_action)

    tray_icon.setContextMenu(tray_menu)
    tray_icon.activated.connect(lambda reason: main_ui.show() if reason == QSystemTrayIcon.DoubleClick else None)
    tray_icon.show()

    main_ui.show()
    sys.exit(app.exec())


def exit_app(main_ui: MainUI, tray_icon: QSystemTrayIcon, app: QApplication) -> None:
    """
    Gracefully exits the application by performing necessary cleanup operations.

    Args:
        main_ui (MainUI): The main user interface instance, responsible for managing the application's UI.
        tray_icon (QSystemTrayIcon): The system tray icon instance, which will be hidden before exiting.
        app (QApplication): The QApplication instance, representing the running application, which will be terminated.

    Behavior:
        - Hides the system tray icon.
        - Calls the `cleanup` method on the main UI to release resources or save state.
        - Quits the application.
    """
    tray_icon.hide()
    main_ui.cleanup()
    app.quit()


if __name__ == "__main__":
    main()