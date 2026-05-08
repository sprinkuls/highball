import base64
import re
import time
import uuid
import requests
import jwt
import logging

import sys
from cryptography.hazmat.primitives.asymmetric import ec
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def main():
    # TODO: put all the watching logic here
    while True:
        pass


if __name__ == '__main__':
    try:
        handler = logging.FileHandler("highball.log", mode="w", encoding="utf-8")
        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        logger.info('highball started')

        main()
    except KeyboardInterrupt:
        logger.info('highball ^Closed')
        sys.exit(0)