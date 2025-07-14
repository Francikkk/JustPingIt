import subprocess
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from JustPingIt.model.ping import Ping
from JustPingIt.model.pinger import Pinger


@pytest.fixture
def mock_logger() -> MagicMock:
    return MagicMock()


@pytest.fixture
def pinger_instance(mock_logger: MagicMock) -> Pinger:
    return Pinger(ip_address="192.168.1.1", frequency=1, logger=mock_logger)


@patch("JustPingIt.model.pinger.subprocess.check_output")
def test_ping_host_success_unix(
    mock_check_output: MagicMock, pinger_instance: Pinger
) -> None:
    mock_check_output.return_value = (
        b"bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.123 ms"
    )
    result = pinger_instance.ping_host("192.168.1.1")
    assert result == "Success"


@patch("JustPingIt.model.pinger.subprocess.check_output")
def test_ping_host_failure_unreachable(
    mock_check_output: MagicMock, pinger_instance: Pinger
) -> None:
    mock_check_output.return_value = b"Destination Host Unreachable"
    result = pinger_instance.ping_host("192.168.1.1")
    assert result == "Failure"


@patch(
    "JustPingIt.model.pinger.subprocess.check_output",
    side_effect=subprocess.CalledProcessError(1, "ping"),
)
def test_ping_host_called_process_error(
    mock_check_output: MagicMock, pinger_instance: Pinger
) -> None:
    result = pinger_instance.ping_host("192.168.1.1")
    assert result == "Failure"


@patch(
    "JustPingIt.model.pinger.subprocess.check_output",
    side_effect=subprocess.TimeoutExpired("ping", 3),
)
def test_ping_host_timeout(
    mock_check_output: MagicMock, pinger_instance: Pinger
) -> None:
    result = pinger_instance.ping_host("192.168.1.1")
    assert result == "Failure"


@patch(
    "JustPingIt.model.pinger.subprocess.check_output",
    side_effect=Exception("Unexpected"),
)
def test_ping_host_unexpected_error(
    mock_check_output: MagicMock,
    pinger_instance: Pinger,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = pinger_instance.ping_host("192.168.1.1")
    assert result == "Failure"
    captured = capsys.readouterr()
    assert "Unexpected error during ping" in captured.out


def test_stop_stops_thread(pinger_instance: Pinger) -> None:
    pinger_instance._is_running = True
    pinger_instance.stop()
    assert not pinger_instance._is_running


def test_run_emits_signal_and_logs(qtbot: Any, mock_logger: MagicMock) -> None:
    ip_address = "192.168.1.1"
    frequency = 1

    # Create a test Pinger object
    pinger = Pinger(ip_address, frequency, mock_logger)

    # Patch ping_host to stop after first call
    def one_ping_then_stop(*args: Any, **kwargs: Any) -> str:
        pinger.stop()
        return "Success"

    pinger.ping_host = MagicMock(side_effect=one_ping_then_stop)

    # Collect emitted signal
    emitted = []

    def handle_ping(ping_obj: Ping) -> None:
        emitted.append(ping_obj)

    pinger.ping_signal.connect(handle_ping)

    # Run the thread
    pinger.start()

    # Wait until the thread is done
    qtbot.waitUntil(lambda: not pinger.isRunning(), timeout=3000)

    # Assertions
    assert len(emitted) == 1
    ping = emitted[0]
    assert isinstance(ping, Ping)
    assert ping.result == "Success"
    assert ping.ip_address == ip_address
    mock_logger.log.assert_called_once()
