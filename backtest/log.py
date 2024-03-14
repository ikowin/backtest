import logging
import os

__all__ = (
    'create_log'
)

SEEX_LOG_LEVEL = "SEEX_LOG_LEVEL"

# CRITICAL = 50
# FATAL = CRITICAL
# ERROR = 40
# WARNING = 30
# WARN = WARNING
# INFO = 20
# DEBUG = 10
# NOTSET = 0
log_level = os.getenv(SEEX_LOG_LEVEL, "DEBUG")


def create_log(name: str = "", level=log_level):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.hasHandlers():
        h = logging.StreamHandler()
        h.setLevel(level)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)-5s [%(filename)11s:%(lineno)3d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        h.setFormatter(formatter)
        logger.addHandler(h)

    return logger


if __name__ == "__main__":
    from time import sleep

    log = create_log(__name__)

    log.info("Server starting...")
    sleep(1)

    log.info("GET /index.html 200 1298")
    log.warning("GET /favicon.ico 404 242")
    sleep(1)

    log.debug(
        "JSONRPC request\n--> %r\n<-- %r",
        {
            "version": "1.1",
            "method": "confirmFruitPurchase",
            "params": [["apple", "orange", "mangoes", "pomelo"], 1.123],
            "id": "194521489",
        },
        {"version": "1.1", "result": True, "error": None, "id": "194521489"},
    )
    log.debug(
        "Loading configuration file /path/to/my.conf"
    )
    log.error("Unable to find 'pomelo' in database!")
    log.info("POST /jsonrpc/ 200 65532")
    log.info("POST /admin/ 401 42234")
    log.warning("password was rejected for admin site.")

    def divide():
        number = 1
        divisor = 0
        foos = ["foo"] * 100
        log.debug("in divide")
        try:
            number / divisor
        except Exception as e:
            log.exception("An error of some kind occurred!")

    divide()
    sleep(1)
    log.critical("Out of memory!")
    log.info("Server exited with code=-1")
    log.info("[bold]EXITING...[/bold]", extra=dict(markup=True))
