from datetime import datetime

class Ping:
    """
    A class to represent the result of a ping operation.

    Attributes:
        result (str): The result of the ping operation (e.g., success or failure).
        timestamp (str): The timestamp when the Ping object was created, formatted as "YYYY-MM-DD HH:MM:SS".
        ip_address (str): The IP address that was pinged.

    Methods:
        __init__(result: str, ip_address: str):
            Initializes a Ping object with the given result and IP address, and sets the timestamp to the current time.
    """
    def __init__(self, result: str, ip_address: str) -> None:
        """
        Initialize a new instance of the class.

        Args:
            result (str): The result of the operation or status.
            ip_address (str): The IP address associated with the instance.

        Attributes:
            result (str): Stores the result of the operation or status.
            timestamp (str): The timestamp when the instance is created, formatted as "YYYY-MM-DD HH:MM:SS".
            ip_address (str): Stores the IP address associated with the instance.
        """
        self.result = result
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ip_address = ip_address