from picamera import PiCamera
from caerus.logger import logger
from time import sleep
from os import path, makedirs, listdir
import datetime
import re


class TimeLapse(object):
    BASE_PROJECT_DIRECTORY = "/home/pi/timelapse"

    @staticmethod
    def _get_max_sequence(directory):
        image_name_regex = re.compile(r"image_(\d+).jpg")
        dir_list = sorted(listdir(directory))
        if len(dir_list) == 0:
            logger.debug("no images in directory - starting at 0")
            return 0

        for i in reversed(dir_list):
            match = image_name_regex.search(i)
            if match:
                last_image_id = match.groups()[0]
                last_image_id_plus_one = int(last_image_id) + 1
                logger.debug(f"found previous images in {directory} - image counter starting at {last_image_id_plus_one}")
                return int(last_image_id) + 1

        logger.error(f"unable to extract last_image_id from {directory} - returning 0 - this may cause file overwrites")
        return 0

    def __init__(self, project_name: str, interval_s: float, duration: datetime.timedelta):
        logger.debug("initialising TimeLapse class")
        self.project_name = project_name
        self.interval = interval_s
        self.duration = duration  # FIXME thread here
        self.project_directory = path.join(TimeLapse.BASE_PROJECT_DIRECTORY, self.project_name)
        if not path.exists(self.project_directory):
            logger.info(f"making project directory '{self.project_directory}'")
            makedirs(self.project_directory, exist_ok=True)
        else:
            logger.info(f"project '{self.project_name}' already exists")

    def start(self):
        logger.info(f"starting timelapse: taking a picture every {self.interval}s for {self.duration} interval")
        end_time = datetime.datetime.now() + self.duration
        counter = TimeLapse._get_max_sequence(self.project_directory)
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
