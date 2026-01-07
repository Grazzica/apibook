import logging, json
from pythonjsonlogger import jsonlogger

def setup_logger():
    logger = logging.getLogger("api")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('app.log')
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logger()
