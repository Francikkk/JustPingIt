import re
from datetime import datetime

from JustPingIt.model.ping import Ping


def test_ping_initialization() -> None:
    result = "success"
    ip = "192.168.0.1"
    ping = Ping(result, ip)

    # Controlla che gli attributi siano correttamente assegnati
    assert ping.result == result  # noqa: S201
    assert ping.ip_address == ip  # noqa: S201

    # Controlla che il timestamp sia una stringa e corrisponda al formato:
    # "YYYY-MM-DD HH:MM:SS"
    assert isinstance(ping.timestamp, str)  # noqa: S201

    # Usa regex per verificare il formato del timestamp
    pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
    assert re.match(pattern, ping.timestamp)  # noqa: S201

    # (Opzionale) Verifica che il timestamp sia vicino al tempo corrente
    timestamp_datetime = datetime.strptime(ping.timestamp, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    diff = (now - timestamp_datetime).total_seconds()
    assert (  # noqa: S201
        diff >= 0 and diff < 5
    )  # Il test dovrebbe essere eseguito entro 5 secondi dalla creazione
