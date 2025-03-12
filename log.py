import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler("app.log")
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)