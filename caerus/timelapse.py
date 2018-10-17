from caerus.logger import logger
from caerus.timelapse import TimeLapse, Camera
from picamera import PiCamera
from time import sleep
from datetime import datetime

logger.add_file_logger("/tmp/caerus.log")


def main():
    logger.debug("timelapse initialised")
    camera = Camera()

    for i in range(0, 50):
        timestamp = datetime.now().isoformat()
        camera.snapshot(f"/home/pi/picture_{timestamp}.jpg")
        sleep(3)


if __name__ == "__main__":
    main()
