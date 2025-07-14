from pathlib import Path
from typing import cast
from unittest.mock import ANY, MagicMock, patch

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QSystemTrayIcon
from pytestqt.qtbot import QtBot

from JustPingIt.model.ping import Ping
from JustPingIt.view.view import AboutDialog, LogViewer, MainUI


@pytest.fixture
def mock_paths(tmp_path: Path) -> MagicMock:
    mock_db_path = tmp_path / "mock_db.sqlite"

    mock = MagicMock()
    mock.get_db_path.return_value = str(mock_db_path)
    mock.get_icon_path.return_value = ":/mock/icon.png"
    return mock


@pytest.fixture
def tray_icon() -> MagicMock:
    return MagicMock()


@pytest.fixture
def main_ui(
    qtbot: QtBot, tray_icon: MagicMock, mock_paths: MagicMock
) -> MainUI:
    with (
        patch("src.JustPingIt.model.DatabaseLogger") as MockLogger,
        patch("src.JustPingIt.view.view.LogViewer") as MockLogViewer,
    ):

        MockLogger.return_value = MagicMock()
        MockLogViewer.return_value = MagicMock()
        ui = MainUI(tray_icon, mock_paths)
        qtbot.addWidget(ui)
        return ui


@pytest.fixture
def about_dialog(qtbot: QtBot) -> AboutDialog:
    dialog = AboutDialog()
    qtbot.addWidget(dialog)
    return dialog


@pytest.fixture
def log_viewer(mock_paths: MagicMock) -> tuple[LogViewer, MagicMock]:
    logger_mock = MagicMock()
    viewer = LogViewer(logger_mock, icon_path=mock_paths.get_icon_path())
    return viewer, logger_mock


def test_ui_initialization(main_ui: MainUI) -> None:
    assert main_ui.windowTitle() == "JustPingIt"
    assert main_ui.start_button.text() == "Start"
    assert main_ui.stop_button.text() == "Stop"
    assert not main_ui.stop_button.isEnabled()


def test_load_and_save_settings(main_ui: MainUI) -> None:
    main_ui.ip_input.setText("192.168.1.1")
    main_ui.freq_input.setValue(5)
    main_ui.save_settings()

    settings = QSettings("JustPingIt", "PingApp")
    assert settings.value("ip") == "192.168.1.1"
    assert cast(int, settings.value("frequency")) == 5


@patch("src.JustPingIt.view.view.Pinger")
def test_start_pinging(mock_pinger_class: MagicMock, main_ui: MainUI) -> None:
    mock_pinger = MagicMock()
    mock_pinger_class.return_value = mock_pinger

    main_ui.ip_input.setText("8.8.8.8")
    main_ui.freq_input.setValue(2)
    main_ui.start_pinging()

    assert not main_ui.ip_input.isEnabled()
    assert not main_ui.freq_input.isEnabled()
    assert not main_ui.start_button.isEnabled()
    assert main_ui.stop_button.isEnabled()
    mock_pinger.start.assert_called_once()


@patch("src.JustPingIt.view.view.Pinger")
def test_start_pinging_without_ip(
    mock_pinger_class: MagicMock, main_ui: MainUI
) -> None:
    main_ui.ip_input.setText("")
    main_ui.start_pinging()

    assert "Please enter an IP address." in main_ui.result_display.text()
    assert main_ui.result_display.styleSheet() == "color: orange;"
    mock_pinger_class.assert_not_called()


@patch("src.JustPingIt.view.view.Pinger")
def test_stop_pinging(mock_pinger_class: MagicMock, main_ui: MainUI) -> None:
    mock_pinger = MagicMock()
    mock_pinger_class.return_value = mock_pinger
    main_ui.pinger = mock_pinger

    main_ui.stop_pinging()
    mock_pinger.stop.assert_called_once()
    mock_pinger.wait.assert_called_once()
    assert main_ui.start_button.isEnabled()
    assert not main_ui.stop_button.isEnabled()


def test_display_result_success(main_ui: MainUI) -> None:
    ping = Ping(result="Success", ip_address="192.168.1.1")
    main_ui.display_result(ping)

    assert "Success" in main_ui.result_display.text()
    assert main_ui.result_display.styleSheet() == "color: green;"

    log_viewer_mock = cast(MagicMock, main_ui.log_viewer)
    log_viewer_mock.load_logs.assert_called_once()


def test_display_result_failure(main_ui: MainUI) -> None:
    ping = Ping(result="Timeout", ip_address="192.168.1.1")
    main_ui.display_result(ping)

    assert "Timeout" in main_ui.result_display.text()
    assert main_ui.result_display.styleSheet() == "color: red;"

    log_viewer_mock = cast(MagicMock, main_ui.log_viewer)
    log_viewer_mock.load_logs.assert_called_once()


def test_show_log_viewer(main_ui: MainUI) -> None:
    main_ui.show_log_viewer()

    log_viewer_mock = cast(MagicMock, main_ui.log_viewer)
    log_viewer_mock.load_logs.assert_called_once()
    log_viewer_mock.show.assert_called_once()


def test_close_event_tray_message(main_ui: MainUI) -> None:
    event = MagicMock()
    main_ui.close_event(event)

    event.ignore.assert_called_once()

    tray_icon_mock = cast(MagicMock, main_ui.tray_icon)
    tray_icon_mock.showMessage.assert_called_with(
        "JustPingIt",
        "Application running in the system tray.",
        QSystemTrayIcon.MessageIcon.Information,
    )


def test_cleanup_with_pinger(main_ui: MainUI) -> None:
    main_ui.pinger = MagicMock()
    main_ui.cleanup()

    main_ui.pinger.stop.assert_called_once()
    main_ui.pinger.wait.assert_called_once()

    log_viewer_mock = cast(MagicMock, main_ui.log_viewer)
    log_viewer_mock.close.assert_called_once()


def test_cleanup_without_pinger(main_ui: MainUI) -> None:
    main_ui.pinger = None
    main_ui.cleanup()

    log_viewer_mock = cast(MagicMock, main_ui.log_viewer)
    log_viewer_mock.close.assert_called_once()


def test_about_dialog_show(about_dialog: AboutDialog) -> None:
    with patch.object(AboutDialog, "show") as mock_show:
        about_dialog.show()
        mock_show.assert_called_once()


def test_log_viewer_filters_and_loads_logs(
    qtbot: QtBot, log_viewer: tuple[LogViewer, MagicMock]
) -> None:
    viewer, logger_mock = log_viewer
    qtbot.addWidget(viewer)
    viewer.filter_ip.setText("192.168.1.1")
    viewer.filter_button.click()
    logger_mock.fetch_logs.assert_called_with(
        ip_filter="192.168.1.1",
        result_filter="",
        from_date=ANY,
        to_date=ANY,
    )
