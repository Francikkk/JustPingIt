import subprocess
import sys

from PySide6.QtCore import QMutex, QThread, QWaitCondition, Signal

from .database_logger import DatabaseLogger
from .ping import Ping

# ----------------- Helper Classes -----------------


# ----------------- Core Classes -----------------


class Pinger(QThread):
    """
    Pinger is a QThread-based class that periodically pings a given IP address
    and logs the results.
    Attributes:
        ping_signal (Signal): A signal emitted with a Ping object containing
        the result of the ping operation.
    Args:
        ip_address (str): The IP address to ping.
        frequency (int): The frequency (in seconds) at which the IP address is
        pinged.
        logger (DatabaseLogger): An instance of a logger to log the ping
        results.
    Methods:
        run():
            Executes the thread's main loop, periodically pinging the IP
            address and emitting/logging the results.
        stop():
            Stops the thread's execution and wakes any waiting conditions.
        ping_host(ip_address: str) -> str:
            Pings the specified IP address and returns the result as a string
            ("Success" or "Failure").
    """

    ping_signal = Signal(Ping)

    def __init__(
        self, ip_address: str, frequency: int, logger: DatabaseLogger
    ) -> None:
        """
        Initializes a new instance of the class.

        Args:
            ip_address (str): The IP address to be monitored.
            frequency (int): The frequency (in seconds) at which the IP address
            should be pinged.
            logger (DatabaseLogger): An instance of DatabaseLogger to log the
            ping results.

        Attributes:
            ip_address (str): The IP address to be monitored.
            frequency (int): The frequency (in seconds) at which the IP address
            should be pinged.
            logger (DatabaseLogger): Logger instance for recording ping
            results.
            _is_running (bool): Indicates whether the monitoring is currently
            active.
            _mutex (QMutex): Mutex for thread synchronization.
            _wait_condition (QWaitCondition): Wait condition for thread
            control.
        """
        super().__init__()
        self.ip_address = ip_address
        self.frequency = frequency
        self.logger = logger
        self._is_running = True
        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()

    def run(self) -> None:
        """
        Executes the main loop for the pinging process.
        Continuously pings the specified IP address at a defined frequency
        while the `_is_running` flag is set to True. The results of each ping
        are logged and emitted as a signal.
        The method uses a mutex and a wait condition to control the timing
        of the loop based on the `frequency` attribute.
        Attributes:
            self.ip_address (str): The IP address to ping.
            self.frequency (int): The frequency (in seconds) at which to ping
            the IP address.
            self._is_running (bool): A flag indicating whether the loop should
            continue running.
            self._mutex (QMutex): A mutex used to synchronize access to shared
            resources.
            self._wait_condition (QWaitCondition): A condition variable used to
            manage the loop timing.
            self.logger (Logger): A logger instance for recording ping results.
            self.ping_signal (Signal): A signal emitted with the ping result.
        Raises:
            Any exceptions raised by `ping_host` or other methods will
            propagate.
        """
        while self._is_running:
            result = self.ping_host(self.ip_address)
            ping = Ping(result, self.ip_address)
            self.logger.log(ping)
            self.ping_signal.emit(ping)

            self._mutex.lock()
            self._wait_condition.wait(self._mutex, self.frequency * 1000)
            self._mutex.unlock()

    def stop(self) -> None:
        """
        Stops the execution of the current process.

        This method acquires a mutex lock to ensure thread safety, sets the
        `_is_running` flag to `False` to signal the process to stop, and
        wakes all threads waiting on the condition variable `_wait_condition`.
        Finally, it releases the mutex lock.
        """
        self._mutex.lock()
        self._is_running = False
        self._wait_condition.wakeAll()
        self._mutex.unlock()

    def ping_host(self, ip_address: str) -> str:
        """
        Pings a given IP address and returns the result as a string.
        This method uses the system's `ping` command to check the reachability
        of the specified IP address.
        It supports both Windows and non-Windows platforms.
        Args:
            ip_address (str): The IP address to ping.
        Returns:
            str: "Success" if the host is reachable, "Failure" otherwise.
        Exceptions:
            - Handles `subprocess.CalledProcessError` if the ping command
            fails.
            - Handles `subprocess.TimeoutExpired` if the ping command times
            out.
            - Handles any other unexpected exceptions and logs the error
            message.
        """
        try:
            if sys.platform.startswith("win"):
                command = ["ping", "-n", "1", ip_address]
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                output = subprocess.check_output(  # noqa: S603
                    command,
                    stderr=subprocess.STDOUT,
                    timeout=3,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                ).decode()
            else:
                command = ["ping", "-c", "1", ip_address]
                output = subprocess.check_output(  # noqa: S603
                    command, stderr=subprocess.STDOUT, timeout=3
                ).decode()

            if (
                "unreachable" in output
                or "100% packet loss" in output
                or "timed out" in output
            ):
                return "Failure"
            elif "Reply from" in output or "bytes from" in output:
                return "Success"
            else:
                return "Failure"
        except subprocess.CalledProcessError:
            return "Failure"
        except subprocess.TimeoutExpired:
            return "Failure"
        except Exception as e:
            print(f"Unexpected error during ping: {e}")
            return "Failure"
