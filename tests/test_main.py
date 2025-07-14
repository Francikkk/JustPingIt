# test_main.py

import sys
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest


# Patch QApplication instance to prevent real GUI loop
@pytest.fixture
def mock_qt(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[dict[str, MagicMock], None, None]:
    mock_app = MagicMock()
    mock_tray_icon = MagicMock()
    mock_menu = MagicMock()
    mock_action = MagicMock()
    mock_icon = MagicMock()
    mock_main_ui = MagicMock()

    monkeypatch.setitem(sys.modules, "PySide6.QtWidgets", MagicMock())
    monkeypatch.setitem(sys.modules, "PySide6.QtGui", MagicMock())

    with (
        patch(
            "PySide6.QtWidgets.QApplication", return_value=mock_app
        ) as mock_app_cls,
        patch(
            "PySide6.QtWidgets.QSystemTrayIcon", return_value=mock_tray_icon
        ) as mock_tray_cls,
        patch(
            "PySide6.QtWidgets.QMenu", return_value=mock_menu
        ) as mock_menu_cls,
        patch(
            "PySide6.QtGui.QAction", return_value=mock_action
        ) as mock_action_cls,
        patch("PySide6.QtGui.QIcon", return_value=mock_icon) as mock_icon_cls,
        patch(
            "JustPingIt.view.MainUI", return_value=mock_main_ui
        ) as mock_ui_cls,
        patch("JustPingIt.model.path.AppPaths") as mock_paths_cls,
    ):

        mock_paths = MagicMock()
        mock_paths.get_icon_path.return_value = "dummy/icon/path"
        mock_paths_cls.return_value = mock_paths

        yield {
            "app": mock_app,
            "tray_icon": mock_tray_icon,
            "menu": mock_menu,
            "action": mock_action,
            "icon": mock_icon,
            "main_ui": mock_main_ui,
            "app_cls": mock_app_cls,
            "tray_cls": mock_tray_cls,
            "menu_cls": mock_menu_cls,
            "action_cls": mock_action_cls,
            "icon_cls": mock_icon_cls,
            "paths_cls": mock_paths_cls,
        }


def test_main_runs_properly(mock_qt: dict[str, MagicMock]) -> None:
    # Import main after mocking
    from JustPingIt.main import main

    with patch("sys.exit") as mock_exit:
        main()

    # Check QApplication and tray were set up correctly
    mock_qt["app"].setApplicationName.assert_called_once_with("JustPingIt")
    mock_qt["app"].setApplicationVersion.assert_called_once_with("1.0.0")
    mock_qt["app"].setWindowIcon.assert_called_once()
    mock_qt["tray_icon"].setContextMenu.assert_called_once_with(
        mock_qt["menu"]
    )
    mock_qt["tray_icon"].show.assert_called_once()
    mock_qt["main_ui"].show.assert_called()
    mock_exit.assert_called_once()


def test_exit_app_behavior(mock_qt: dict[str, MagicMock]) -> None:
    from JustPingIt.main import exit_app

    # Call exit_app directly
    exit_app(mock_qt["main_ui"], mock_qt["tray_icon"], mock_qt["app"])

    mock_qt["tray_icon"].hide.assert_called_once()
    mock_qt["main_ui"].cleanup.assert_called_once()
    mock_qt["app"].quit.assert_called_once()
