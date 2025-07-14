import contextlib
import gc
import os
import tempfile
from collections.abc import Iterator
from datetime import datetime, timedelta
from typing import cast

import pytest

from JustPingIt.model.database_logger import DatabaseLogger
from JustPingIt.model.ping import Ping


@pytest.fixture
def temp_db_path() -> Iterator[str]:
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        db_path = tf.name

    yield db_path

    # Explicitly run garbage collection and ensure file is not locked
    gc.collect()
    try:
        os.remove(db_path)
    except PermissionError as e:
        print(f"Warning: could not delete temp db file: {e}")


@pytest.fixture
def db_logger(temp_db_path: str) -> DatabaseLogger:
    return DatabaseLogger(temp_db_path)


@pytest.fixture
def sample_ping() -> Ping:
    return Ping(
        result="Success",
        ip_address="192.168.0.1",
    )


def test_create_table_and_log_insert(
    db_logger: DatabaseLogger, sample_ping: Ping
) -> None:
    # Log a sample ping
    db_logger.log(sample_ping)

    # Fetch logs
    logs = db_logger.fetch_logs()
    assert len(logs) == 1
    log = logs[0]
    assert log[1] == sample_ping.result
    assert log[2] == sample_ping.timestamp
    assert log[3] == sample_ping.ip_address


def test_fetch_logs_filters(db_logger: DatabaseLogger) -> None:
    now = datetime.now()

    entries = [
        Ping(
            result="Success",
            ip_address="10.0.0.1",
        ),
        Ping(
            result="Failure",
            ip_address="10.0.0.2",
        ),
        Ping(
            result="Success",
            ip_address="10.0.0.3",
        ),
    ]

    for ping in entries:
        db_logger.log(ping)

    # Filter by IP
    ip_filtered = db_logger.fetch_logs(ip_filter="10.0.0.2")
    assert len(ip_filtered) == 1
    assert ip_filtered[0][3] == "10.0.0.2"

    # Filter by result
    result_filtered = db_logger.fetch_logs(result_filter="Success")
    assert len(result_filtered) == 2

    # Filter by date range
    from_date = now - timedelta(days=1)
    to_date = now
    date_filtered = db_logger.fetch_logs(from_date=from_date, to_date=to_date)
    assert len(date_filtered) == 3  # Last three entries


def test_delete_logs_by_ids(
    db_logger: DatabaseLogger, sample_ping: Ping
) -> None:
    # Insert multiple entries
    for _ in range(3):
        db_logger.log(sample_ping)

    logs = db_logger.fetch_logs()
    ids_to_delete = [log[0] for log in logs[:2]]  # Delete first 2 logs

    db_logger.delete_logs_by_ids(ids_to_delete)
    remaining_logs = db_logger.fetch_logs()

    assert len(remaining_logs) == 1
    assert remaining_logs[0][0] not in ids_to_delete


def test_fetch_logs_empty(db_logger: DatabaseLogger) -> None:
    logs = db_logger.fetch_logs()
    assert logs == []


def test_log_invalid_data_handling(db_logger: DatabaseLogger) -> None:
    # You can only test exception handling if Ping has required fields missing
    class BrokenPing:
        def __init__(self) -> None:
            self.result = None
            self.timestamp = None
            self.ip_address = None

    broken_ping = BrokenPing()
    with contextlib.redirect_stdout(None):
        db_logger.log(cast(Ping, broken_ping))

    logs = db_logger.fetch_logs()
    assert logs == []
    logs = db_logger.fetch_logs()
    assert logs == []  # Shouldn't log invalid entries
