from picamera import PiCamera
from caerus.logger import logger
from time import sleep
from os import path, makedirs
import datetime


class TimeLapse(object):
    BASE_PROJECT_DIRECTORY = "/home/pi/timelapse"

    def __init__(self, project_name: str, interval_s: float, duration: datetime.timedelta):
        logger.debug("initialising TimeLapse class")
        self.project_name = project_name
        self.interval = interval_s
        self.duration = duration  # FIXME thread here
        self.project_directory = path.join(TimeLapse.BASE_PROJECT_DIRECTORY, self.project_name)
        if not path.exists(self.project_directory):
            logger.info(f"making project directory '{self.project_directory}'")
            makedirs(self.project_directory, exist_ok=True)

    def start(self):
        # FIXME check if file name exists - go to end of sequence - don't overwrite
        logger.info(f"starting timelapse: taking a picture every {self.interval}s for {self.duration} interval")
        end_time = datetime.datetime.now() + self.duration
        counter = 0
        while datetime.datetime.now() < end_time:
            # filename = f"image_{datetime.datetime.now().isoformat()}.jpg"
            filename = f"image_{counter:09}.jpg"
            Camera.snapshot(path.join(self.project_directory, filename))
            counter += 1
            sleep(self.interval)
        logger.info("timelapse complete")


class Camera(object):
    SLEEP_INTERVAL = 2
    __RESOLUTION = (3280, 2464)

    @staticmethod
    def snapshot(file_destination: str):
        camera = PiCamera()
        camera.resolution = Camera.__RESOLUTION
        sleep(Camera.SLEEP_INTERVAL)
        logger.info(f"writing {file_destination}")
        camera.capture(file_destination)
        camera.close()
