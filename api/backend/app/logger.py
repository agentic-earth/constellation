# app/logger.py

import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from backend.app.config import Settings
import sys


class ConstellationLogger:
    """
    A comprehensive logging class for the Hybrid Model Application.

    This class manages logging for multiple components, handles file paths,
    and formats logs properly. It uses the Singleton pattern to ensure
    a single logging instance across the application.
    """

    _instance = None

    def __new__(cls) -> "ConstellationLogger":
        if cls._instance is None:
            cls._instance = super(ConstellationLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.config = Settings()  # Initialize configuration
        self.loggers: Dict[str, logging.Logger] = {}
        self.log_dir: Path = (
            Path(__file__).resolve().parent.parent / "logs"
        )  # Absolute path to root/logs
        self._create_log_directory()

    def _create_log_directory(self) -> None:
        """Create the log directory if it doesn't exist."""
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True, exist_ok=True)

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger for a specific component.

        Args:
            name (str): Name of the component requesting a logger.

        Returns:
            logging.Logger: Logger instance for the specified component.
        """
        if name not in self.loggers:
            self._setup_logger(name)
        return self.loggers[name]

    def _setup_logger(self, name: str) -> None:
        """
        Set up a new logger for a component and clear existing logs.

        Args:
            name (str): Name of the component.
        """
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, self.config.LOG_LEVEL.upper(), logging.INFO))

        log_file = self.log_dir / f"{name}_logs.log"

        # Clear existing logs
        with open(log_file, "w") as file:
            file.write(f"Log file initialized on {datetime.now()}\n")

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(
            getattr(logging, self.config.LOG_LEVEL.upper(), logging.INFO)
        )

        formatter = logging.Formatter(self.config.LOG_FORMAT)
        file_handler.setFormatter(formatter)

        # Prevent adding multiple handlers to the logger
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.propagate = (
                False  # Prevent log messages from being propagated to the root logger
            )

        self.loggers[name] = logger

    def log(self, name: str, level: str, message: str, **kwargs: Any) -> None:
        """
        Log a message for a specific component.

        Args:
            name (str): Name of the component logging the message.
            level (str): Log level ('debug', 'info', 'warning', 'error', 'critical').
            message (str): The log message.
            **kwargs: Additional key-value pairs to be included in the log message.
        """
        logger = self.get_logger(name)
        log_method = getattr(logger, level.lower(), None)

        if not log_method:
            raise ValueError(f"Invalid log level: {level}")

        if kwargs:
            sensitive_fields = ["password", "password_hash", "access_token", "token"]
            sanitized_kwargs = {
                k: ("***" if k in sensitive_fields else v) for k, v in kwargs.items()
            }
            formatted_kwargs = " - ".join(
                f"{k}={v}" for k, v in sanitized_kwargs.items()
            )
            message = f"{message} - {formatted_kwargs}"

        log_method(message)

    def get_recent_logs(self, name: str, lines: int = 100) -> str:
        """
        Retrieve the most recent log entries for a component.

        Args:
            name (str): Name of the component.
            lines (int): Number of recent log lines to retrieve. Defaults to 100.

        Returns:
            str: The most recent log entries.
        """
        log_file = self.log_dir / f"{name}_logs.log"
        if not log_file.exists():
            return f"No log file found for {name}"

        with open(log_file, "r") as file:
            return "".join(file.readlines()[-lines:])
