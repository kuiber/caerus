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

    def get_camera(self):
        logger.debug("returning camera instance")
        return PiCamera(framerate=self.framerate)

    def __init__(self, resolution_scale_factor=1.0, framerate=(30, 1), iso=100):
        logger.debug("initialising Camera class")

        # self.framerate = Fraction(framerate[0], framerate[1])
        # self.framerate = Fraction(1, 6)
        # self.framerate = Fraction(60, 1)
        self.framerate = 20
        self.resolution = (int(Camera.__RESOLUTION[0] * resolution_scale_factor), int(Camera.__RESOLUTION[1] * resolution_scale_factor))
        self.iso = iso

        # create the original camera instance so we can get some other hardcoded values
        camera = self.get_camera()
        camera.resolution = self.resolution
        camera.iso = self.iso

        # now we set some permanent values for future pictures
        sleep(Camera.SLEEP_INTERVAL)
        self.shutter_speed = camera.exposure_speed
        camera.exposure_mode = 'off'
        self.awb_gains = camera.awb_gains
        camera.close()
        logger.info(f"created camera instance - resolution:{self.resolution} - framerate:{self.framerate} - iso:{self.iso} - shutterspeed:{self.shutter_speed} - awb:{self.awb_gains}")

    def snapshot(self, file_destination):
        camera = self.get_camera()
        camera.resolution = self.resolution
        camera.iso = self.iso
        camera.shutter_speed = self.shutter_speed
        # camera.shutter_speed = 6000000
        # camera.exposure_mode = 'off'
        # camera.awb_mode = 'off'
        # camera.awb_gains = self.awb_gains
        sleep(Camera.SLEEP_INTERVAL)
        logger.info(f"saving image {file_destination}")
        camera.capture(file_destination)
        camera.close()
