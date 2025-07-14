import os
import sys
from unittest import mock

import pytest

from JustPingIt.model.path import AppPaths


@pytest.fixture
def base_path() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def test_dev_mode_true(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test AppPaths in development mode (no _MEIPASS)."""
    monkeypatch.delenv("_MEIPASS", raising=False)
    app_paths = AppPaths()

    assert app_paths.dev_mode is True
    assert "JustPingIt" in app_paths.base_path or os.path.exists(
        app_paths.base_path
    )
    assert app_paths.icon_filename == "JPI.ico"
    assert app_paths.db_filename == "ping_log.db"


def test_dev_mode_false(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test AppPaths in production mode (PyInstaller bundle)."""
    monkeypatch.setattr(sys, "_MEIPASS", "/fake/bundle/path", raising=False)
    app_paths = AppPaths()

    assert app_paths.dev_mode is False
    assert app_paths.base_path == "/fake/bundle/path"


def test_get_icon_path_dev(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test icon path in development mode."""
    monkeypatch.delenv("_MEIPASS", raising=False)
    app_paths = AppPaths()
    expected = os.path.join(app_paths.base_path, "data", "img", "JPI.ico")
    assert app_paths.get_icon_path() == expected


def test_get_icon_path_prod(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test icon path in production mode."""
    monkeypatch.setattr(sys, "_MEIPASS", "/prod/path", raising=False)
    app_paths = AppPaths()
    expected = os.path.join("/prod/path", "JPI.ico")
    assert app_paths.get_icon_path() == expected


@mock.patch("src.JustPingIt.model.path.QStandardPaths.writableLocation")
@mock.patch("os.makedirs")
def test_get_db_path_dev(
    mock_makedirs: mock.MagicMock,
    mock_qpaths: mock.MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test DB path in development mode."""
    monkeypatch.delenv("_MEIPASS", raising=False)
    app_paths = AppPaths()
    expected = os.path.join(app_paths.base_path, "data", "db", "ping_log.db")
    result = app_paths.get_db_path()

    assert result == expected
    mock_makedirs.assert_not_called()
    mock_qpaths.assert_not_called()


@mock.patch("src.JustPingIt.model.path.QStandardPaths.writableLocation")
@mock.patch("os.makedirs")
def test_get_db_path_prod(
    mock_makedirs: mock.MagicMock,
    mock_qpaths: mock.MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test DB path in production mode with writable app data location."""
    monkeypatch.setattr(sys, "_MEIPASS", "/prod/path", raising=False)
    mock_qpaths.return_value = "/mock/appdata"

    app_paths = AppPaths()
    db_path = app_paths.get_db_path()

    expected_path = os.path.join("/mock/appdata", "data", "ping_log.db")
    assert db_path == expected_path

    mock_makedirs.assert_any_call("/mock/appdata", exist_ok=True)
    mock_makedirs.assert_any_call(
        os.path.join("/mock/appdata", "data"), exist_ok=True
    )
    assert mock_qpaths.called


def test_get_base_path_dev(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test base path returned in dev mode (no _MEIPASS)."""
    monkeypatch.delenv("_MEIPASS", raising=False)
    app_paths = AppPaths()
    base_path = app_paths._get_base_path()

    assert os.path.basename(base_path) != "_MEIPASS"
