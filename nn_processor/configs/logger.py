
from rich.console import Console
from rich.logging import RichHandler
from logging.handlers import RotatingFileHandler

import logging
import os

CONTAINER_ID = os.getenv("CONTAINER_ID")

console = Console(force_terminal=True)

NN_PROCESSOR_LOGS = os.getenv('NN_PROCESSOR_LOGS')
NN_PROCESSOR_DEBUG = int(os.getenv('NN_PROCESSOR_DEBUG'))
NN_PROCESSOR_LOGS_CONTAINER = os.getenv('NN_PROCESSOR_LOGS_CONTAINER')
NN_PROCESSOR_LOGS_MAXBYTES = int(os.getenv('NN_PROCESSOR_LOGS_MAXBYTES'))
NN_PROCESSOR_LOGS_BACKUPCOUNT = int(os.getenv('NN_PROCESSOR_LOGS_BACKUPCOUNT'))


class ColorfulFormatter(logging.Formatter):
    LEVEL_COLORS = {
        "DEBUG": "[green]",
        "INFO": "[cyan]",
        "WARNING": "[yellow]",
        "ERROR": "[bold red]",
        "CRITICAL": "[bold white on red]",
    }

    def format(self, record):
        level_color = self.LEVEL_COLORS.get(record.levelname, "")
        message = super().format(record)
        return f"{level_color}{message}[/]"


def setup_logging():
    file_handler = RotatingFileHandler(
        filename=f'{NN_PROCESSOR_LOGS}{NN_PROCESSOR_LOGS_CONTAINER}/nn_processor_container_id_{CONTAINER_ID}',
        maxBytes=NN_PROCESSOR_LOGS_MAXBYTES * 1024 * 1024,
        backupCount=NN_PROCESSOR_LOGS_BACKUPCOUNT
    )
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True,
        markup=True
    )

    console_handler.setFormatter(ColorfulFormatter("%(message)s"))
    if NN_PROCESSOR_DEBUG:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.WARNING

    logging.basicConfig(
        level=logging_level,
        handlers=[file_handler, console_handler]
    )

