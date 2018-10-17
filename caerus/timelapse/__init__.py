from picamera import PiCamera
from caerus.logger import logger
from time import sleep
from fractions import Fraction


class TimeLapse(object):
    def __init__(self):
        logger.debug("initialising TimeLapse class")


class Camera(object):
    SLEEP_INTERVAL = 2
    __RESOLUTION = (3280, 2464)

    @staticmethod
    def snapshot(file_destination):
        camera = PiCamera()
        camera.resolution = Camera.__RESOLUTION
        sleep(Camera.SLEEP_INTERVAL)
        logger.info(f"writing {file_destination}")
        camera.capture(file_destination)
        camera.close()
